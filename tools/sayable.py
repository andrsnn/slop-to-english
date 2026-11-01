"""sayable: ask GLM 5.3 (through Ollama) whether a person would say each line out loud, and how they would say it.

  python tools/sayable.py copy.txt                       one line of copy per text line (markdown bullets are fine)
  python tools/sayable.py strings.json --context "Chatbot lines in a comedy game"
  echo "When it fails, fix tool first." | python tools/sayable.py -
  python tools/sayable.py copy.txt --json out.json       also write every verdict as JSON

For every line the model answers "keep" or "fix". A fix comes with the problem (the words a listener trips on and the
question they would ask) and a rewrite: plain, the same length or shorter, every number and name kept, no new facts.
Each line is judged on its own, because every line has to make sense out of context.

The model is glm-5.3:cloud by default. It runs on Ollama's servers, not on this machine, so it needs Ollama running and
signed in, with usage left on the account. When any of that is missing, the script prints one line starting with
"GLM PASS UNAVAILABLE:" and the reason, and exits with code 3. Then use SKILL.md's rules alone.

Exit codes: 0 every line passes, 1 at least one line to fix, 2 bad input, 3 GLM unavailable.
Standard library only.
"""
import argparse, json, re, sys, time, urllib.error, urllib.request
from pathlib import Path

DEFAULT_MODEL = 'glm-5.3:cloud'
DEFAULT_HOST = 'http://127.0.0.1:11434'
NUM = re.compile(r'\d+(?:[.,]\d+)?')

PROMPT = """You check copy that a person will say out loud or read on screen: narration, game text, UI text, slides,
READMEs. The rule: every line must be something a person would actually say out loud to a friend, and it must make
sense heard once, with no other context. Less text is better.

For each line:
1. Say it out loud once to a friend who has seen nothing else. Would they stop and ask "what does that mean?",
   "who did that?", "of what?", "which one?" or "what are you talking about?"
2. It fails if any of these is true:
   - No one does the action. A thing acts like a person: drawings "use" a body, rules "live" somewhere, a job "asks",
     a word "turns floors pink", a move "disappears". Name who or what really acts (I, the AI, the model, the tool).
   - A word points at something the line never names: "it", "that version", "those checks", "another round",
     "one set", "in the before and the after".
   - A noun or unit is dropped: "every node gives one more", "hurts less", "5 a day, plus 20 to start".
   - A figure of speech stands in for a plain fact: climbs, lands, sits, feeds, clicks, lives.
   - The listener has to decode it in two steps, like a riddle or a joke that explains itself.
   - It has a written shape nobody speaks: stacked clauses, a "which" clause that lands on the wrong noun, stacked
     hedges ("roughly several"), poster shorthand that drops "the" ("fix tool first").
   - It packs more into one sentence than a person says in one breath.
3. Jokes and game lines (when the context says the line is a joke, or a game character's line) have stricter rules,
   because the player hears them once, mid-action:
   - The thing on screen does the joke. A line that explains the joke fails. A second sentence that gives a reason
     ("because...", "instead of paying...", "we spent the budget on...", anything about investors, budgets or fees
     the player cannot see) is explaining the joke.
   - A joke the listener has to work out in two steps fails, even if it is clever.
   - Over 14 words fails. Under 10 is best.
   - The rewrite names the thing or the event and adds one short, plain reaction. Do not keep the old joke and only
     clean its grammar; write a simpler line about the same thing.
4. If it fails, rewrite it the way the speaker would say it: who does what, in plain words, one idea per sentence.
   Keep every number, name and fact. Never add a fact. Make it shorter. Only when an actor or a noun was missing may
   it grow, by those few words. Do not just swap a word; say the line again from scratch.
5. If it passes, the verdict is "keep" and the rewrite is "". Many lines are already fine. Flag a line only when the
   friend would really stop you and ask. A word you would have chosen differently is not a reason; keep it.

Examples:
- "The chart climbs from 4 to 9." -> fix: charts do not climb, and no one gives the scores. -> "My judge scored it 4, then 9."
- "The screenshot earns a 6 out of 10." -> fix: a screenshot does not earn anything. -> "My judge gave this screenshot a 6 out of 10."
- "We moved the needle on churn: 5.1% down to 3.4%." -> fix: idiom for a number. -> "Churn fell from 5.1% to 3.4%."
- "The default timeout is 30 seconds." -> keep.
- (game joke, the player got a hammer) "Here's your hammer. Hit the server until the chatbot agrees with you." -> fix:
  the listener has to work out the joke. -> "A hammer! Every bubble needs one."
- (game joke, the player got a wrench) "Here's your wrench. You bought the machine. Repairs are your problem." -> fix:
  three sentences about ownership the player cannot see. -> "A wrench! Righty tighty, lefty loosey."
- (game joke, the player got a scissors tool) "Scissors! Your natural enemy." -> keep.

Context for these lines: {context}

Answer with JSON only, in this shape, one entry per input line, same ids:
{{"lines": [{{"id": "1", "verdict": "keep", "problem": "", "rewrite": ""}},
            {{"id": "2", "verdict": "fix", "problem": "the words a listener trips on, and the question they would ask", "rewrite": "..."}}]}}
"""


class Unavailable(Exception):
    """Ollama or the model cannot answer right now (not running, not signed in, out of usage, model missing)."""


# ---------- input ----------

def read_items(path: str) -> list[dict]:
    raw = sys.stdin.read() if path == '-' else Path(path).read_text(encoding='utf-8')
    if path.endswith('.json') or raw.lstrip().startswith('['):
        data = json.loads(raw)
        items = []
        for i, x in enumerate(data, 1):
            if isinstance(x, str): items.append({'id': str(i), 'text': x})
            elif isinstance(x, dict) and isinstance(x.get('text'), str):
                items.append({'id': str(x.get('id', i)), 'text': x['text'], 'context': x.get('context', '')})
        return [x for x in items if x['text'].strip()]
    return split_text(raw)


def split_text(raw: str) -> list[dict]:
    """One item per line of prose. Skips blank lines, code blocks, tables' separator rows and bare headings markup."""
    items, in_code = [], False
    for line in raw.splitlines():
        s = line.strip()
        if s.startswith('```'): in_code = not in_code; continue
        if in_code or not s or set(s) <= set('|-: '): continue
        s = re.sub(r'^(#{1,6}\s+|[-*+]\s+|>\s*|\d+[.)]\s+)', '', s).strip()
        if s: items.append({'id': str(len(items) + 1), 'text': s})
    return items


# ---------- model call ----------

def check_available(host: str, model: str, timeout: float = 5) -> None:
    try:
        tags = json.loads(urllib.request.urlopen(host + '/api/tags', timeout=timeout).read())
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise Unavailable(f'Ollama is not answering at {host} ({reason_of(e)}). Start Ollama, then retry.')
    names = {m.get('name') for m in tags.get('models', [])} | {m.get('model') for m in tags.get('models', [])}
    if model not in names and model + ':latest' not in names:
        raise Unavailable(f'model {model} is not in `ollama list`. Run `ollama pull {model}` (cloud models need `ollama signin`).')


def reason_of(e: Exception) -> str:
    r = getattr(e, 'reason', None) or e
    return str(r)[:200]


def classify_http_error(code: int, body: str) -> str | None:
    """A reason string when the error means GLM cannot be used right now; None when a retry might work."""
    low = body.lower()
    if code == 401 or 'unauthorized' in low or 'signin' in low or 'sign in' in low:
        return 'Ollama is not signed in for cloud models. Run `ollama signin`.'
    if code == 429 or any(w in low for w in ('usage limit', 'rate limit', 'quota', 'upgrade for higher limits', 'too many requests')):
        return f'the Ollama account is out of usage ("{body.strip()[:160]}"). It resets after a few hours.'
    if code == 404 and 'not found' in low:
        return f'the model is not available ("{body.strip()[:160]}").'
    return None


def chat(host: str, model: str, system: str, user: str, think: bool | None, timeout: float = 300) -> str:
    payload = {'model': model, 'stream': False, 'format': 'json', 'options': {'temperature': 0.2},
               'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]}
    if think is not None: payload['think'] = think
    req = urllib.request.Request(host + '/api/chat', json.dumps(payload).encode(), {'Content-Type': 'application/json'})
    last = ''
    for attempt in range(3):
        try:
            body = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
            if body.get('error'):
                why = classify_http_error(200, body['error'])
                if why: raise Unavailable(why)
                last = body['error']
            else:
                return body.get('message', {}).get('content', '')
        except urllib.error.HTTPError as e:
            text = e.read().decode('utf-8', 'replace')
            why = classify_http_error(e.code, text)
            if why: raise Unavailable(why)
            last = f'HTTP {e.code}: {text[:200]}'
        except (urllib.error.URLError, OSError) as e:
            last = reason_of(e)
        time.sleep(2 * (attempt + 1))
    raise Unavailable(f'GLM did not answer after 3 tries ({last}).')


# ---------- parsing and checks ----------

def parse_reply(content: str, ids: list[str]) -> dict[str, dict]:
    """Model reply -> {id: {verdict, problem, rewrite}}. Tolerates code fences, prose around the JSON, a bare list,
    and missing ids (those come back as verdict "unknown")."""
    text = re.sub(r'^```(?:json)?\s*|\s*```$', '', content.strip(), flags=re.S)
    data = None
    for cand in (text, text[text.find('{'):text.rfind('}') + 1] if '{' in text else '',
                 text[text.find('['):text.rfind(']') + 1] if '[' in text else ''):
        try:
            data = json.loads(cand); break
        except ValueError:
            continue
    rows = []
    if isinstance(data, dict):
        rows = data.get('lines') or next((v for v in data.values() if isinstance(v, list)), [])
    elif isinstance(data, list):
        rows = data
    out = {}
    for pos, r in enumerate(rows):
        if not isinstance(r, dict): continue
        rid = str(r.get('id', ids[pos] if pos < len(ids) else ''))
        verdict = str(r.get('verdict', '')).strip().lower()
        verdict = verdict if verdict in ('keep', 'fix') else 'unknown'
        rewrite = (r.get('rewrite') or '').strip() if isinstance(r.get('rewrite'), str) else ''
        if verdict == 'fix' and not rewrite: verdict = 'unknown'
        out[rid] = {'verdict': verdict, 'problem': str(r.get('problem') or '').strip(), 'rewrite': rewrite}
    for i in ids:
        out.setdefault(i, {'verdict': 'unknown', 'problem': 'the model gave no answer for this line', 'rewrite': ''})
    return {i: out[i] for i in ids}


def tidy(s: str) -> str:
    return (s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
             .replace(' — ', ', ').replace('—', ', ').strip())


def check_rewrite(before: str, after: str) -> list[str]:
    """Problems with a rewrite that the caller should know about. 'lost number' means: do not use it as is."""
    notes = []
    lost = [n for n in NUM.findall(before) if n not in NUM.findall(after)]
    added = [n for n in NUM.findall(after) if n not in NUM.findall(before)]
    if lost: notes.append('lost number ' + ', '.join(lost))
    if added: notes.append('new number ' + ', '.join(added))
    if len(after) > 1.2 * len(before) + 5: notes.append(f'longer ({len(after)} vs {len(before)} characters)')
    return notes


# ---------- run ----------

def judge(items: list[dict], model=DEFAULT_MODEL, host=DEFAULT_HOST, context='', batch=12, think=None,
          log=lambda m: None) -> list[dict]:
    check_available(host, model)
    results = []
    for start in range(0, len(items), batch):
        chunk = items[start:start + batch]
        own = {x.get('context') or '' for x in chunk}
        per_line = not context and len(own) > 1
        ctx = (context or (own.pop() if len(own) == 1 else '') or 'not given; judge each line as general copy'
               if not per_line else 'given with each line')
        system = PROMPT.format(context=ctx)
        user = json.dumps([{'id': x['id'], 'text': x['text'], **({'context': x.get('context', '')} if per_line else {})}
                           for x in chunk], ensure_ascii=False)
        got = parse_reply(chat(host, model, system, user, think), [x['id'] for x in chunk])
        for x in chunk:
            v = got[x['id']]
            rewrite = tidy(v['rewrite']) if v['verdict'] == 'fix' else ''
            notes = check_rewrite(x['text'], rewrite) if rewrite else []
            results.append({'id': x['id'], 'text': x['text'], 'verdict': v['verdict'], 'problem': v['problem'],
                            'rewrite': rewrite, 'notes': notes})
        log(f'{min(start + batch, len(items))}/{len(items)} lines judged')
    return results


def report(results: list[dict], model: str) -> str:
    fixes = [r for r in results if r['verdict'] == 'fix']
    unknown = [r for r in results if r['verdict'] == 'unknown']
    out = [f'GLM pass ({model}): {len(results)} lines, {len(fixes)} to fix, {len(unknown)} with no answer.']
    for r in results:
        if r['verdict'] == 'keep': continue
        out.append('')
        out.append(f"{'FIX' if r['verdict'] == 'fix' else '???'} {r['id']}: {r['text']}")
        if r['problem']: out.append(f"  problem: {r['problem']}")
        if r['rewrite']: out.append(f"  say:     {r['rewrite']}")
        if r['notes']: out.append(f"  check:   {'; '.join(r['notes'])}")
    return '\n'.join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input', help="text file, JSON list, or - for stdin")
    ap.add_argument('--context', default='', help='what the copy is, e.g. "Voiceover for a YouTube video"')
    ap.add_argument('--model', default=DEFAULT_MODEL)
    ap.add_argument('--host', default=DEFAULT_HOST)
    ap.add_argument('--batch', type=int, default=12)
    ap.add_argument('--no-think', action='store_true', help='ask the model to skip its thinking (uses less usage)')
    ap.add_argument('--json', dest='json_out', help='also write every verdict to this JSON file')
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    try:
        items = read_items(a.input)
    except (OSError, ValueError) as e:
        print(f'bad input: {e}', file=sys.stderr); return 2
    if not items:
        print('bad input: no lines to judge', file=sys.stderr); return 2
    try:
        results = judge(items, a.model, a.host, a.context, a.batch, False if a.no_think else None,
                        log=lambda m: print(m, file=sys.stderr, flush=True))
    except Unavailable as e:
        msg = f'GLM PASS UNAVAILABLE: {e} Fall back to the SKILL.md rules alone.'
        print(msg)
        if a.json_out: Path(a.json_out).write_text(json.dumps({'status': 'unavailable', 'reason': str(e)}, indent=1), encoding='utf-8')
        return 3
    if a.json_out:
        Path(a.json_out).write_text(json.dumps({'status': 'ok', 'model': a.model, 'lines': results},
                                               ensure_ascii=False, indent=1), encoding='utf-8')
    print(report(results, a.model))
    return 1 if any(r['verdict'] == 'fix' for r in results) else 0


if __name__ == '__main__':
    sys.exit(main())
