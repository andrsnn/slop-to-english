"""deslop: rewrite the player-facing sentences in a code base with this skill's rules, through an Ollama model
(default glm-5.3:cloud, which runs on Ollama's servers, not this machine).

  python deslop.py scan <repo> [--glob 'src/**/*.ts']         list the candidate lines (deslop-candidates.json)
  python deslop.py rewrite <repo> [--model glm-5.3:cloud]     ask the model, batch by batch (deslop-proposals.json, resumable)
  python deslop.py apply <repo>                               write the accepted rewrites back into the files

A candidate is a single-quoted string literal of 5+ words that reads as a sentence (ends in . ! or ?, or holds one),
with no code in it (no ${ }, braces, = ; < >, URLs or paths). Names, ids and short labels are left alone. The model gets
SKILL.md's rules and must keep every number, name and game term; a rewrite that drops a number or grows past 1.6x the
original is rejected and the line keeps its old text. Files are rewritten in place only by `apply`.
"""
import argparse, glob, json, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
BAD = re.compile(r"\$\{|[{}<>=;]|https?:|\\n|\w/\w+/|\.(ts|png|json|js|mjs)\b")
NUM = re.compile(r"\d+(?:\.\d+)?")


def literals(text: str):
    """Every single-quoted literal: (start, end, raw inner text). One linear pass; skips // comments."""
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == '/' and i + 1 < n and text[i + 1] == '/':
            j = text.find('\n', i); i = n if j < 0 else j; continue
        if c == "'":
            j = i + 1
            while j < n and text[j] not in "'\n":
                j += 2 if text[j] == '\\' else 1
            if j < n and text[j] == "'":
                yield i + 1, j, text[i + 1:j]
            i = j + 1; continue
        i += 1


def is_sentence(s: str) -> bool:
    return len(s.split()) >= 5 and not BAD.search(s) and bool(re.search(r"[.!?]$|[.!?] [A-Z]", s)) and s[:1].isupper()


def scan(repo: Path, pattern: str) -> list[dict]:
    out = []
    for f in sorted(glob.glob(str(repo / pattern), recursive=True)):
        if '.test.' in f or 'fixtures' in f: continue
        t = Path(f).read_text(encoding='utf-8')
        for a, b, raw in literals(t):
            s = raw.replace("\\'", "'")
            if is_sentence(s): out.append({'file': str(Path(f).relative_to(repo)).replace('\\', '/'), 'text': s})
    seen, uniq = set(), []
    for c in out:  # the same sentence in two places is asked about once
        if c['text'] not in seen: seen.add(c['text']); uniq.append(c)
    return uniq


def rules() -> str:
    skill = (HERE / 'SKILL.md').read_text(encoding='utf-8')
    return ("You rewrite text from a video game so a player can read each line aloud and know exactly what it means. "
            "Follow these rules:\n\n" + skill + "\n\nGame-specific rules: keep every number, unit, item name, place name, "
            "key name and game term exactly. Keep the second person ('you') where the line uses it. Keep each line about "
            "the same length or shorter; never add new facts. If a line is already plain and literal, return it unchanged. "
            "Use straight quotes and apostrophes only.\n\nYou get a JSON array of lines. Reply with ONLY a JSON array of "
            "the same length, one rewritten line per input line, in order.")


def ask(model: str, system: str, lines: list[str], host: str) -> list[str]:
    body = json.dumps({'model': model, 'stream': False, 'format': 'json', 'options': {'temperature': .2},
                       'messages': [{'role': 'system', 'content': system},
                                    {'role': 'user', 'content': json.dumps(lines, ensure_ascii=False)}]}).encode()
    for attempt in range(4):
        try:
            req = urllib.request.Request(host + '/api/chat', body, {'Content-Type': 'application/json'})
            content = json.loads(urllib.request.urlopen(req, timeout=600).read())['message']['content']
            got = json.loads(content)
            if isinstance(got, dict): got = next((v for v in got.values() if isinstance(v, list)), [])
            if isinstance(got, list) and len(got) == len(lines) and all(isinstance(x, str) for x in got): return got
        except Exception as e:
            print('  retry', attempt + 1, str(e)[:120], flush=True)
        time.sleep(3 * (attempt + 1))
    return list(lines)  # give up on this batch: keep the originals


def accept(old: str, new: str) -> str:
    new = new.strip().replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('—', ', ')
    if not new or '\n' in new or len(new) > 1.6 * len(old) + 10: return old
    if sorted(NUM.findall(old)) != sorted(NUM.findall(new)): return old  # a number changed or went missing
    return new


def rewrite(repo: Path, model: str, host: str, size: int, workers: int):
    cand = json.loads((repo / 'deslop-candidates.json').read_text(encoding='utf-8'))
    pfile = repo / 'deslop-proposals.json'
    done = json.loads(pfile.read_text(encoding='utf-8')) if pfile.exists() else {}
    todo = [c['text'] for c in cand if c['text'] not in done]
    batches = [todo[i:i + size] for i in range(0, len(todo), size)]; system = rules()
    print(f'{len(cand)} lines, {len(done)} done, {len(batches)} batches to ask', flush=True)
    def run(batch):
        return batch, ask(model, system, batch, host)
    with ThreadPoolExecutor(workers) as ex:
        for k, (batch, got) in enumerate(ex.map(run, batches)):
            for old, new in zip(batch, got): done[old] = accept(old, new)
            pfile.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding='utf-8')
            print(f'batch {k + 1}/{len(batches)}', flush=True)


def apply(repo: Path) -> int:
    props = json.loads((repo / 'deslop-proposals.json').read_text(encoding='utf-8'))
    changed = {o: n for o, n in props.items() if n != o}; files = {c['file'] for c in json.loads((repo / 'deslop-candidates.json').read_text(encoding='utf-8'))}
    count = 0
    for f in sorted(files):
        p = repo / f; t = p.read_text(encoding='utf-8'); parts, last = [], 0
        for a, b, raw in literals(t):
            s = raw.replace("\\'", "'")
            if s in changed:
                parts.append(t[last:a]); parts.append(changed[s].replace("\\", "\\\\").replace("'", "\\'")); last = b; count += 1
        if parts: parts.append(t[last:]); p.write_text(''.join(parts), encoding='utf-8')
    return count


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['scan', 'rewrite', 'apply']); ap.add_argument('repo', type=Path)
    ap.add_argument('--glob', default='src/**/*.ts'); ap.add_argument('--model', default='glm-5.3:cloud')
    ap.add_argument('--host', default='http://127.0.0.1:11434'); ap.add_argument('--batch', type=int, default=20); ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()
    if a.cmd == 'scan':
        c = scan(a.repo, a.glob); (a.repo / 'deslop-candidates.json').write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding='utf-8')
        print(len(c), 'candidate lines in', len({x['file'] for x in c}), 'files')
    elif a.cmd == 'rewrite': rewrite(a.repo, a.model, a.host, a.batch, a.workers)
    else: print(apply(a.repo), 'literals rewritten')
