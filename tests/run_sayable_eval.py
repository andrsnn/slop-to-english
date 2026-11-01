"""Run the GLM pass (tools/sayable.py) over the fixtures and write a results table.

The real failures are private: private/sayable.jsonl (gitignored). Without it, the eval runs
over the made-up examples in tests/fixtures/sayable.example.jsonl. Results always go to private/.

  python -I tests/run_sayable_eval.py [--model glm-5.3:cloud] [--no-think]

Each fixture is a line that failed the out-loud test, with the fix that was used. The eval asks:
  1. Does the GLM pass flag the bad line ("before")?            (should be yes)
  2. Does it leave the known-good fix ("after") alone?          (should mostly be yes)
  3. How long is its rewrite compared to the bad line and to the known fix?
The raw answers go to private/results-sayable.json, and a table goes to private/RESULTS.md for a person to read.
"""
import argparse, json, sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIVATE = HERE.parent / 'private'
REAL = PRIVATE / 'sayable.jsonl'
NOTES = '<!-- notes: kept on re-run -->'
sys.path.insert(0, str(HERE.parent / 'tools'))
import sayable  # noqa: E402


def load(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding='utf-8').splitlines() if l.strip()]


def cell(s: str) -> str:
    return s.replace('|', '\\|').replace('\n', ' ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default=sayable.DEFAULT_MODEL); ap.add_argument('--host', default=sayable.DEFAULT_HOST)
    ap.add_argument('--no-think', action='store_true')
    ap.add_argument('--fixtures', type=Path, default=REAL if REAL.exists() else HERE / 'fixtures' / 'sayable.example.jsonl')
    a = ap.parse_args()
    fx = load(a.fixtures)
    PRIVATE.mkdir(exist_ok=True)
    think = False if a.no_think else None
    log = lambda m: print(m, file=sys.stderr, flush=True)
    try:
        bad = sayable.judge([{'id': f['id'], 'text': f['before'], 'context': f['context']} for f in fx], a.model, a.host, think=think, log=log)
        good = sayable.judge([{'id': f['id'], 'text': f['after'], 'context': f['context']} for f in fx], a.model, a.host, think=think, log=log)
    except sayable.Unavailable as e:
        print(f'GLM PASS UNAVAILABLE: {e}'); return 3
    (PRIVATE / 'results-sayable.json').write_text(json.dumps({'model': a.model, 'before': bad, 'after': good},
                                                          ensure_ascii=False, indent=1), encoding='utf-8')
    B, G = {r['id']: r for r in bad}, {r['id']: r for r in good}
    n = len(fx)
    flagged = sum(B[f['id']]['verdict'] == 'fix' for f in fx)
    kept = sum(G[f['id']]['verdict'] == 'keep' for f in fx)
    unsafe = sum(any(x.startswith('lost number') for x in B[f['id']]['notes']) for f in fx)
    ratios = [len(B[f['id']]['rewrite']) / len(f['before']) for f in fx if B[f['id']]['rewrite']]
    known = [len(f['after']) / len(f['before']) for f in fx]
    by_kind = {}
    for f in fx:
        k = by_kind.setdefault(f['kind'], [0, 0]); k[0] += 1; k[1] += B[f['id']]['verdict'] == 'fix'

    lines = [
        '# GLM pass results', '',
        f'Run on {date.today().isoformat()} with `{a.model}` through Ollama, over the {n} real failures in '
        f'`{a.fixtures.name}`. Re-run with `python -I tests/run_sayable_eval.py`. Raw answers are in '
        '`private/results-sayable.json`.', '',
        '| Check | Result |', '|---|---|',
        f'| Bad lines flagged | {flagged} of {n} |',
        f'| Known-good fixes left alone | {kept} of {n} |',
        f'| Rewrites that lost a number | {unsafe} |',
        f'| Rewrite length / bad line length (median) | {sorted(ratios)[len(ratios) // 2]:.2f} |' if ratios else '| Rewrite length | none |',
        f'| Known fix length / bad line length (median) | {sorted(known)[len(known) // 2]:.2f} |', '',
        'Flagged by kind: ' + ', '.join(f'{k} {v[1]} of {v[0]}' for k, v in by_kind.items()) + '.', '',
        '## Every line', '',
        '"GLM on fix" is what the pass said about the known-good fix: keep means it agreed the fix is fine.', '',
        '| id | Bad line | Known fix | GLM rewrite | GLM on fix |', '|---|---|---|---|---|',
    ]
    for f in fx:
        b, g = B[f['id']], G[f['id']]
        rw = b['rewrite'] if b['verdict'] == 'fix' else f"({b['verdict']})"
        gv = g['verdict'] if g['verdict'] != 'fix' else f"fix: {g['rewrite']}"
        lines.append(f"| {f['id']} | {cell(f['before'])} | {cell(f['after'])} | {cell(rw)} | {cell(gv)} |")
    # hand-written notes below the marker survive a re-run
    old = (PRIVATE / 'RESULTS.md').read_text(encoding='utf-8') if (PRIVATE / 'RESULTS.md').exists() else ''
    notes = old[old.index(NOTES):] if NOTES in old else ''
    (PRIVATE / 'RESULTS.md').write_text('\n'.join(lines) + '\n' + ('\n' + notes if notes else ''), encoding='utf-8')
    print(f'flagged {flagged}/{n} bad lines, kept {kept}/{n} known fixes, {unsafe} rewrites lost a number')
    return 0


if __name__ == '__main__':
    sys.exit(main())
