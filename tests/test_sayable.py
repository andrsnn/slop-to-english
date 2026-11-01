"""Offline tests for tools/sayable.py: reply parsing, rewrite checks, and the fallback when GLM cannot answer.
No network: urllib is replaced with fakes.   python -m unittest tests/test_sayable.py   (or pytest)"""
import io, json, sys, unittest, urllib.error
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
import sayable as S  # noqa: E402

TAGS = {'models': [{'name': 'glm-5.3:cloud', 'model': 'glm-5.3:cloud'}]}


class Resp:
    def __init__(self, obj): self.obj = obj
    def read(self): return json.dumps(self.obj).encode()


def fake_urlopen(chat_reply=None, chat_error=None, tags=TAGS, down=False):
    """A stand-in for urllib.request.urlopen: /api/tags answers with `tags`, /api/chat with `chat_reply` or `chat_error`."""
    def urlopen(req, timeout=None):
        url = req if isinstance(req, str) else req.full_url
        if down: raise urllib.error.URLError(ConnectionRefusedError(10061, 'connection refused'))
        if url.endswith('/api/tags'): return Resp(tags)
        if chat_error: raise chat_error
        return Resp({'message': {'role': 'assistant', 'content': chat_reply}})
    return urlopen


def http_error(code, body):
    return urllib.error.HTTPError('http://x/api/chat', code, 'err', {}, io.BytesIO(body.encode()))


class ParseTests(unittest.TestCase):
    def test_plain_json(self):
        got = S.parse_reply('{"lines":[{"id":"1","verdict":"keep","problem":"","rewrite":""},'
                            '{"id":"2","verdict":"fix","problem":"who?","rewrite":"The AI drew it."}]}', ['1', '2'])
        self.assertEqual(got['1']['verdict'], 'keep')
        self.assertEqual(got['2'], {'verdict': 'fix', 'problem': 'who?', 'rewrite': 'The AI drew it.'})

    def test_code_fence_and_prose_around(self):
        got = S.parse_reply('Here you go:\n```json\n{"lines":[{"id":"1","verdict":"FIX","problem":"p","rewrite":"r"}]}\n```', ['1'])
        self.assertEqual(got['1']['verdict'], 'fix')

    def test_bare_list_without_ids_uses_order(self):
        got = S.parse_reply('[{"verdict":"keep"},{"verdict":"fix","rewrite":"x"}]', ['a', 'b'])
        self.assertEqual((got['a']['verdict'], got['b']['verdict']), ('keep', 'fix'))

    def test_missing_and_broken_answers_are_unknown(self):
        got = S.parse_reply('{"lines":[{"id":"1","verdict":"fix","rewrite":""}]}', ['1', '2'])
        self.assertEqual(got['1']['verdict'], 'unknown')  # a fix with no rewrite is not usable
        self.assertEqual(got['2']['verdict'], 'unknown')
        self.assertEqual(S.parse_reply('not json at all', ['1'])['1']['verdict'], 'unknown')


class CheckTests(unittest.TestCase):
    def test_lost_and_new_numbers(self):
        self.assertIn('lost number 5', S.check_rewrite('Free is now 5 a day.', 'The free plan is smaller now.'))
        self.assertIn('new number 6', S.check_rewrite('Some projects.', 'All 6 projects.'))
        self.assertEqual(S.check_rewrite('It scored 4, then 9.', 'My judge scored it 4, then 9.'), [])

    def test_much_longer_is_noted(self):
        self.assertTrue(any(n.startswith('longer') for n in S.check_rewrite('Short line.', 'A much much much much longer line than before.')))

    def test_split_text_skips_markup(self):
        items = S.split_text('# Title\n\n- First line.\n```\ncode()\n```\n|---|---|\n2. Second line.\n')
        self.assertEqual([x['text'] for x in items], ['Title', 'First line.', 'Second line.'])


class FallbackTests(unittest.TestCase):
    def run_main(self, urlopen, text='When it fails, fix tool first.\n'):
        buf = io.StringIO()
        with mock.patch('urllib.request.urlopen', urlopen), mock.patch('time.sleep'), \
                mock.patch('sys.stdin', io.StringIO(text)), redirect_stdout(buf):
            code = S.main(['-'])
        return code, buf.getvalue()

    def test_ollama_not_running(self):
        code, out = self.run_main(fake_urlopen(down=True))
        self.assertEqual(code, 3)
        self.assertIn('GLM PASS UNAVAILABLE: Ollama is not answering', out)
        self.assertIn('Fall back to the SKILL.md rules alone', out)

    def test_model_not_pulled(self):
        code, out = self.run_main(fake_urlopen(tags={'models': []}))
        self.assertEqual(code, 3)
        self.assertIn('ollama pull glm-5.3:cloud', out)

    def test_out_of_usage(self):
        err = http_error(429, '{"error":"you have reached your session usage limit, upgrade for higher limits"}')
        code, out = self.run_main(fake_urlopen(chat_error=err))
        self.assertEqual(code, 3)
        self.assertIn('out of usage', out)

    def test_not_signed_in(self):
        code, out = self.run_main(fake_urlopen(chat_error=http_error(401, '{"error":"unauthorized"}')))
        self.assertEqual(code, 3)
        self.assertIn('ollama signin', out)

    def test_working_reply_prints_fix(self):
        reply = json.dumps({'lines': [{'id': '1', 'verdict': 'fix', 'problem': "'it' names nothing",
                                       'rewrite': 'When the tool fails, fix it first.'}]})
        code, out = self.run_main(fake_urlopen(chat_reply=reply))
        self.assertEqual(code, 1)
        self.assertIn('FIX 1: When it fails, fix tool first.', out)
        self.assertIn('say:     When the tool fails, fix it first.', out)

    def test_all_keep_exits_zero(self):
        reply = json.dumps({'lines': [{'id': '1', 'verdict': 'keep', 'problem': '', 'rewrite': ''}]})
        code, out = self.run_main(fake_urlopen(chat_reply=reply), text='The default timeout is 30 seconds.\n')
        self.assertEqual(code, 0)
        self.assertIn('1 lines, 0 to fix', out)


if __name__ == '__main__':
    unittest.main()
