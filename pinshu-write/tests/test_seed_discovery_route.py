"""Structure checks for the 3.5.0 route: the master gate, ten steps and three gates, one writer and four positions,
a fact sheet the writer never makes, and no dangling pointers. These prove the documents are wired together, not
that the articles are good: that is judged only by real articles."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
REFERENCES = SKILL / "references"
MAINTAINERS = ("lessons.md", "changelog.md", "proven.md")
# Role, step and file names retired up to 3.5.0; they may appear only in the maintainers' files.
REMOVED_NAMES = ("wording editor", "judgment gate", "skeleton gate", "cold reader", "red team", "editor-in-chief",
                 "Structure editor", "Managing editor", "Seed check", "Attraction reader", "After-revision read",
                 "Good-article check", "AI-flavor reader and flow", "Facts and risk", "Originality check",
                 "Stop 2", "Stop 3", "Stop 4", "stop 4", "2-research-and-counter.md", "3-structure.md", "4-writing.md",
                 "writer_parts", "second_writer", "seven questions")
POSITIONS = ("Editor", "Reader", "Expert", "Fact checker")


def read(rel):
    return (SKILL / rel).read_text(encoding="utf-8")


def doc_files():
    return [SKILL / "SKILL.md"] + sorted(REFERENCES.glob("*.md"))


def section(text, start, end):
    return text.split(start, 1)[1].split(end, 1)[0]


class RouteTests(unittest.TestCase):
    def test_master_gate_comes_first(self):
        text = read("SKILL.md")
        self.assertLess(text.index("## The master gate"), text.index("## The route"))
        gate = section(text, "## The master gate", "## What it is for")
        for must in ("动笔前先答三问", "第十六节", "why does the reader open this article", "The Skill keeps no set of its own"):
            self.assertIn(must, gate)

    def test_entry_table_routes_every_entry(self):
        table = section(read("SKILL.md"), "| The author brings | Enter at |", "\n\n")
        for row in ("| Nothing", "| An idea, a link, someone else's article or title, any length | Step 1",
                    "| A title or an outline | Step 3", "| A draft to look at | Step 6",
                    "| Comments on a draft | Revision by size", "| The author's own hand edit of a draft | Edit pairs"):
            self.assertIn(row, table)

    def test_route_has_ten_steps_and_three_gates(self):
        route = section(read("SKILL.md"), "## The route", "## The roles")
        steps = re.findall(r"^\| (\d+) [A-Z]", route, re.M)
        self.assertEqual(steps, [str(n) for n in range(1, 11)])
        self.assertEqual(re.findall(r"\*\*Gate (\d)\*\*", route), ["1", "2", "3"])
        headings = re.findall(r"^## (Topic|Gate \d)", read("references/stops.md"), re.M)
        self.assertEqual(headings, ["Topic", "Gate 1", "Gate 2", "Gate 3"])

    def test_gate_two_sees_title_outline_and_opening(self):
        self.assertIn("Title, outline, opening and first section", read("SKILL.md"))
        gate2 = section(read("references/stops.md"), "## Gate 2", "## Gate 3")
        self.assertIn("The opening and first section, written in full", gate2)
        self.assertIn("The last place anything is overturned", gate2)

    def test_hard_gates_are_on_the_route(self):
        text = read("SKILL.md")
        self.assertIn("--length 2000-2500 --hard-max 2500", text)
        self.assertIn("One-sentence paragraphs in a row", text)


class RoleTests(unittest.TestCase):
    def test_one_writer_and_four_positions(self):
        roles = section(read("SKILL.md"), "## The roles", "## Rules that do not bend")
        rows = re.findall(r"^\| ([A-Z][a-z]+(?: [a-z]+)?) \|", roles, re.M)
        self.assertEqual(rows[1:], ["Writer", *POSITIONS])  # the first match is the header row
        review = read("references/5-review.md")
        for position in POSITIONS:
            self.assertIn(f"| {position} |", review)

    def test_writer_never_makes_the_fact_sheet(self):
        review = read("references/5-review.md")
        self.assertIn("never by the writer", review)
        self.assertIn("scripts/extract_facts.py", review)
        self.assertTrue((SKILL / "scripts" / "extract_facts.py").is_file())

    def test_positions_get_only_their_own_material(self):
        review = read("references/5-review.md")
        self.assertIn("Pass one never sees the draft", review)
        self.assertIn("one fresh call per step", review.replace("The reader runs as one call per step", "one fresh call per step"))
        self.assertIn("Each call is fresh, so the reader cannot know what comes next", review)

    def test_only_facts_and_copying_force_a_change(self):
        self.assertIn("Only hard facts and copying force a change.", read("SKILL.md"))
        review = read("references/5-review.md")
        self.assertIn("锋利的话、冲突、钩子一样不许磨软", review)
        self.assertIn("listed apart", review)

    def test_prompts_cover_every_position(self):
        prompts = read("references/prompts.md")
        for heading in ("## Editor", "## Reader", "## Expert", "## Fact checker, pass one: the fact sheet",
                        "## Fact checker, pass two: copying", "## Fact sheet: names", "## Fallback writer: revise"):
            self.assertIn(heading, prompts)


class WritingTests(unittest.TestCase):
    def test_three_questions_point_at_the_standard(self):
        step1 = section(read("references/write.md"), "## Step 1", "## Step 3")
        self.assertIn("动笔前先答三问", step1)
        self.assertIn("第十六节", step1)

    def test_title_candidates_pass_two_checks_before_showing(self):
        step3 = section(read("references/write.md"), "## Step 3", "## Step 4")
        self.assertIn("an ordinary reader understands it at a glance", step3)
        self.assertIn("with the company and case names removed, the reader still cares", step3)

    def test_core_changed_stops_otherwise_write_through(self):
        step4 = section(read("references/write.md"), "## Step 4", "## Step 7")
        self.assertIn("Changed: stop and go back to gate 2. Unchanged: write to the end without stopping.", step4)

    def test_fallback_brief_carries_what_to_write_not_rules(self):
        brief = section(read("references/write.md"), "## When the session cannot write", "## After 定稿")
        bottom = brief.split("```text", 1)[1].split("```", 1)[0]
        self.assertEqual(re.findall(r"^(\d)\. ", bottom, re.M), ["1", "2", "3"])
        self.assertIn("The seed, whole and verbatim", brief)
        self.assertIn("not a rule book", brief)

    def test_exemplars_are_found_offered_and_read_before_writing(self):
        write = read("references/write.md")
        step3 = section(write, "## Step 3", "## Step 4")
        self.assertIn("**Exemplars.**", step3)
        self.assertIn("**How the piece moves**", step3)
        step4 = section(write, "## Step 4", "## Step 7")
        self.assertIn("**Read before writing.** The standard's 利他 paragraph first", step4)
        self.assertIn("Then the picked exemplars, whole", step4)
        self.assertIn("exemplar candidates", section(read("references/stops.md"), "## Gate 2", "## Gate 3"))

    def test_titles_come_from_two_vendors_and_changes_are_read_again(self):
        step3 = section(read("references/write.md"), "## Step 3", "## Step 4")
        self.assertIn("Title and opening candidates from two vendors", step3)
        review = read("references/5-review.md")
        self.assertIn("**The editor's second pass** replaces the old read of what changed", review)
        prompts = read("references/prompts.md")
        for heading in ("## Title and opening candidates", "## Editor: pass two"):
            self.assertIn(heading, prompts)

    def test_edit_rules_reach_the_editor(self):
        self.assertIn("The edit rules reach the editor position", read("references/write.md"))
        self.assertIn("修改规律.md", read("references/5-review.md"))


class ReviewOrderTests(unittest.TestCase):
    """3.6: the editor runs after grading, re-checks come before grading, and the writer hands in a change list."""

    def test_rechecks_come_before_grading_and_grading_waits(self):
        review = read("references/5-review.md")
        self.assertLess(review.index("### The two re-checks (补核)"), review.index("### Grading"))
        self.assertLess(review.index("### Grading"), review.index("### The editor's first pass"))
        self.assertIn("Grading waits for both.", review)
        self.assertIn("20 minutes after sending", review)

    def test_grading_can_stop_the_route_before_the_editor(self):
        self.assertIn("stop and take it to the author before the editor runs", read("references/5-review.md"))
        self.assertIn("## When review stops the route", read("references/stops.md"))
        self.assertIn("grading puts a finding at 动骨架", read("SKILL.md"))

    def test_editor_first_pass_never_gets_the_outline_or_findings(self):
        review = read("references/5-review.md")
        editor = section(review, "### The editor's first pass", "## Merging")
        for withheld in ("The reader's record", "the outline", "the three answers", "self-check record"):
            self.assertIn(withheld, editor)
        self.assertIn("built only after the first pass has been delivered", review)

    def test_expert_never_gets_the_fact_sheet(self):
        review = read("references/5-review.md")
        row = next(line for line in review.splitlines() if line.startswith("| Expert |"))
        never = row.split("|")[3]
        self.assertIn("The fact sheet", never)
        self.assertIn("第十五节", never)

    def test_writer_hands_in_a_change_list_and_self_checks(self):
        write = read("references/write.md")
        self.assertIn("**The change list**", section(write, "## Step 7", "## When the session cannot write"))
        self.assertIn("**One question, one answer.**", section(write, "## Step 1", "## Step 3"))

    def test_fact_checker_has_five_statuses_and_a_second_recheck_card(self):
        prompts = read("references/prompts.md")
        self.assertIn("## Fact checker: second re-check", prompts)
        for status in ("有出处", "对不上", "待补", "查不到", "无需核"):
            self.assertIn(status, section(prompts, "## Fact checker, pass one", "## Fact checker, pass two"))
        self.assertTrue((SKILL / "scripts" / "check_fact_notes.py").is_file())


class WriterSideTests(unittest.TestCase):
    """3.7: the writer reads the exemplars and the standard's writing sections, reads its draft through, never lengthens a sentence."""

    def test_writer_reads_the_standard_on_writing_and_reads_the_draft_through(self):
        step4 = section(read("references/write.md"), "## Step 4", "## Step 7")
        self.assertIn("第五节", step4)
        self.assertIn("第九节", step4)
        self.assertIn("**Read it through, then fix by the paragraph.**", step4)

    def test_writer_tables_of_3_6_are_gone(self):
        write = read("references/write.md")
        for table in ("Split the third answer into small sentences", "**所以呢**", "Who is speaking", "Register the core words"):
            self.assertNotIn(table, write)

    def test_length_is_held_by_the_maximum_not_sentence_by_sentence(self):
        # 3.9 (the author, 2026-10-23): no rule that a revised sentence may not grow; a condition still goes in its own sentence.
        for rel in ("references/write.md", "references/5-review.md", "references/prompts.md"):
            text = read(rel)
            for gone in ("never makes a sentence longer", "keeps or shortens the sentence", "不比原句长"):
                self.assertNotIn(gone, text, rel)
        self.assertIn("Length is held by the configuration's maximum, not sentence by sentence", read("references/write.md"))
        self.assertIn("goes into a sentence of its own", read("references/5-review.md"))

    def test_exemplars_are_mature_writers_and_reach_the_editor(self):
        step3 = section(read("references/write.md"), "## Step 3", "## Step 4")
        self.assertIn("Never the account's own old articles", step3)
        self.assertIn("{{EXEMPLAR}}", read("references/prompts.md"))
        self.assertIn("动作十一｜和参照范文比", read("references/prompts.md"))


class PointerTests(unittest.TestCase):
    def test_every_reference_is_listed_in_the_main_file_and_exists(self):
        listed = set(re.findall(r"\| `references/([\w.-]+\.md)` \|", read("SKILL.md")))
        present = {p.name for p in REFERENCES.glob("*.md")}
        self.assertEqual(listed, present)

    def test_no_pointer_to_a_missing_reference(self):
        known = {p.name for p in REFERENCES.glob("*.md")}
        for path in doc_files() + [SKILL / "agents" / "openai.yaml", SKILL / "templates" / "config.example.yaml"]:
            for name in re.findall(r"references/([\w.-]+\.md)", path.read_text(encoding="utf-8")):
                self.assertIn(name, known, f"{path.name} points at missing references/{name}")

    def test_openai_prompt_is_one_sentence_pointing_at_the_main_file(self):
        prompt = read("agents/openai.yaml")
        self.assertIn("SKILL.md", prompt)
        self.assertLess(len(prompt.split("default_prompt:", 1)[1]), 400)

    def test_scripts_point_only_at_existing_references(self):
        known = {p.name for p in REFERENCES.glob("*.md")}
        for path in (SKILL / "scripts").glob("*.py"):
            for name in re.findall(r"references/([\w.-]+\.md)", path.read_text(encoding="utf-8")):
                self.assertIn(name, known, f"{path.name} points at missing references/{name}")

    def test_no_step_points_at_the_maintainers_files(self):
        for path in doc_files():
            if path.name in MAINTAINERS or path.name == "SKILL.md":
                continue
            text = path.read_text(encoding="utf-8")
            for name in MAINTAINERS:
                self.assertNotIn(name, text, path.name)


class TopicReferenceTests(unittest.TestCase):
    def test_topic_reference_carries_the_routes_and_the_source_families(self):
        text = read("references/1-topic.md")
        for route in range(1, 5):
            self.assertIn(f"Route {route}:", text)
        self.assertEqual(len(re.findall(r"^\| [1-4] ", text, re.M)), 4, "four source families")

    def test_someone_elses_article_is_a_seed_only(self):
        topic = read("references/1-topic.md")
        self.assertIn("### Someone else's article as the seed", topic)
        self.assertIn("never names the article or its author", topic)


class CleanSkillTests(unittest.TestCase):
    def test_removed_names_only_in_the_maintainers_files(self):
        for path in doc_files() + [SKILL / "agents" / "openai.yaml", SKILL / "templates" / "config.example.yaml"]:
            if path.name in MAINTAINERS:
                continue
            text = path.read_text(encoding="utf-8")
            for name in REMOVED_NAMES:
                self.assertNotIn(name, text, f"{path.name} still mentions {name!r}")

    def test_no_private_paths_in_the_skill(self):
        for path in SKILL.rglob("*"):
            if path.is_file() and path.suffix in (".md", ".yaml", ".py") and "tests" not in path.parts:
                self.assertNotIn("/Users/", path.read_text(encoding="utf-8"), str(path))

    def test_config_template_has_one_model_entry_per_role(self):
        models = read("templates/config.example.yaml").split("models:", 1)[1]
        for key in ("writer", "writer_fallback", "research", "hook_second", "fact_sheet_names", "editor", "reader", "expert", "fact_checker"):
            self.assertRegex(models, re.compile(rf"^  {key}:", re.M), f"models.{key}")
        for old in ("organizer", "counter", "structure_editor", "managing_editor", "facts_risk", "language", "seed_check"):
            self.assertNotRegex(models, re.compile(rf"^  {old}:", re.M), f"models.{old}")

    def test_config_template_names_the_exemplar_index_and_edit_pairs(self):
        text = read("templates/config.example.yaml")
        for key in ("exemplar_index", "exemplar_fallback", "edit_pairs_folder"):
            self.assertRegex(text, re.compile(rf"^{key}:", re.M))


if __name__ == "__main__":
    unittest.main()
