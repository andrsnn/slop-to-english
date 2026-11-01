"""mine_transcripts: find places in Claude Code transcripts where the owner complained about copy, or asked GLM to fix it.

  python -I tools/mine_transcripts.py [--root ~/.claude/projects] [--out hits.jsonl]

For each user message that matches a complaint pattern ("makes no sense", "nobody talks like that", "say it out loud",
"slop", "convoluted", "GLM" ...), writes one JSON line with the transcript path, the user's message and the last
assistant text before it (the copy being complained about). Also writes lines where an assistant tool call sent copy
to a GLM model. The output is raw material: a person picks the before/after pairs for tests/fixtures/sayable.jsonl by
hand. Lines that look like they hold a secret (key=, token, password, sk-...) are dropped.
"""
import argparse, json, re, sys
from pathlib import Path

COMPLAINT = re.compile(
    r"makes? no sense|doesn'?t make sense|does not make sense|nobody (talks|says|speaks)|no one (talks|says)|"
    r"(say|read|said) (it|this|that|them|these) (out )?loud|out loud|\bslop\b|sloppy|convoluted|\bglm\b|"
    r"human would never|would never say|sounds like (an? )?(ai|llm|robot)|what does (that|this) (even )?mean|"
    r"word salad|gibberish|\bawkward\b|unreadable|not english|plain english|slop-to-english", re.I)
SECRET = re.compile(r"((api[_-]?key|token|password|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}|bearer\s+[A-Za-z0-9_\-.]{20,}|"
                    r"\b(sk|hf|rpa|ghp|gho|xox[bp])[-_][A-Za-z0-9_\-]{16,})", re.I)


def text_of(content) -> str:
    if isinstance(content, str): return content
    if isinstance(content, list):
        return '\n'.join(b.get('text', '') for b in content if isinstance(b, dict) and b.get('type') == 'text')
    return ''


def tool_inputs(content) -> list[str]:
    if not isinstance(content, list): return []
    return [json.dumps(b.get('input', {}), ensure_ascii=False) for b in content
            if isinstance(b, dict) and b.get('type') == 'tool_use']


def scan(path: Path):
    last_assistant = ''
    try:
        lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
    except OSError:
        return
    for raw in lines:
        try:
            ev = json.loads(raw)
        except ValueError:
            continue
        msg = ev.get('message') or {}
        role, content = msg.get('role'), msg.get('content')
        if ev.get('type') == 'assistant' and role == 'assistant':
            t = text_of(content)
            if t.strip(): last_assistant = t
            for inp in tool_inputs(content):
                if re.search(r'glm', inp, re.I) and len(inp) > 80:
                    yield {'kind': 'glm_call', 'file': str(path), 'input': inp[:4000]}
        elif ev.get('type') == 'user' and role == 'user' and not ev.get('isMeta'):
            t = text_of(content)
            if not t or t.startswith('<') and 'command-name' in t[:200]: continue
            if len(t) < 4000 and COMPLAINT.search(t):
                yield {'kind': 'complaint', 'file': str(path), 'user': t, 'before': last_assistant[-3000:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, default=Path.home() / '.claude' / 'projects')
    ap.add_argument('--out', type=Path, default=Path('hits.jsonl'))
    a = ap.parse_args()
    n = 0
    with a.out.open('w', encoding='utf-8') as f:
        for p in sorted(a.root.glob('*/*.jsonl')):
            for hit in scan(p):
                blob = json.dumps(hit, ensure_ascii=False)
                if SECRET.search(hit.get('user', '') + hit.get('input', '')): continue
                f.write(blob + '\n'); n += 1
    print(n, 'hits ->', a.out, file=sys.stderr)


if __name__ == '__main__':
    main()
