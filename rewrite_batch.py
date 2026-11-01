#!/usr/bin/env python3
"""Rewrite a batch of strings with SKILL.md and check each rewrite.

Input is a JSON list. Each item is a string, or an object {"id", "text", "context"}.
Output is a JSON list of {"id", "before", "after", "changed", "ok", "problems"}.
"after" is the model's rewrite. "ok" is false when a check failed; the caller should
then keep "before". Standard library only.

  python rewrite_batch.py strings.json out.json --openai-url http://localhost:11434/v1 --model glm-5.3:cloud

Checks on every rewrite:
  tokens    the protected tokens (${...}, {0}, {{0}}, %s, HTML tags, entities, \\ escapes) are the
            same, in the same order
  length    not longer than the input (--max-growth allows some extra characters)
  numbers   no number that was not in the input
  terms     no new capitalised word or ALL-CAPS word that was not in the input
  banned    none of the global banned phrases from evals/run_eval.py

Requests go out in batches (--batch-size items per request), with at most --workers in flight.
Finished batches are cached in <out>.cache.jsonl, so a rerun only asks for what is missing.
"""
import argparse, hashlib, json, os, re, sys, threading
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "evals"))
from run_eval import GLOBAL_BANNED, ask_openai, nums, strip_think  # noqa: E402

SKILL_MD = os.path.join(HERE, "SKILL.md")

BATCH_RULES = """
---
You are rewriting short strings from software (UI labels, buttons, hints, notices, descriptions,
dialogue). Apply the skill above to each string on its own.

Rules for this batch:
- Most strings are already plain. If a string passes the test, return it unchanged, character for character.
- Never make a string longer. Labels and buttons stay labels and buttons: keep their case style
  (ALL CAPS stays ALL CAPS, Title Case stays Title Case) and do not turn a label into a sentence.
- Keep every fact: numbers, names, keys and button letters.
- Copy every protected token exactly and in the same order: ${...}, {0}, {{0}}, %s, HTML tags
  like <b> and </b>, entities like &amp; and escapes like \\n or \\u00b7.
- Do not add new names or terms. Do not translate.
- "context" says where the string comes from. Use it only to understand the string.

The input is a JSON array of objects {"i": number, "text": string, "context": string}.
Reply with a JSON array of strings only, one per input item, in the same order, with no commentary.
"""

TOKEN_RE = re.compile(
    r"\$\{[^}]*\}|\{\{[^}]*\}\}|\{[A-Za-z0-9_]+\}|%[sdif]|<[^>]*>|&[A-Za-z#0-9]+;|\\u[0-9a-fA-F]{4}|\\u\{[0-9a-fA-F]+\}|\\x[0-9a-fA-F]{2}|\\.")


def tokens(s):
    return TOKEN_RE.findall(s or "")


def _terms(s):
    """Capitalised words that are not the first word of a sentence, plus ALL-CAPS words."""
    s = TOKEN_RE.sub(" ", s or "")
    out = set()
    for m in re.finditer(r"[A-Za-z][A-Za-z'’-]*", s):
        w = m.group(0)
        before = s[: m.start()].rstrip()
        sentence_start = not before or before[-1] in ".!?:;·|/—-(\"'"
        if w.isupper() and len(w) > 1:
            out.add(w)
        elif w[0].isupper() and not sentence_start:
            out.add(w)
    return out


def check(before, after, max_growth=0):
    """Return the list of failed checks for one rewrite ([] means it passes)."""
    problems = []
    if not after or not after.strip():
        return ["empty"]
    if tokens(before) != tokens(after):
        problems.append("tokens")
    if len(after) > len(before) + max_growth:
        problems.append("length")
    if not nums(TOKEN_RE.sub(" ", after)) <= nums(TOKEN_RE.sub(" ", before)):
        problems.append("numbers")
    words_before = {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'’-]*", before)}
    new_terms = [t for t in _terms(after) if t.lower() not in words_before]
    if new_terms:
        problems.append("terms:" + ",".join(sorted(new_terms)))
    low_b, low_a = before.lower(), after.lower()
    if any(re.search(p, low_a) and not re.search(p, low_b) for p in GLOBAL_BANNED):
        problems.append("banned")
    return problems


def parse_reply(raw, n):
    """Pull a JSON array of n strings out of a model reply. Returns None if it can't."""
    raw = strip_think(raw)
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    start, end = raw.find("["), raw.rfind("]")
    if start < 0 or end < start:
        return None
    try:
        arr = json.loads(raw[start: end + 1])
    except ValueError:
        return None
    if not isinstance(arr, list) or len(arr) != n:
        return None
    out = []
    for x in arr:
        if isinstance(x, dict):
            x = x.get("text", x.get("rewrite"))
        if not isinstance(x, str):
            return None
        out.append(x)
    return out


def normalise(items):
    out = []
    for i, it in enumerate(items):
        if isinstance(it, str):
            it = {"text": it}
        out.append({"id": it.get("id", i), "text": it["text"], "context": it.get("context", "")})
    return out


def batch_key(batch, model):
    h = hashlib.sha256(model.encode())
    for it in batch:
        h.update(b"\0" + it["text"].encode() + b"\1" + it["context"].encode())
    return h.hexdigest()[:24]


def rewrite_all(items, ask, system, batch_size=20, workers=3, cache_path=None, model="", log=None):
    """ask(system, user) -> raw reply. Returns {id: after} for every item."""
    items = normalise(items)
    batches = [items[i: i + batch_size] for i in range(0, len(items), batch_size)]
    cache, lock = {}, threading.Lock()
    if cache_path and os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    row = json.loads(line)
                    cache[row["key"]] = row["out"]

    def run(batch):
        key = batch_key(batch, model)
        if key in cache:
            return batch, cache[key]
        user = json.dumps([{"i": k, "text": it["text"], "context": it["context"]} for k, it in enumerate(batch)],
                          ensure_ascii=False)
        out = None
        for _ in range(2):
            try:
                out = parse_reply(ask(system, user), len(batch))
            except Exception as e:  # network or server error: retry, then fall back
                if log:
                    log(f"batch error: {e}")
            if out is not None:
                break
        if out is None and len(batch) > 1:  # fall back to one item per request
            out = []
            for it in batch:
                one = json.dumps([{"i": 0, "text": it["text"], "context": it["context"]}], ensure_ascii=False)
                try:
                    r = parse_reply(ask(system, one), 1)
                except Exception:
                    r = None
                out.append(r[0] if r else it["text"])
        elif out is None:
            out = [batch[0]["text"]]
        if cache_path:
            with lock, open(cache_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"key": key, "out": out}, ensure_ascii=False) + "\n")
        return batch, out

    result, done = {}, 0
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for batch, out in pool.map(run, batches):
            for it, after in zip(batch, out):
                result[it["id"]] = after
            done += 1
            if log:
                log(f"{done}/{len(batches)} batches")
    return result


def build_rows(items, rewrites, max_growth=0):
    rows = []
    for it in normalise(items):
        after = rewrites.get(it["id"], it["text"])
        problems = [] if after == it["text"] else check(it["text"], after, max_growth)
        rows.append({"id": it["id"], "before": it["text"], "after": after, "context": it["context"],
                     "changed": after != it["text"], "ok": not problems, "problems": problems})
    return rows


def openai_asker(url, model, key, temperature=0.0):
    import urllib.request

    def ask(system, user):
        body = json.dumps({"model": model, "temperature": temperature,
                           "messages": [{"role": "system", "content": system},
                                        {"role": "user", "content": user}]}).encode()
        req = urllib.request.Request(url.rstrip("/") + "/chat/completions", body,
                                     {"Content-Type": "application/json", "Authorization": f"Bearer {key or 'none'}"})
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.load(r)["choices"][0]["message"]["content"]
    return ask


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input"), ap.add_argument("output")
    ap.add_argument("--openai-url", required=True), ap.add_argument("--model", default="default")
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))
    ap.add_argument("--batch-size", type=int, default=20)
    ap.add_argument("--workers", type=int, default=3, help="requests in flight at once")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-growth", type=int, default=0, help="extra characters a rewrite may add")
    ap.add_argument("--rules", help="file with extra instructions appended to the system prompt")
    a = ap.parse_args()

    items = json.load(open(a.input, encoding="utf-8"))
    system = open(SKILL_MD, encoding="utf-8").read() + BATCH_RULES
    if a.rules:
        system += "\n" + open(a.rules, encoding="utf-8").read()
    ask = openai_asker(a.openai_url, a.model, a.api_key, a.temperature)
    rewrites = rewrite_all(items, ask, system, a.batch_size, a.workers, a.output + ".cache.jsonl", a.model,
                           log=lambda m: print("\r" + m, end="", file=sys.stderr))
    print(file=sys.stderr)
    rows = build_rows(items, rewrites, a.max_growth)
    json.dump(rows, open(a.output, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    changed = sum(r["changed"] for r in rows)
    bad = sum(r["changed"] and not r["ok"] for r in rows)
    print(f"{len(rows)} strings, {changed} rewritten, {bad} failed a check; wrote {a.output}")


if __name__ == "__main__":
    main()
