"""deslop.py: finds sentence literals and nothing else, refuses rewrites that lose a number, and writes back escaped."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import deslop as D

SRC = """const a={name:'Iron Helmet',text:'It\\'s a round iron helmet. You take 5 percent less damage.'};
// this.banner('A comment sentence that should be skipped because it is commented out.');
const k='walk-0',u='/sprites/world/hero.png',t=`Template ${x} sentence is skipped here, always.`;
banner('You choked on the smoke. Get out of the cloud now.');
"""


def test_scan_finds_sentences_only(tmp_path):
    (tmp_path / 'src').mkdir(); (tmp_path / 'src' / 'a.ts').write_text(SRC)
    got = [c['text'] for c in D.scan(tmp_path, 'src/**/*.ts')]
    assert got == ["It's a round iron helmet. You take 5 percent less damage.", 'You choked on the smoke. Get out of the cloud now.']


def test_accept_keeps_numbers_and_length():
    old = "It's a round iron helmet. You take 5 percent less damage."
    assert D.accept(old, "A round iron helmet. You take 4 percent less damage.") == old
    assert D.accept(old, old * 3) == old
    assert D.accept(old, "A round iron helmet. You take 5 percent less damage.") == "A round iron helmet. You take 5 percent less damage."


def test_apply_writes_back_escaped(tmp_path):
    (tmp_path / 'src').mkdir(); f = tmp_path / 'src' / 'a.ts'; f.write_text(SRC)
    (tmp_path / 'deslop-candidates.json').write_text(json.dumps(D.scan(tmp_path, 'src/**/*.ts')))
    (tmp_path / 'deslop-proposals.json').write_text(json.dumps({"It's a round iron helmet. You take 5 percent less damage.": "It's an iron helmet. You take 5 percent less damage."}))
    assert D.apply(tmp_path) == 1
    assert "text:'It\\'s an iron helmet. You take 5 percent less damage.'" in f.read_text()


def test_accept_refuses_a_different_sentence_and_lost_names():
    assert D.accept("This wall is cracked. You need Smash to break it.", "This gap is too wide. You need Dash.").startswith('This wall')
    assert D.accept("Bel keeps watch from here, and patrols show on your map.", "Someone keeps watch from here, and patrols show on your map.").startswith('Bel')
    assert D.accept("Read the overhead. Space parry. Cut to riposte.", "Watch for the overhead. Press Space to parry. Cut to riposte.") == "Watch for the overhead. Press Space to parry. Cut to riposte."
