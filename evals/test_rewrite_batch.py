"""Tests for rewrite_batch.py. Run: python -m unittest evals/test_rewrite_batch.py"""
import json, os, sys, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import rewrite_batch as rb  # noqa: E402


def fake_model(table):
    """An ask() that rewrites by lookup and counts requests."""
    calls = []

    def ask(system, user):
        calls.append(user)
        items = json.loads(user)
        return "```json\n" + json.dumps([table.get(it["text"], it["text"]) for it in items]) + "\n```"
    return ask, calls


class CheckTests(unittest.TestCase):
    def test_passes_a_plain_shorter_rewrite(self):
        self.assertEqual(rb.check("Unlock the power of ${n} drones", "Use ${n} drones"), [])

    def test_tokens_must_match_in_order(self):
        self.assertIn("tokens", rb.check("Hold {{0}} to fire {{1}}", "Hold {{1}} to fire {{0}}"))
        self.assertIn("tokens", rb.check("<b>${n}</b> crew aboard", "${n} crew aboard"))
        self.assertIn("tokens", rb.check("Up \\u00b7 down", "Up - down"))

    def test_length_numbers_terms_banned(self):
        self.assertIn("length", rb.check("Fire now", "Fire the gun now"))
        self.assertIn("numbers", rb.check("Lasts a while here", "Lasts 30 s"))
        self.assertTrue(any(p.startswith("terms") for p in rb.check("Return the ore to base now", "Bring ore to Kessa")))
        self.assertIn("banned", rb.check("A great tool for all of the crew", "A seamless crew tool"))

    def test_sentence_start_capitals_are_not_new_terms(self):
        self.assertEqual(rb.check("the guns are ready to fire now. go", "Guns ready. Go"), [])


class BatchTests(unittest.TestCase):
    def test_batches_cache_and_rows(self):
        items = ["Unleash a tapestry of fire", {"id": "b", "text": "Pause", "context": "menu"}, "Hold {0} to boost now"]
        ask, calls = fake_model({"Unleash a tapestry of fire": "Fire a lot",
                                 "Hold {0} to boost now": "Boost with {1}"})
        with tempfile.TemporaryDirectory() as d:
            cache = os.path.join(d, "c.jsonl")
            out = rb.rewrite_all(items, ask, "sys", batch_size=2, workers=3, cache_path=cache)
            self.assertEqual(len(calls), 2)
            rows = rb.build_rows(items, out)
            self.assertEqual([r["after"] for r in rows], ["Fire a lot", "Pause", "Boost with {1}"])
            self.assertEqual([r["ok"] for r in rows], [True, True, False])
            self.assertFalse(rows[1]["changed"])
            self.assertEqual(rows[1]["id"], "b")
            rb.rewrite_all(items, ask, "sys", batch_size=2, workers=3, cache_path=cache)
            self.assertEqual(len(calls), 2, "second run is served from the cache")

    def test_bad_batch_reply_falls_back_to_single_items(self):
        replies = iter(["not json", "still not json", '["A"]', '["B"]'])
        out = rb.rewrite_all(["one two", "three four"], lambda s, u: next(replies), "sys", batch_size=2, workers=1)
        self.assertEqual(out, {0: "A", 1: "B"})

    def test_parse_reply_handles_think_and_objects(self):
        self.assertEqual(rb.parse_reply('<think>hm</think>[{"text":"x"},"y"]', 2), ["x", "y"])
        self.assertIsNone(rb.parse_reply('["x"]', 2))


if __name__ == "__main__":
    unittest.main()
