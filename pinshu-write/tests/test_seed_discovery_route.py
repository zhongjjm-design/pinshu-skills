"""Structure checks for the 3.1.0 route: one route, four stops (topic, the line, the opening, final), every reviewing role kept, hard gates, no dangling pointers.
These prove the documents are wired together, not that their topics or articles are good: that is judged only by
real forward tests."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
REFERENCES = SKILL / "references"
# Role and step names removed in 2.0.0; they may appear only in the maintainers' archive.
REMOVED_NAMES = ("wording editor", "judgment gate", "skeleton gate", "skeleton re-read", "cold reader", "cold-reader",
                 "five-step", "common-sense floor", "red team", "seed-discovery", "Approval 1", "approval 3",
                 # removed in 2.1.0
                 "editor-in-chief", "editor_in_chief", "Rules for every writer", "Style layers")
ROLES = ("Organizer", "Writer", "Counter", "Structure editor", "Managing editor", "Reader", "Expert", "Facts and risk",
         "Language and flow", "Good-article check", "After-revision read", "Seed check",
         "Attraction reader", "Originality check")
LEGACY = ("3-structure.md", "4-writing.md")


def read(rel):
    return (SKILL / rel).read_text(encoding="utf-8")


def doc_files():
    return [SKILL / "SKILL.md"] + sorted(REFERENCES.glob("*.md"))


class RouteTests(unittest.TestCase):
    def test_entry_table_routes_every_entry(self):
        text = read("SKILL.md")
        table = text.split("| The author brings | Enter at |", 1)[1].split("\n\n", 1)[0]
        self.assertRegex(table, r"\| Nothing[^|]*\| 1 Topic: scan, three topics, stop 1 \|")
        for row in ("| An idea, topic, link or article, any length | 2 Research, the author's words kept whole as the seed",
                    "| A line or a title | 3 The line", "| A draft to look at | 6 The read and the fact check",
                    "| Comments on a draft | Revision by size", "| The author's own hand edit of a draft | Edit pairs"):
            self.assertIn(row, table)

    def test_route_has_exactly_four_stops(self):
        text = read("SKILL.md")
        route = text.split("## The route", 1)[1].split("## The roles", 1)[0]
        stops = re.findall(r"^\|[^|]*\*\*Stop (\d)\*\*", route, re.M)
        self.assertEqual(stops, ["1", "2", "3", "4"])
        headings = re.findall(r"^## Stop (\d): (.+)$", read("references/stops.md"), re.M)
        self.assertEqual([h[0] for h in headings], ["1", "2", "3", "4"])
        self.assertEqual([h[1].split(" (")[0] for h in headings], ["topic", "the line", "the opening", "final"])

    def test_every_reviewing_role_is_on_the_route(self):
        main = read("SKILL.md").split("## The roles", 1)[1].split("## Rules that do not bend", 1)[0]
        self.assertEqual(len(re.findall(r"^\| [A-Z]", main, re.M)) - 1, 14)  # minus the header row; 3.3 added the attraction reader and the originality check
        review = read("references/5-review.md")
        for role in ROLES:
            self.assertIn(f"| {role} |", main)
            if role not in ("Organizer", "Writer"):
                self.assertIn(role, review)

    def test_hard_gates_are_on_the_route(self):
        route = read("SKILL.md").split("## The route", 1)[1].split("## The roles", 1)[0]
        self.assertIn("--length 2000-2500 --hard-max 2700", route)
        self.assertIn("One-sentence paragraphs in a row", route)

    def test_writer_brief_has_the_seed_whole_and_five_bottom_lines(self):
        write = read("references/write.md")
        brief = write.split("## The writer's brief", 1)[1].split("## The opening", 1)[0]
        bottom = brief.split("**Five bottom lines**", 1)[1].split("```text", 1)[1].split("```", 1)[0]
        self.assertEqual(re.findall(r"^(\d)\. ", bottom, re.M), ["1", "2", "3", "4", "5"])
        for must in ("The seed, whole and verbatim", "The line the author approved", "exemplars", "How the author edits",
                     "The material pack", "no rule book, no audit list, no per-section template, no sample sentences"):
            self.assertIn(must, brief)

    def test_line_is_not_four_boxes_and_titles_carry_news(self):
        write = read("references/write.md")
        line = write.split("## The line (stop 2)", 1)[1].split("## The writer's brief", 1)[0]
        self.assertIn("not four labelled boxes", line)
        self.assertIn("谁不知道", line)

    def test_revision_is_whole_sections_and_facts_are_hard_facts(self):
        review = read("references/5-review.md")
        self.assertIn("rewrites whole sections", review)
        self.assertIn("is not a fault", review)
        write = read("references/write.md")
        self.assertIn("## Review and revision", write)

    def test_organizer_reads_first_and_learns_from_edits(self):
        write = read("references/write.md")
        self.assertIn("**Read like a reader first.**", write)
        self.assertIn("## After 定稿: learn from the author's edits", write)
        self.assertIn("never from the account's old articles", write)

    def test_legacy_references_are_marked_off_the_route(self):
        main = read("SKILL.md").split("## References", 1)[1]
        for name in LEGACY:
            row = [line for line in main.splitlines() if f"`references/{name}`" in line][0]
            self.assertIn("2.x, off the route", row)
        route = read("SKILL.md").split("## The route", 1)[1].split("## The roles", 1)[0]
        for name in LEGACY:
            self.assertNotIn(name, route)


class PointerTests(unittest.TestCase):
    def test_every_reference_is_listed_in_the_main_file_and_exists(self):
        main = read("SKILL.md")
        listed = set(re.findall(r"\| `references/([\w.-]+\.md)` \|", main))
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

    def test_no_step_points_at_the_maintainers_archive(self):
        for path in doc_files():
            if path.name == "lessons.md":
                continue
            text = path.read_text(encoding="utf-8")
            if path.name == "SKILL.md":
                text = text.replace("| `references/lessons.md` |", "").replace("`references/lessons.md`, which only the maintainer reads", "")
            self.assertNotIn("lessons.md", text, path.name)


class TopicReferenceTests(unittest.TestCase):
    def test_topic_reference_carries_the_routes_and_the_source_families(self):
        text = read("references/1-topic.md")
        for route in range(1, 5):
            self.assertIn(f"Route {route}:", text)
        self.assertEqual(len(re.findall(r"^\| [1-4] ", text, re.M)), 4, "four source families")
        for word in ("source route", "Public source map", "Entry rule", "Stop 1 offers three topics", "S1, S2, S3"):
            self.assertIn(word.lower(), text.lower())

    def test_discovery_method_lives_in_one_place(self):
        self.assertIn("1-topic.md", read("references/stops.md"))
        for name in ("2-research-and-counter.md", "3-structure.md", "4-writing.md", "5-review.md"):
            self.assertNotIn("Public source map.", read(f"references/{name}"), name)


class CleanSkillTests(unittest.TestCase):
    def test_removed_role_names_are_not_steps_anywhere_but_the_archive(self):
        for path in doc_files() + [SKILL / "agents" / "openai.yaml", SKILL / "templates" / "config.example.yaml"]:
            if path.name == "lessons.md":
                continue
            text = path.read_text(encoding="utf-8").lower()
            for name in REMOVED_NAMES:
                self.assertNotIn(name.lower(), text, f"{path.name} still mentions {name!r}")

    def test_no_private_paths_in_the_skill(self):
        for path in SKILL.rglob("*"):
            if path.is_file() and path.suffix in (".md", ".yaml", ".py") and "tests" not in path.parts:
                self.assertNotIn("/Users/", path.read_text(encoding="utf-8"), str(path))

    def test_config_template_names_the_exemplar_index(self):
        text = read("templates/config.example.yaml")
        self.assertRegex(text, re.compile(r"^exemplar_index:", re.M))
        self.assertRegex(text, re.compile(r"^exemplar_fallback:", re.M))
        self.assertRegex(text, re.compile(r"^edit_pairs_folder:", re.M))
        self.assertTrue((SKILL / "templates" / "exemplar-index.example.md").is_file())

    def test_config_template_has_one_model_entry_per_role(self):
        text = read("templates/config.example.yaml")
        models = text.split("models:", 1)[1]
        for key in ("organizer", "research", "writer", "second_writer", "counter", "structure_editor", "managing_editor",
                    "reader", "expert", "facts_risk", "language", "seed_check"):
            self.assertRegex(models, re.compile(rf"^  {key}:", re.M), f"models.{key}")
        for old in ("wording_editor", "layperson_reader", "target_reader", "fact_checker", "reviewers", "editor_in_chief"):
            self.assertNotIn(old, models)


if __name__ == "__main__":
    unittest.main()


class HookFirstTests(unittest.TestCase):
    """3.3 (2026-10-19): reach comes first; only facts and copying force a change."""

    def test_hook_is_chosen_before_the_line(self):
        write = read("references/write.md")
        self.assertLess(write.index("## The hook (before the line, stop 2)"), write.index("## The line (stop 2)"))
        hook = write.split("## The hook", 1)[1].split("## The line (stop 2)", 1)[0]
        for must in ("One sentence the whole piece says", "Candidates from two vendors", "The author picks", "never replaced without asking"):
            self.assertIn(must, hook)
        self.assertIn("0. **The hook first**", read("references/stops.md"))

    def test_writer_is_told_what_grips(self):
        brief = read("references/write.md").split("## The writer's brief", 1)[1].split("## The opening", 1)[0]
        self.assertIn("让人忍不住点开、看完、转出去", brief)
        self.assertIn("The title and opening the author chose", brief)

    def test_only_facts_and_copying_force_a_change(self):
        review = read("references/5-review.md")
        self.assertIn("Only hard facts and copying force a change", review)
        self.assertIn("锋利的话、冲突、钩子一样不许磨软", review)
        self.assertIn("Reach comes first; only facts and copying force a change.", read("SKILL.md"))
        self.assertIn("three sharpest lines beside the previous version", read("references/write.md"))

    def test_new_prompts_exist(self):
        prompts = read("references/prompts.md")
        for h in ("## 13. Attraction reader", "## 14. Originality check", "## 15. Title and opening candidates"):
            self.assertIn(h, prompts)

    def test_someone_elses_article_is_a_seed_only(self):
        topic = read("references/1-topic.md")
        self.assertIn("### Someone else's article as the seed", topic)
        self.assertIn("never names the article or its author", topic)
        self.assertNotIn("resembling a hit earns nothing", read("references/3-structure.md"))
