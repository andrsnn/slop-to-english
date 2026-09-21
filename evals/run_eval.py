#!/usr/bin/env python3
"""Test how well a model rewrites LLM-speak into plain spoken English.

Each test case is a piece of LLM-speak with facts hidden in it. The script sends the case to a
model, then checks the model's rewrite: are the facts still there, are the banned phrases gone,
is it short enough, did it invent any numbers. Standard library only.

Pick where the rewrites come from. The scoring is identical for all three.

  # 1. A server with an OpenAI-style API (llama.cpp, LM Studio, vLLM, Ollama /v1, OpenAI)
  python run_eval.py --openai-url http://127.0.0.1:8080/v1 --model qwen --skill

  # 2. A command that reads the prompt on stdin and prints the rewrite
  python run_eval.py --cmd "claude -p" --skill
  python run_eval.py --cmd "ollama run llama3.1" --skill

  # 3. A file of rewrites you collected by hand from any chat window
  python run_eval.py --write-prompts prompts.jsonl --skill   # paste each prompt into the chat
  python run_eval.py --outputs outputs.jsonl                 # lines: {"id": "c001", "output": "..."}

--skill puts the SKILL.md text in front of each case, which tests the skill.
Without it the model gets a one-line instruction, which gives you the baseline to compare against.
"""
import argparse, difflib, json, os, re, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CASES = os.path.join(HERE, "cases.jsonl")
SKILL_MD = os.path.join(HERE, "..", "SKILL.md")

BASELINE = "Rewrite the following text in plain spoken English. Keep every number and technical term. Reply with the rewrite only."
SKILL_WRAP = (
    "Follow these instructions exactly.\n\n{skill}\n\n---\n"
    "Apply the skill to the text below. Reply with the rewrite only, no commentary.\n\nTEXT:\n{text}"
)
BASE_WRAP = BASELINE + "\n\nTEXT:\n{text}"

# Tells that fail any rewrite, regardless of case. Lowercase regexes.
GLOBAL_BANNED = [
    r"\bdelv(e|es|ed|ing)\b", r"\btapestr(y|ies)\b", r"\btestament to\b", r"\bin the realm of\b",
    r"\bgame[- ]?chang(er|ing)\b", r"\bit'?s worth noting\b", r"\bworth stating\b", r"\blet'?s dive\b",
    r"\bnot just\b.{0,60}\b(but|it'?s|it is)\b", r"\bit'?s not\b.{0,60}\bit'?s\b", r"\bisn'?t (just )?(about )?.{0,50}, it'?s\b",
    r"\bnot (merely|only|simply)\b", r"\bat the end of the day\b", r"\bunder the hood\b", r"\bseamless(ly)?\b",
    r"\bunlock(s|ed|ing)?\b", r"\belevat(e|es|ed|ing)\b", r"\bcutting[- ]edge\b", r"\bnavigat(e|es|ing) the\b",
    r"\bever[- ]evolving\b", r"\bfast[- ]paced world\b", r"\bload[- ]bearing\b", r"\bthe real tension\b",
    r"\bcarr(y|ies) the argument\b", r"\bhere'?s the (honest )?truth\b", r"\bgreat question\b",
]
SYMBOLS = ["→", "←", "⇒", "✓", "✗", "✔", "✘", "~", "★", "✦"]


def nums(s):
    s = re.sub(r"(?<=\d),(?=\d)", "", s)
    return set(re.findall(r"\d+(?:\.\d+)?", s))


def score(case, out):
    out = (out or "").strip()
    low = out.lower()
    checks = {}
    facts = case["facts"]
    kept = [f for f in facts if f.lower() in low]
    checks["facts"] = len(kept) == len(facts)
    checks["banned"] = not any(b.lower() in low for b in case["banned"])
    checks["global_banned"] = not any(re.search(p, low) for p in GLOBAL_BANNED)
    checks["length"] = 0 < len(out) <= case["max_chars"]
    # numbers in the output must all come from the input (no inventing)
    checks["no_new_numbers"] = nums(out) <= nums(case["input"])
    checks["dashes"] = out.count("—") + out.count(" - ") <= 1
    checks["symbols"] = not any(s in out and s not in "".join(facts) for s in SYMBOLS)
    if case["category"] == "control-plain":
        # already plain: must stay close to the input
        sim = difflib.SequenceMatcher(None, case["input"].lower(), low).ratio()
        checks["unchanged"] = sim >= 0.8
        checks["length"] = True
    fail = [k for k, v in checks.items() if not v]
    return {
        "id": case["id"], "category": case["category"], "weight": case.get("weight", 1),
        "pass": not fail, "failed": fail,
        "facts_kept": f"{len(kept)}/{len(facts)}", "chars": len(out),
    }


def load_cases(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def make_prompt(case, skill_text):
    if skill_text:
        return SKILL_WRAP.format(skill=skill_text, text=case["input"])
    return BASE_WRAP.format(text=case["input"])


def ask_openai(url, model, key, prompt):
    body = json.dumps({"model": model, "temperature": 0,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(url.rstrip("/") + "/chat/completions", body,
                                 {"Content-Type": "application/json", "Authorization": f"Bearer {key or 'none'}"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def ask_cmd(cmd, prompt):
    p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, shell=True, encoding="utf-8", timeout=600)
    return p.stdout


def strip_think(s):
    return re.sub(r"<think>[\s\S]*?</think>", "", s or "").strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cases", default=DEFAULT_CASES)
    ap.add_argument("--skill", action="store_true", help="prepend SKILL.md to every prompt")
    ap.add_argument("--openai-url"), ap.add_argument("--model", default="default")
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))
    ap.add_argument("--cmd", help="shell command: prompt on stdin, rewrite on stdout")
    ap.add_argument("--outputs", help="score a file of rewrites (outputs.jsonl)")
    ap.add_argument("--write-prompts", help="write prompts.jsonl for manual use and exit")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--out", default="results.json")
    a = ap.parse_args()

    cases = load_cases(a.cases)[: a.limit]
    skill_text = open(SKILL_MD, encoding="utf-8").read() if a.skill else ""

    if a.write_prompts:
        with open(a.write_prompts, "w", encoding="utf-8") as f:
            for c in cases:
                f.write(json.dumps({"id": c["id"], "prompt": make_prompt(c, skill_text)}, ensure_ascii=False) + "\n")
        print(f"wrote {len(cases)} prompts to {a.write_prompts}")
        return

    rewrites = {}
    if a.outputs:
        for l in open(a.outputs, encoding="utf-8"):
            if l.strip():
                o = json.loads(l)
                rewrites[o["id"]] = o["output"]
    elif a.openai_url or a.cmd:
        for i, c in enumerate(cases, 1):
            prompt = make_prompt(c, skill_text)
            try:
                raw = ask_openai(a.openai_url, a.model, a.api_key, prompt) if a.openai_url else ask_cmd(a.cmd, prompt)
            except Exception as e:  # keep going, count as a failure
                raw = ""
                print(f"  {c['id']} error: {e}", file=sys.stderr)
            rewrites[c["id"]] = strip_think(raw)
            print(f"\r{i}/{len(cases)}", end="", file=sys.stderr)
        print(file=sys.stderr)
    else:
        ap.error("give one of --openai-url, --cmd, --outputs, --write-prompts")

    rows = [score(c, rewrites.get(c["id"], "")) for c in cases]
    passed = sum(r["pass"] for r in rows)
    wtot = sum(r["weight"] for r in rows)
    wpass = sum(r["weight"] for r in rows if r["pass"])
    wpct = 100 * wpass // max(1, wtot)
    print(f"\nWEIGHTED SCORE {wpct}%  (opaque phrases count 3x)")
    print(f"PASS {passed}/{len(rows)} cases ({100 * passed // max(1, len(rows))}%)\n")
    by = {}
    for r in rows:
        by.setdefault(r["category"], []).append(r["pass"])
    for cat, v in sorted(by.items(), key=lambda kv: (not kv[0].startswith("opaque-"), kv[0])):
        print(f"  {cat:32} {sum(v)}/{len(v)}")
    fails = {}
    for r in rows:
        for k in r["failed"]:
            fails[k] = fails.get(k, 0) + 1
    if fails:
        print("\nfailed checks:", ", ".join(f"{k}={v}" for k, v in sorted(fails.items(), key=lambda x: -x[1])))
    json.dump({"weighted_pct": wpct, "passed": passed, "total": len(rows), "rows": rows,
               "rewrites": rewrites}, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"\nwrote {a.out}")
    sys.exit(0 if passed == len(rows) else 1)


if __name__ == "__main__":
    main()
