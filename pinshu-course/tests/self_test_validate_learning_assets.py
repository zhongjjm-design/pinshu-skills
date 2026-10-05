#!/usr/bin/env python3
"""Exercise public learning-asset validation with actual Markdown and JSON pairs."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

VALIDATOR = Path(__file__).resolve().parents[1] / "scripts" / "validate-learning-assets.py"


def check(kind: str, path: Path, success: bool, message: str = "") -> None:
    result = subprocess.run([sys.executable, str(VALIDATOR), "--kind", kind, str(path)], capture_output=True, text=True)
    assert (result.returncode == 0) == success, (result.stdout, result.stderr)
    if message:
        assert message in result.stdout, result.stdout


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for name in ("faithful.md", "lecture.md", "second.md"):
            (root / name).write_text("# Actual source\n\nEvidence.\n", encoding="utf-8")
        cards = root / "cards.md"
        index = root / "cards.json"
        cards.write_text("""---
card_count_total: 1
source_lecture: lecture.md
source_transcript: faithful.md
metadata_index: cards.json
---
# Lesson: causal reasoning

### Card 1 · Identify the premise
**Question**: What must be true first?
> [!question]- Answer
> Check the necessary premise.
> Source: lesson notes, section one.
""", encoding="utf-8")
        index.write_text(json.dumps({"schema_version": 1, "asset_type": "active_recall_cards", "source_document": "cards.md", "items": [{"card_id": "L01-01", "position": 1, "card_kind": "atomic"}]}), encoding="utf-8")
        check("cards", cards, True)
        questions = root / "questions.md"
        qi = root / "questions.json"
        questions.write_text("""---
question_count_total: 1
source_lecture: lecture.md
metadata_index: questions.json
---
# Lesson: practice

### Question 1 · Transfer
**Question**: How would the rule change in another setting?
> [!question]- Reference answer
> State the limiting condition.
""", encoding="utf-8")
        qi.write_text(json.dumps({"schema_version": 1, "asset_type": "training_questions", "source_document": "questions.md", "items": [{"q_id": "Q01-01", "position": 1}]}), encoding="utf-8")
        check("questions", questions, True)
        chinese = root / "zh-cards.md"
        chinese.write_text(cards.read_text().replace("cards.json", "zh-cards.json").replace("Card 1 · Identify the premise", "\u53611·\u95ee\u9898").replace("**Question**: What must be true first?", "**\u95ee\u9898**\uff1a\u5148\u51b3\u6761\u4ef6\u662f\u4ec0\u4e48\uff1f").replace("- Answer", "- \u7b54\u6848"), encoding="utf-8")
        (root / "zh-cards.json").write_text(json.dumps({"asset_type": "active_recall_cards", "source_document": "zh-cards.md", "items": [{"card_id": "L01-01", "position": 1}]}), encoding="utf-8")
        check("cards", chinese, True)
        clues = root / "clues.md"
        clues.write_text("""---
document_type: clues
---
# Open questions
### Clue 1
Knowledge object: A concept
Current-lesson contribution: New distinction
Cross-lesson rationale: Compare next lesson
Later trigger: On reading lesson two
Evidence state: verified across lessons
Current-lesson source: faithful.md
Second source: second.md
""", encoding="utf-8")
        check("clues", clues, True)
        clues.write_text(clues.read_text().replace("Second source: second.md", ""), encoding="utf-8")
        check("clues", clues, False, "no second source")
        index.write_text(index.read_text().replace('"position": 1', '"position": 2'), encoding="utf-8")
        check("cards", cards, False, "positions must follow")
        index.write_text(index.read_text().replace('"position": 2', '"position": 1').replace("active_recall_cards", "training_questions"), encoding="utf-8")
        check("cards", cards, False, "asset_type must be active_recall_cards")
        cards.write_text(cards.read_text().replace("### Card 1", "<!-- card_id: hidden -->\n### Card 1"), encoding="utf-8")
        check("cards", cards, False, "user-facing body contains HTML")
    print("learning_assets self-test: PASS (4 valid, 4 invalid cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
