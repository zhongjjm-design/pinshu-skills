#!/usr/bin/env python3
"""Legacy backend validator and route regression tests (not content-quality acceptance)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parents[0]
VALIDATOR = SKILL_DIR / "scripts" / "validate-propagation-assets.py"
RESOLVER = SKILL_DIR / "scripts" / "resolve-content-route.py"
COURSE_VALIDATOR = SKILL_DIR.parents[0] / "pinshu-course" / "scripts" / "validate-course-markdown.py"


class ContentAssetsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.md"
        self.source.write_text("# 一场访谈\n\n增长不是多发内容，而是让同一个判断被更多真实证据支撑。\n", encoding="utf-8")
        self.other_source = self.root / "other.md"
        self.other_source.write_text("# 另一个来源\n\n另一条可定位内容。\n", encoding="utf-8")
        self.course_map = self.root / "course-map.md"
        self.course_map.write_text("# 课程地图\n\n计划课次全部验收。\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def item(self) -> dict:
        return {
            "asset_id": "INTERVIEW-001",
            "candidate_type": "quote",
            "expression_identity": "lecturer_quote",
            "content": "增长不是多发内容，而是让同一个判断被更多真实证据支撑。",
            "source_excerpt": "增长不是多发内容，而是让同一个判断被更多真实证据支撑。",
            "source_anchor": {"document": "source.md", "section": "一场访谈"},
            "context": "受访者讨论内容增长时的判断。",
            "value_reason": "可用于区分数量增长与证据积累。",
            "boundary": "不能据此否定必要的发布频率。",
            "verification_status": "not_required",
            "risk_level": "R1",
            "status": "captured",
        }

    def payload(self) -> dict:
        return {
            "schema_version": "1.0",
            "asset_type": "propagation_candidates",
            "status": "captured",
            "scope_type": "single",
            "coverage_status": "complete",
            "source_documents": ["source.md"],
            "items": [self.item()],
        }

    def write_payload(self, payload: dict, name: str = "registry.json") -> Path:
        path = self.root / name
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def run_validator(self, payload: dict) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(VALIDATOR), str(self.write_payload(payload))], text=True, capture_output=True)

    def run_full_delivery(self, backend: dict, package: dict) -> subprocess.CompletedProcess[str]:
        for number in range(5):
            sibling = self.root / f"{number:02d}_既有栏目"
            sibling.mkdir(exist_ok=True)
            (sibling / "入口.md").write_text("# 既有栏目\n\n项目正式栏目。\n", encoding="utf-8")
        source_registry = self.write_payload(backend, "source-registry.json")
        package_manifest = self.write_payload(package, "content-package.json")
        return subprocess.run([
            sys.executable,
            str(VALIDATOR),
            "--profile", "full-delivery",
            "--project-root", str(self.root),
            str(source_registry),
            str(package_manifest),
        ], text=True, capture_output=True)

    def refresh_package_approval(self, package: dict) -> None:
        package["semantic_review"]["content_unit_ids"] = [
            unit["asset_id"] for unit in package["content_units"]
        ]
        digest_map: dict[str, str] = {}
        for deliverable in package["deliverables"]:
            target = self.root / deliverable["path"]
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            deliverable["file_freeze"]["file_sha256"] = digest
            digest_map[deliverable["deliverable_id"]] = digest
        package["semantic_review"]["deliverable_sha256"] = digest_map

    def add_restricted_record(
        self,
        backend: dict,
        package: dict,
        source_id: str = "RESTRICTED-001",
        raw_claim: str = "某项受限收益数字为12345元。",
    ) -> None:
        restricted_item = dict(self.item())
        restricted_item.update({
            "asset_id": source_id,
            "candidate_type": "data",
            "expression_identity": "editorial_synthesis",
            "content": raw_claim,
            "context": "该数字只有讲师口述，尚无独立凭证。",
            "value_reason": "保留核验线索。",
            "boundary": "完成证据核验和人工审批前不得使用。",
            "risk_level": "R3",
            "verification_status": "pending",
            "status": "captured",
        })
        restricted_item.pop("source_excerpt", None)
        backend["items"].append(restricted_item)
        self.source.write_text(
            self.source.read_text(encoding="utf-8") + f"\n{raw_claim}\n",
            encoding="utf-8",
        )
        package["considered_source_ids"].append(source_id)
        restricted_path = self.root / "05_内容资产" / "05_待核验与禁用.md"
        restricted_content = f"待核验：{raw_claim}在完成证据核验和人工审批前禁用。"
        restricted_path.write_text(
            f"# 待核验与禁用\n\n{restricted_content}\n\n解除条件：完成证据核验和人工审批。\n",
            encoding="utf-8",
        )
        package["has_restricted_content"] = True
        package["deliverables"].append({
            "deliverable_id": "RES-001",
            "asset_role": "restricted",
            "title": "待核验与禁用",
            "path": "05_内容资产/05_待核验与禁用.md",
            "use_status": "needs_verification",
            "next_action": "完成证据核验和人工审批后再决定是否启用",
            "file_freeze": {
                "frozen_by": "producer-agent",
                "frozen_at": "2026-09-26",
                "file_sha256": "pending-refresh",
            },
        })
        package["content_units"].append({
            "asset_id": "PUBLIC-RESTRICTED-001",
            "deliverable_id": "RES-001",
            "source_asset_ids": [source_id],
            "source_support": [{
                "source_asset_id": source_id,
                "support_excerpt": raw_claim,
                "relationship": "direct_support",
                "source_anchor": {"document": "source.md", "section": "一场访谈"},
            }],
            "candidate_type": "data",
            "expression_identity": "editorial_synthesis",
            "content": restricted_content,
            "source_anchor": {"document": "source.md", "section": "一场访谈"},
            "context": "该判断涉及高风险内容，暂不进入可用区。",
            "value_reason": "保留核验线索，同时防止误用。",
            "boundary": "完成证据核验和人工审批前不得使用。",
            "verification_status": "pending",
            "risk_level": "R3",
            "status": "captured",
        })
        self.refresh_package_approval(package)

    def assert_fails(self, payload: dict, message: str) -> None:
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(message, result.stdout)

    def promoted_mother(self, scope: str = "single") -> dict:
        payload = self.payload()
        payload.update({
            "asset_type": "propagation_mother_asset",
            "status": "validated",
            "scope_type": scope,
            "coverage_status": "complete",
        })
        payload["items"][0]["status"] = "promoted"
        if scope == "course":
            payload.update({
                "course_complete": True,
                "source_documents": ["source.md", "course-map.md"],
                "completion_evidence": {
                    "kind": "course_map",
                    "reference": "course-map.md#完成状态",
                    "source_excerpt": "计划课次全部验收。",
                    "completion_assertion": "course_complete",
                    "verified_at": "2026-09-26",
                    "reviewed_by": "reviewer-id",
                    "review_evidence": "review-record-001",
                },
            })
        return payload

    def handoff(self, delivery: str = "handoff_pending") -> dict:
        payload = self.promoted_mother()
        payload.update({"asset_type": "content_handoff", "status": "handoff_ready"})
        payload["route"] = {
            "role": "content_workflow_handoff",
            "route_resolution_status": "resolved",
            "delivery_status": delivery,
            "destination": "workflow:writer",
        }
        return payload

    def content_package(self, profile: str = "full") -> dict:
        package_root = self.root / "05_内容资产"
        files = {
            "navigation": package_root / "00_内容资产导航.md",
            "ready_to_use": package_root / "01_可直接使用" / "01_观点与判断.md",
            "topic_library": package_root / "02_选题库" / "01_优先选题.md",
            "production_brief": package_root / "03_待生产" / "CT-001_内容任务卡.md",
        }
        statuses = {
            "navigation": "ready_to_browse",
            "ready_to_use": "ready_to_copy",
            "topic_library": "ready_for_topic_library",
            "production_brief": "ready_for_production",
        }
        public_content = {
            "ready_to_use": "增长不是多发内容，而是让同一个判断被更多真实证据支撑。",
            "topic_library": "选题：为什么内容增长不是简单增加发布数量？",
            "production_brief": "任务卡：面向内容创作者解释数量增长与证据积累的区别。",
        }
        for role, path in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            body = public_content.get(role, "从可直接使用资产、优先选题和任务卡进入下一步工作。")
            path.write_text(f"# {role}\n\n{body}\n\n下一步按本页说明继续使用。\n", encoding="utf-8")
        deliverables = [
            {
                "deliverable_id": f"DEL-{number:03d}",
                "asset_role": role,
                "title": path.stem,
                "path": str(path.relative_to(self.root)),
                "use_status": statuses[role],
                "next_action": "按该资产标明的用途继续使用",
                "file_freeze": {
                    "frozen_by": "producer-agent",
                    "frozen_at": "2026-09-26",
                    "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                },
            }
            for number, (role, path) in enumerate(files.items(), 1)
        ]
        deliverable_id_by_role = {item["asset_role"]: item["deliverable_id"] for item in deliverables}
        candidate_types = {
            "ready_to_use": "viewpoint",
            "topic_library": "topic",
            "production_brief": "method",
        }
        content_units = []
        for number, role in enumerate(("ready_to_use", "topic_library", "production_brief"), 1):
            unit = {
                "asset_id": f"PUBLIC-{number:03d}",
                "deliverable_id": deliverable_id_by_role[role],
                "source_asset_ids": ["INTERVIEW-001"],
                "source_support": [{
                    "source_asset_id": "INTERVIEW-001",
                    "support_excerpt": "增长不是多发内容，而是让同一个判断被更多真实证据支撑。",
                    "relationship": "direct_support",
                    "source_anchor": {"document": "source.md", "section": "一场访谈"},
                }],
                "candidate_type": candidate_types[role],
                "expression_identity": "editorial_synthesis",
                "content": public_content[role],
                "source_anchor": {"document": "source.md", "section": "一场访谈"},
                "context": "基于访谈原话整理成用户可直接使用的内容。",
                "value_reason": "可以直接复制、入选题库或交给下游生产。",
                "boundary": "不能据此否定必要的发布频率。",
                "verification_status": "not_required",
                "risk_level": "R0",
                "status": "promoted",
            }
            if role == "topic_library":
                unit["topic_fields"] = {
                    "title": "为什么内容增长不是简单增加发布数量？",
                    "target_reader": "正在提高内容发布频率的创作者",
                    "core_judgment": "内容增长还需要真实证据积累",
                    "rationale": "纠正常见的数量替代质量误区",
                    "safe_evidence": "访谈中的原始判断",
                    "recommended_form": "公众号文章",
                    "current_status": "ready",
                    "next_action": "进入选题库并补充个人案例",
                }
            content_units.append(unit)
        review_record = self.root / "semantic-review.md"
        approval_excerpt = "独立复核者已检查完整前台主张、来源身份、风险继承、第一人称归属和选题合同，同意该版本入库。"
        review_record.write_text(f"# 语义复核\n\n{approval_excerpt}\n", encoding="utf-8")
        payload = {
            "schema_version": "1.1",
            "asset_type": "content_asset_package",
            "status": "semantic_approved",
            "producer": "producer-agent",
            "scope_type": "single",
            "coverage_status": "complete",
            "delivery_profile": profile,
            "requested_roles": list(files),
            "package_mode": "created",
            "package_root": "05_内容资产",
            "has_restricted_content": False,
            "considered_source_ids": ["INTERVIEW-001"],
            "source_documents": ["source.md"],
            "deliverables": deliverables,
            "content_units": content_units,
            "semantic_review": {
                "status": "approved",
                "reviewer": "independent-reviewer",
                "reviewed_at": "2026-09-26",
                "review_scope": [
                    "complete_visible_claims",
                    "source_identity",
                    "risk_inheritance",
                    "first_person_ownership",
                    "topic_contract",
                ],
                "content_unit_ids": [unit["asset_id"] for unit in content_units],
                "deliverable_sha256": {
                    item["deliverable_id"]: item["file_freeze"]["file_sha256"]
                    for item in deliverables
                },
                "evidence": {
                    "kind": "file",
                    "reference": "semantic-review.md",
                    "approval_excerpt": approval_excerpt,
                    "readback_verified": True,
                },
            },
        }
        return payload

    def test_valid_candidate_passes(self) -> None:
        result = self.run_validator(self.payload())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_valid_single_mother_passes(self) -> None:
        result = self.run_validator(self.promoted_mother())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_valid_complete_course_mother_passes(self) -> None:
        result = self.run_validator(self.promoted_mother("course"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_valid_full_content_asset_package_passes(self) -> None:
        result = self.run_validator(self.content_package())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_full_delivery_profile_requires_usable_content_package(self) -> None:
        source_registry = self.write_payload(self.payload(), "source-registry.json")
        result = subprocess.run([
            sys.executable,
            str(VALIDATOR),
            "--profile", "full-delivery",
            "--project-root", str(self.root),
            str(source_registry),
        ], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires at least one valid semantic_approved content_asset_package", result.stdout)

    def test_full_delivery_profile_passes_real_frontend_and_backend_chain(self) -> None:
        for number in range(5):
            sibling = self.root / f"{number:02d}_既有栏目"
            sibling.mkdir()
            (sibling / "入口.md").write_text("# 既有栏目\n\n这里是项目现有正式栏目。\n", encoding="utf-8")
        source_registry = self.write_payload(self.payload(), "source-registry.json")
        package_manifest = self.write_payload(self.content_package(), "content-package.json")
        result = subprocess.run([
            sys.executable,
            str(VALIDATOR),
            "--profile", "full-delivery",
            "--project-root", str(self.root),
            str(source_registry),
            str(package_manifest),
        ], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS full-delivery", result.stdout)

    def test_full_delivery_profile_rejects_requested_subset_package(self) -> None:
        for number in range(5):
            sibling = self.root / f"{number:02d}_既有栏目"
            sibling.mkdir()
            (sibling / "入口.md").write_text("# 既有栏目\n\n项目正式栏目。\n", encoding="utf-8")
        source_registry = self.write_payload(self.payload(), "source-registry.json")
        package_manifest = self.write_payload(
            self.content_package("requested_subset"), "content-package.json"
        )
        result = subprocess.run([
            sys.executable, str(VALIDATOR),
            "--profile", "full-delivery",
            "--project-root", str(self.root),
            str(source_registry), str(package_manifest),
        ], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires at least one valid semantic_approved content_asset_package", result.stdout)

    def test_full_delivery_profile_accepts_explicit_reused_entry(self) -> None:
        payload = self.content_package()
        old_root = self.root / "05_内容资产"
        reused_root = self.root / "03_内容资产"
        old_root.rename(reused_root)
        payload["package_mode"] = "reused"
        payload["package_root"] = "03_内容资产"
        for deliverable in payload["deliverables"]:
            deliverable["path"] = deliverable["path"].replace("05_内容资产", "03_内容资产", 1)
        later = self.root / "06_后来栏目"
        later.mkdir()
        (later / "入口.md").write_text("# 后来栏目\n\n这是复用入口之后新增的正式栏目。\n", encoding="utf-8")
        source_registry = self.write_payload(self.payload(), "source-registry.json")
        package_manifest = self.write_payload(payload, "content-package.json")
        result = subprocess.run([
            sys.executable, str(VALIDATOR),
            "--profile", "full-delivery",
            "--project-root", str(self.root),
            str(source_registry), str(package_manifest),
        ], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_full_delivery_requires_pending_r3_in_restricted_deliverable(self) -> None:
        for number in range(5):
            sibling = self.root / f"{number:02d}_既有栏目"
            sibling.mkdir()
            (sibling / "入口.md").write_text("# 既有栏目\n\n项目正式栏目。\n", encoding="utf-8")
        backend = self.payload()
        backend["items"][0].update({
            "risk_level": "R3",
            "verification_status": "pending",
            "status": "captured",
        })
        source_registry = self.write_payload(backend, "source-registry.json")
        package_manifest = self.write_payload(self.content_package(), "content-package.json")
        result = subprocess.run([
            sys.executable, str(VALIDATOR),
            "--profile", "full-delivery",
            "--project-root", str(self.root),
            str(source_registry), str(package_manifest),
        ], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must set has_restricted_content=true", result.stdout)
        self.assertIn("restricted deliverable does not cover considered active restricted items", result.stdout)

    def test_full_delivery_passes_when_pending_r3_is_explicitly_restricted(self) -> None:
        for number in range(5):
            sibling = self.root / f"{number:02d}_既有栏目"
            sibling.mkdir()
            (sibling / "入口.md").write_text("# 既有栏目\n\n项目正式栏目。\n", encoding="utf-8")
        backend = self.payload()
        restricted_item = dict(self.item())
        restricted_item.update({
            "asset_id": "RESTRICTED-001",
            "candidate_type": "data",
            "expression_identity": "editorial_synthesis",
            "content": "某项受限收益数字为12345元。",
            "context": "该数字只有讲师口述，尚无独立凭证。",
            "value_reason": "保留核验线索。",
            "boundary": "完成证据核验和人工审批前不得使用。",
            "risk_level": "R3",
            "verification_status": "pending",
            "status": "captured",
        })
        restricted_item.pop("source_excerpt", None)
        backend["items"].append(restricted_item)
        self.source.write_text(
            self.source.read_text(encoding="utf-8") + "\n某项受限收益数字为12345元。\n",
            encoding="utf-8",
        )
        package = self.content_package()
        package["considered_source_ids"].append("RESTRICTED-001")
        restricted_path = self.root / "05_内容资产" / "05_待核验与禁用.md"
        restricted_content = "待核验：某项受限收益数字为12345元，在完成证据核验和人工审批前禁用。"
        restricted_path.write_text(
            f"# 待核验与禁用\n\n{restricted_content}\n\n解除条件：完成证据核验和人工审批。\n",
            encoding="utf-8",
        )
        restricted_digest = hashlib.sha256(restricted_path.read_bytes()).hexdigest()
        package["has_restricted_content"] = True
        package["deliverables"].append({
            "deliverable_id": "RES-001",
            "asset_role": "restricted",
            "title": "待核验与禁用",
            "path": "05_内容资产/05_待核验与禁用.md",
            "use_status": "needs_verification",
            "next_action": "完成证据核验和人工审批后再决定是否启用",
            "file_freeze": {
                "frozen_by": "producer-agent",
                "frozen_at": "2026-09-26",
                "file_sha256": restricted_digest,
            },
        })
        package["content_units"].append({
            "asset_id": "PUBLIC-RESTRICTED-001",
            "deliverable_id": "RES-001",
            "source_asset_ids": ["RESTRICTED-001"],
            "source_support": [{
                "source_asset_id": "RESTRICTED-001",
                "support_excerpt": "某项受限收益数字为12345元。",
                "relationship": "direct_support",
                "source_anchor": {"document": "source.md", "section": "一场访谈"},
            }],
            "candidate_type": "data",
            "expression_identity": "editorial_synthesis",
            "content": restricted_content,
            "source_anchor": {"document": "source.md", "section": "一场访谈"},
            "context": "该判断涉及高风险内容，暂不进入可用区。",
            "value_reason": "保留核验线索，同时防止误用。",
            "boundary": "完成证据核验和人工审批前不得使用。",
            "verification_status": "pending",
            "risk_level": "R3",
            "status": "captured",
        })
        package["semantic_review"]["content_unit_ids"].append("PUBLIC-RESTRICTED-001")
        package["semantic_review"]["deliverable_sha256"]["RES-001"] = restricted_digest
        source_registry = self.write_payload(backend, "source-registry.json")
        package_manifest = self.write_payload(package, "content-package.json")
        result = subprocess.run([
            sys.executable, str(VALIDATOR),
            "--profile", "full-delivery",
            "--project-root", str(self.root),
            str(source_registry), str(package_manifest),
        ], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_full_delivery_profile_rejects_wrong_next_sibling_number(self) -> None:
        sibling = self.root / "06_既有栏目"
        sibling.mkdir()
        (sibling / "入口.md").write_text("# 既有栏目\n\n该栏目编号高于内容资产目录。\n", encoding="utf-8")
        source_registry = self.write_payload(self.payload(), "source-registry.json")
        package_manifest = self.write_payload(self.content_package(), "content-package.json")
        result = subprocess.run([
            sys.executable,
            str(VALIDATOR),
            "--profile", "full-delivery",
            "--project-root", str(self.root),
            str(source_registry),
            str(package_manifest),
        ], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must use next sibling number 07, got 05", result.stdout)

    def test_full_delivery_profile_rejects_duplicate_numbered_asset_entry(self) -> None:
        duplicate = self.root / "04_传播资产"
        duplicate.mkdir()
        (duplicate / "入口.md").write_text("# 旧入口\n\n这是另一个编号化传播资产入口。\n", encoding="utf-8")
        source_registry = self.write_payload(self.payload(), "source-registry.json")
        package_manifest = self.write_payload(self.content_package(), "content-package.json")
        result = subprocess.run([
            sys.executable,
            str(VALIDATOR),
            "--profile", "full-delivery",
            "--project-root", str(self.root),
            str(source_registry),
            str(package_manifest),
        ], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("another numbered content/propagation asset entry", result.stdout)

    def test_content_asset_package_requires_numbered_directory(self) -> None:
        payload = self.content_package()
        old_root = self.root / "05_内容资产"
        new_root = self.root / "内容资产"
        old_root.rename(new_root)
        payload["package_root"] = "内容资产"
        for deliverable in payload["deliverables"]:
            deliverable["path"] = deliverable["path"].replace("05_内容资产", "内容资产", 1)
        self.assert_fails(payload, "must use a two-digit XX_内容资产 name")

    def test_full_content_asset_package_requires_user_facing_roles(self) -> None:
        payload = self.content_package()
        payload["deliverables"] = [
            item for item in payload["deliverables"] if item["asset_role"] != "production_brief"
        ]
        self.assert_fails(payload, "missing requested deliverable roles: production_brief")

    def test_content_asset_package_rejects_json_process_files(self) -> None:
        payload = self.content_package()
        process_file = self.root / "05_内容资产" / "候选注册表.json"
        process_file.write_text("{}", encoding="utf-8")
        self.assert_fails(payload, "contains process file: 候选注册表.json")

    def test_content_asset_package_rejects_build_script(self) -> None:
        payload = self.content_package()
        process_file = self.root / "05_内容资产" / "build.py"
        process_file.write_text("print('internal build')\n", encoding="utf-8")
        self.assert_fails(payload, "contains process file: build.py")

    def test_content_asset_package_rejects_any_unregistered_file(self) -> None:
        payload = self.content_package()
        extra_file = self.root / "05_内容资产" / "generate-assets.js"
        extra_file.write_text("console.log('internal build')\n", encoding="utf-8")
        self.assert_fails(payload, "contains unregistered file: generate-assets.js")

    def test_content_asset_package_rejects_symlinked_directory(self) -> None:
        payload = self.content_package()
        external = self.root / "external-process-files"
        external.mkdir()
        (external / "hidden-build.js").write_text("console.log('hidden')\n", encoding="utf-8")
        linked = self.root / "05_内容资产" / "附加材料"
        linked.symlink_to(external, target_is_directory=True)
        self.assert_fails(payload, "must not contain symlinks: 附加材料")

    def test_content_asset_package_rejects_symlinked_package_root(self) -> None:
        payload = self.content_package()
        package_link = self.root / "05_内容资产"
        real_package = self.root / "real-content-package"
        package_link.rename(real_package)
        package_link.symlink_to(real_package, target_is_directory=True)
        self.assert_fails(payload, "package_root must not be a symlink")

    def test_exact_file_review_digest_rejects_unmapped_appended_claim(self) -> None:
        payload = self.content_package()
        ready_file = self.root / payload["deliverables"][1]["path"]
        ready_file.write_text(
            ready_file.read_text(encoding="utf-8") + "\n这种偏方一定能治愈癌症。\n",
            encoding="utf-8",
        )
        self.assert_fails(payload, "file_sha256 does not match the frozen file")

    def test_content_asset_package_rejects_process_markdown(self) -> None:
        payload = self.content_package()
        process_file = self.root / "05_内容资产" / "执行日志.md"
        process_file.write_text("# 执行日志\n\n这里记录内部执行过程，不是用户内容资产。\n", encoding="utf-8")
        self.assert_fails(payload, "contains process file: 执行日志.md")

    def test_content_asset_deliverable_must_stay_inside_package(self) -> None:
        payload = self.content_package()
        outside = self.root / "outside.md"
        outside.write_text("# 外部文件\n\n这份文件虽然存在，但不在编号化内容资产目录内。\n", encoding="utf-8")
        payload["deliverables"][0]["path"] = "outside.md"
        self.assert_fails(payload, "path must stay inside package_root")

    def test_content_asset_role_and_use_status_must_match(self) -> None:
        payload = self.content_package()
        payload["deliverables"][1]["use_status"] = "ready_for_topic_library"
        self.assert_fails(payload, "is incompatible with role ready_to_use")

    def test_process_record_root_must_stay_outside_content_assets(self) -> None:
        payload = self.content_package()
        payload["process_record_root"] = "05_内容资产/生产记录"
        self.assert_fails(payload, "process_record_root must stay outside package_root")

    def test_content_asset_package_rejects_empty_directory(self) -> None:
        payload = self.content_package()
        (self.root / "05_内容资产" / "04_可拆分内容组件").mkdir()
        self.assert_fails(payload, "contains empty directory")

    def test_content_asset_role_must_use_its_frontend_location(self) -> None:
        payload = self.content_package()
        deliverable = next(item for item in payload["deliverables"] if item["asset_role"] == "ready_to_use")
        old_path = self.root / deliverable["path"]
        new_path = self.root / "05_内容资产" / "杂项" / "观点.md"
        new_path.parent.mkdir()
        old_path.replace(new_path)
        deliverable["path"] = str(new_path.relative_to(self.root))
        self.assert_fails(payload, "path does not match the required location for role ready_to_use")

    def test_content_unit_must_appear_in_user_facing_file(self) -> None:
        payload = self.content_package()
        payload["content_units"][0]["content"] = "最终文件里并不存在的危险替换内容。"
        self.assert_fails(payload, "content is not present in its user-facing deliverable")

    def test_unverified_r3_cannot_enter_ready_to_use_deliverable(self) -> None:
        payload = self.content_package()
        unit = payload["content_units"][0]
        unit.update({
            "content": "这种偏方一定能治愈癌症。",
            "risk_level": "R3",
            "verification_status": "pending",
        })
        ready_file = self.root / payload["deliverables"][1]["path"]
        ready_file.write_text(ready_file.read_text(encoding="utf-8") + "\n这种偏方一定能治愈癌症。\n", encoding="utf-8")
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot enter a promoted or user-facing asset before verification", result.stdout)
        self.assertIn("structured human_review", result.stdout)

    def test_semantic_approval_requires_distinct_reviewer(self) -> None:
        payload = self.content_package()
        payload["semantic_review"]["reviewer"] = payload["producer"]
        self.assert_fails(payload, "semantic_review reviewer must differ from producer")

    def test_polished_lecturer_quote_is_rejected(self) -> None:
        payload = self.payload()
        payload["items"][0]["content"] = "增长不只是多发内容，而是持续积累真实证据。"
        self.assert_fails(payload, "lecturer_quote content must match source_excerpt verbatim")

    def test_first_person_experience_requires_verified_identity(self) -> None:
        payload = self.content_package()
        unit = payload["content_units"][0]
        unit["content"] = "我去年发过一百篇内容，所以我最清楚数量并不等于增长。"
        ready_file = self.root / payload["deliverables"][1]["path"]
        ready_file.write_text(
            ready_file.read_text(encoding="utf-8") + f"\n{unit['content']}\n",
            encoding="utf-8",
        )
        self.refresh_package_approval(payload)
        self.assert_fails(payload, "first-person experience requires lecturer_quote or verified user_extension identity")

    def test_topic_unit_requires_complete_topic_fields(self) -> None:
        payload = self.content_package()
        topic = next(unit for unit in payload["content_units"] if unit["candidate_type"] == "topic")
        del topic["topic_fields"]["target_reader"]
        self.assert_fails(payload, "topic_fields missing: target_reader")

    def test_source_anchor_section_must_be_an_exact_heading(self) -> None:
        payload = self.payload()
        payload["items"][0]["source_anchor"]["section"] = "不存在的小节"
        self.assert_fails(payload, "source_anchor.section is not an exact Markdown heading")

    def test_quote_must_be_inside_declared_source_section(self) -> None:
        self.source.write_text(
            "# 一场访谈\n\n本节没有目标原话。\n\n# 第二部分\n\n增长不是多发内容，而是让同一个判断被更多真实证据支撑。\n",
            encoding="utf-8",
        )
        self.assert_fails(self.payload(), "source_excerpt not found inside declared source section")

    def test_source_support_requires_direct_source_readback(self) -> None:
        payload = self.content_package()
        support = payload["content_units"][0]["source_support"][0]
        support["support_excerpt"] = "来源中不存在的支持片段"
        self.assert_fails(payload, "support_excerpt not found inside declared source section")

    def test_contrast_source_cannot_be_the_only_support(self) -> None:
        payload = self.content_package()
        payload["content_units"][0]["source_support"][0]["relationship"] = "contrast"
        self.assert_fails(payload, "requires at least one direct_support source")

    def test_source_support_anchor_must_match_referenced_item(self) -> None:
        backend = self.payload()
        other = dict(self.item())
        other.update({
            "asset_id": "OTHER-001",
            "content": "另一条可定位内容。",
            "source_excerpt": "另一条可定位内容。",
            "source_anchor": {"document": "other.md", "section": "另一个来源"},
        })
        backend["source_documents"].append("other.md")
        backend["items"].append(other)
        package = self.content_package()
        unit = package["content_units"][0]
        unit["source_asset_ids"] = ["OTHER-001"]
        unit["source_support"] = [{
            "source_asset_id": "OTHER-001",
            "support_excerpt": "另一条可定位内容。",
            "relationship": "direct_support",
            "source_anchor": {"document": "source.md", "section": "一场访谈"},
        }]
        self.source.write_text(
            self.source.read_text(encoding="utf-8") + "\n另一条可定位内容。\n",
            encoding="utf-8",
        )
        package["considered_source_ids"].append("OTHER-001")
        result = self.run_full_delivery(backend, package)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source_support anchor does not match source item OTHER-001", result.stdout)

    def test_restricted_listing_cannot_launder_public_source_reference(self) -> None:
        backend = self.payload()
        package = self.content_package()
        raw_claim = "某项受限收益数字为12345元。"
        self.add_restricted_record(backend, package, raw_claim=raw_claim)
        public_unit = package["content_units"][0]
        public_unit["source_asset_ids"] = ["RESTRICTED-001"]
        public_unit["source_support"] = [{
            "source_asset_id": "RESTRICTED-001",
            "support_excerpt": raw_claim,
            "relationship": "direct_support",
            "source_anchor": {"document": "source.md", "section": "一场访谈"},
        }]
        result = self.run_full_delivery(backend, package)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cites active restricted source RESTRICTED-001", result.stdout)

    def test_raw_restricted_claim_cannot_hide_in_topic_warning(self) -> None:
        backend = self.payload()
        package = self.content_package()
        raw_claim = "某项受限收益数字为12345元。"
        self.add_restricted_record(backend, package, raw_claim=raw_claim)
        topic_deliverable = next(
            item for item in package["deliverables"] if item["asset_role"] == "topic_library"
        )
        topic_file = self.root / topic_deliverable["path"]
        topic_file.write_text(
            topic_file.read_text(encoding="utf-8")
            + f"\n\n## 卡点（待核验，不得使用）\n\n{raw_claim}\n",
            encoding="utf-8",
        )
        self.refresh_package_approval(package)
        result = self.run_full_delivery(backend, package)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("raw active restricted claim from RESTRICTED-001", result.stdout)

    def test_safe_derivative_can_support_public_units(self) -> None:
        backend = self.payload()
        restricted = backend["items"][0]
        restricted.update({
            "asset_id": "RESTRICTED-001",
            "candidate_type": "data",
            "expression_identity": "editorial_synthesis",
            "content": "某项受限收益数字为12345元。",
            "context": "该数字只有讲师口述。",
            "value_reason": "保留核验线索。",
            "boundary": "完成核验前不得使用。",
            "risk_level": "R3",
            "verification_status": "pending",
            "status": "captured",
        })
        restricted.pop("source_excerpt", None)
        derivative_evidence = self.root / "derivative-review.md"
        approval_excerpt = "复核者确认安全派生只保留内容增长需要证据积累的判断。"
        derivative_evidence.write_text(f"# 派生复核\n\n{approval_excerpt}\n", encoding="utf-8")
        derivative = self.item()
        derivative.update({
            "asset_id": "INTERVIEW-001",
            "candidate_type": "viewpoint",
            "expression_identity": "editorial_synthesis",
            "status": "promoted",
            "derived_from_source_ids": ["RESTRICTED-001"],
            "derivative_type": "safe_derivative",
            "removed_claims": ["具体收益数字和结果承诺"],
            "risk_reduction_reason": "新主张不再包含收益数字或结果承诺。",
            "derivative_review": {
                "status": "approved",
                "reviewer": "independent-reviewer",
                "reviewed_at": "2026-09-26",
                "evidence": {
                    "kind": "file",
                    "reference": "derivative-review.md",
                    "approval_excerpt": approval_excerpt,
                    "readback_verified": True,
                },
            },
        })
        backend["items"] = [restricted, derivative]
        package = self.content_package()
        result = self.run_full_delivery(backend, package)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_valid_partial_selection_passes(self) -> None:
        payload = self.payload()
        payload.update({
            "asset_type": "propagation_selection",
            "status": "stage_complete",
            "scope_type": "module",
            "coverage_status": "partial",
        })
        payload["items"][0]["status"] = "deduplicated"
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_module_mother_is_forbidden(self) -> None:
        payload = self.promoted_mother()
        payload.update({"scope_type": "module", "coverage_status": "partial"})
        self.assert_fails(payload, "allowed only for single or completed course")

    def test_partial_course_cannot_be_mother_asset(self) -> None:
        payload = self.promoted_mother("course")
        payload.update({"coverage_status": "partial", "course_complete": False})
        self.assert_fails(payload, "course mother asset requires complete coverage")

    def test_asset_type_rejects_wrong_top_status(self) -> None:
        payload = self.payload()
        payload["status"] = "delivered"
        self.assert_fails(payload, "invalid top-level status")

    def test_mother_item_must_be_promoted(self) -> None:
        payload = self.promoted_mother()
        payload["items"][0]["status"] = "captured"
        self.assert_fails(payload, "must use status=promoted")

    def test_duplicate_ids_fail(self) -> None:
        payload = self.payload()
        payload["items"].append(dict(payload["items"][0]))
        self.assert_fails(payload, "asset_id values must be unique")

    def test_cross_file_duplicate_ids_fail(self) -> None:
        first = self.write_payload(self.payload(), "first.json")
        second = self.write_payload(self.payload(), "second.json")
        result = subprocess.run([sys.executable, str(VALIDATOR), str(first), str(second)], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("asset_id also appears", result.stdout)

    def test_duplicate_json_keys_fail(self) -> None:
        path = self.root / "duplicate-key.json"
        path.write_text('{"schema_version":"1.0","schema_version":"1.0"}', encoding="utf-8")
        result = subprocess.run([sys.executable, str(VALIDATOR), str(path)], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate JSON key", result.stdout)

    def test_quote_must_exist_in_source(self) -> None:
        payload = self.payload()
        payload["items"][0]["source_excerpt"] = "来源中不存在的原话"
        self.assert_fails(payload, "source_excerpt not found")

    def test_anchor_must_be_declared(self) -> None:
        payload = self.payload()
        payload["items"][0]["source_anchor"]["document"] = "other.md"
        self.assert_fails(payload, "not declared in source_documents")

    def test_r3_mother_requires_verification_and_human_evidence(self) -> None:
        payload = self.promoted_mother()
        payload["items"][0].update({"risk_level": "R3", "verification_status": "pending"})
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("before verification", result.stdout)
        self.assertIn("structured human_review", result.stdout)

    def test_r2_cannot_claim_verification_not_required(self) -> None:
        payload = self.payload()
        payload["items"][0].update({"risk_level": "R2", "verification_status": "not_required"})
        self.assert_fails(payload, "R2 cannot use verification_status=not_required")

    def test_verified_state_cannot_keep_pending_verification(self) -> None:
        payload = self.payload()
        payload["items"][0].update({"status": "verified", "verification_status": "pending"})
        self.assert_fails(payload, "verified status conflicts with verification_status=pending")

    def test_corroborated_claim_requires_verification_evidence(self) -> None:
        payload = self.payload()
        payload["items"][0].update({"risk_level": "R2", "verification_status": "corroborated"})
        self.assert_fails(payload, "verification_evidence requires a non-empty evidence list")

    def test_r3_handoff_pending_cannot_bypass_human_review(self) -> None:
        payload = self.handoff()
        payload["items"][0].update({
            "risk_level": "R3",
            "verification_status": "corroborated",
            "verification_evidence": [{
                "source": "https://example.invalid/evidence",
                "accessed_at": "2026-09-26",
                "claim": "支持被核验的具体主张",
            }],
        })
        self.assert_fails(payload, "structured human_review")

    def test_valid_r3_mother_with_structured_evidence_passes(self) -> None:
        review_record = self.root / "review-record.md"
        review_record.write_text("# 审核记录\n\n审核者确认该条内容可以在保留边界的前提下使用。\n", encoding="utf-8")
        payload = self.promoted_mother()
        payload["items"][0].update({
            "risk_level": "R3",
            "verification_status": "corroborated",
            "verification_evidence": [{
                "source": "https://example.invalid/evidence",
                "accessed_at": "2026-09-26",
                "claim": "支持被核验的具体主张",
            }],
            "human_review": {
                "status": "approved",
                "reviewer": "reviewer-id",
                "reviewed_at": "2026-09-26",
                "evidence": {
                    "kind": "file",
                    "reference": "review-record.md",
                    "approval_excerpt": "审核者确认该条内容可以在保留边界的前提下使用。",
                    "readback_verified": True,
                },
            },
        })
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_r3_review_string_cannot_masquerade_as_readback_evidence(self) -> None:
        payload = self.promoted_mother()
        payload["items"][0].update({
            "risk_level": "R3",
            "verification_status": "corroborated",
            "verification_evidence": [{
                "source": "https://example.invalid/evidence",
                "accessed_at": "2026-09-26",
                "claim": "支持被核验的具体主张",
            }],
            "human_review": {
                "status": "approved",
                "reviewer": "reviewer-id",
                "reviewed_at": "2026-09-26",
                "evidence": "review-record-001",
            },
        })
        self.assert_fails(payload, "requires structured readback evidence")

    def test_r3_review_evidence_file_cannot_be_empty(self) -> None:
        review_record = self.root / "empty-review.md"
        review_record.write_text("", encoding="utf-8")
        payload = self.promoted_mother()
        payload["items"][0].update({
            "risk_level": "R3",
            "verification_status": "corroborated",
            "verification_evidence": [{
                "source": "https://example.invalid/evidence",
                "accessed_at": "2026-09-26",
                "claim": "支持被核验的具体主张",
            }],
            "human_review": {
                "status": "approved",
                "reviewer": "reviewer-id",
                "reviewed_at": "2026-09-26",
                "evidence": {
                    "kind": "file",
                    "reference": "empty-review.md",
                    "approval_excerpt": "同意使用",
                    "readback_verified": True,
                },
            },
        })
        self.assert_fails(payload, "evidence file must not be empty")

    def test_delivered_requires_readback_evidence(self) -> None:
        self.assert_fails(self.handoff("delivered"), "readback_verified=true")

    def test_valid_delivered_handoff_with_readback_passes(self) -> None:
        target = self.root / "delivered.md"
        target.write_text("delivered", encoding="utf-8")
        payload = self.handoff("delivered")
        payload["status"] = "handed_off"
        payload["route"]["delivery_evidence"] = {
            "kind": "file",
            "readback_verified": True,
            "verified_at": "2026-09-26",
            "target_reference": str(target),
            "verification_method": "read_file",
        }
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_incomplete_course_map_excerpt_cannot_prove_completion(self) -> None:
        self.course_map.write_text("# 课程地图\n\n本课程尚未完课。\n", encoding="utf-8")
        payload = self.promoted_mother("course")
        payload["completion_evidence"]["source_excerpt"] = "本课程尚未完课。"
        self.assert_fails(payload, "states that the course is incomplete")

    def test_positive_excerpt_cannot_hide_revoked_completion_in_same_file(self) -> None:
        self.course_map.write_text(
            "# 课程地图\n\n计划课次全部验收。\n\n更正：课程尚未完课，前述结项结论撤回。\n",
            encoding="utf-8",
        )
        payload = self.promoted_mother("course")
        self.assert_fails(payload, "contains an incomplete or revoked completion statement")

    def test_status_explanation_cannot_hide_latest_incomplete_state(self) -> None:
        self.course_map.write_text(
            "# 课程地图\n\n计划课次全部验收。\n\n状态说明：课程尚未完课。\n",
            encoding="utf-8",
        )
        payload = self.promoted_mother("course")
        self.assert_fails(payload, "contains an incomplete or revoked completion statement")

    def test_rule_label_cannot_hide_latest_incomplete_state(self) -> None:
        self.course_map.write_text(
            "# 课程地图\n\n计划课次全部验收。\n\n规则状态：课程尚未完课。\n",
            encoding="utf-8",
        )
        payload = self.promoted_mother("course")
        self.assert_fails(payload, "contains an incomplete or revoked completion statement")

    def test_normative_and_live_incomplete_clauses_on_same_line_are_separated(self) -> None:
        for separator in ("；", "，", ",", "——", " "):
            with self.subTest(separator=separator):
                self.course_map.write_text(
                    "# 课程地图\n\n计划课次全部验收。\n\n"
                    f"规则说明：未完课时不得生成完整母资产{separator}状态说明：课程尚未完课。\n",
                    encoding="utf-8",
                )
                payload = self.promoted_mother("course")
                self.assert_fails(payload, "contains an incomplete or revoked completion statement")

    def test_older_incomplete_status_before_current_completion_does_not_block(self) -> None:
        self.course_map.write_text(
            "# 课程地图\n\n历史状态：课程尚未完课。\n\n计划课次全部验收。\n",
            encoding="utf-8",
        )
        payload = self.promoted_mother("course")
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_completion_instruction_after_status_does_not_create_false_conflict(self) -> None:
        self.course_map.write_text(
            "# 课程地图\n\n计划课次全部验收。\n\n规则说明：未完课时不得生成完整母资产。\n",
            encoding="utf-8",
        )
        payload = self.promoted_mother("course")
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_user_confirmation_reference_must_exist(self) -> None:
        payload = self.promoted_mother("course")
        payload["completion_evidence"].update({
            "kind": "user_confirmation",
            "reference": "missing-confirmation.md",
            "source_excerpt": "用户确认课程已经完成。",
        })
        self.assert_fails(payload, "completion_evidence reference does not exist")

    def test_missing_relative_delivery_target_fails(self) -> None:
        payload = self.handoff("delivered")
        payload["status"] = "handed_off"
        payload["route"]["delivery_evidence"] = {
            "kind": "file",
            "readback_verified": True,
            "verified_at": "2026-09-26",
            "target_reference": "missing-relative-target.md",
            "verification_method": "read_file",
        }
        self.assert_fails(payload, "must be an existing regular file")

    def test_delivery_directory_cannot_masquerade_as_readback_file(self) -> None:
        payload = self.handoff("delivered")
        payload["status"] = "handed_off"
        payload["route"]["delivery_evidence"] = {
            "kind": "file",
            "readback_verified": True,
            "verified_at": "2026-09-26",
            "target_reference": str(self.root),
            "verification_method": "read_file",
        }
        self.assert_fails(payload, "must be an existing regular file")

    def test_resolved_route_cannot_be_destination_unresolved(self) -> None:
        payload = self.handoff("destination_unresolved")
        self.assert_fails(payload, "resolved route cannot use destination_unresolved")

    def test_route_role_is_enumerated(self) -> None:
        payload = self.handoff()
        payload["route"]["role"] = "anything"
        self.assert_fails(payload, "invalid route role")

    def test_unconfigured_route_is_explicit_and_creates_nothing(self) -> None:
        before = set(self.root.iterdir())
        result = subprocess.run([sys.executable, str(RESOLVER), "--role", "draft"], cwd=self.root, text=True, capture_output=True)
        after = set(self.root.iterdir())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["route_resolution_status"], "unresolved")
        self.assertEqual(payload["delivery_status"], "destination_unresolved")
        self.assertEqual(before, after)

    def test_explicit_config_resolves_without_creating_destination(self) -> None:
        destination = self.root / "not-created"
        config = self.root / "private.yaml"
        config.write_text(f"content_draft_destination: {destination}\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(RESOLVER), "--role", "draft", "--config", str(config)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["route_resolution_status"], "resolved")
        self.assertEqual(payload["destination"], str(destination))
        self.assertFalse(destination.exists())
        self.assertFalse(payload["created"])

    def test_json_non_string_destination_is_rejected(self) -> None:
        config = self.root / "invalid.json"
        config.write_text(json.dumps({"content_draft_destination": ["/a", "/b"]}), encoding="utf-8")
        result = subprocess.run([sys.executable, str(RESOLVER), "--role", "draft", "--config", str(config)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("must be a string or null", result.stdout)

    def test_route_json_duplicate_key_is_rejected(self) -> None:
        config = self.root / "duplicate-route.json"
        config.write_text(
            '{"content_draft_destination":"/safe","content_draft_destination":"/other"}',
            encoding="utf-8",
        )
        result = subprocess.run([sys.executable, str(RESOLVER), "--role", "draft", "--config", str(config)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicate JSON key", result.stdout)

    def test_nested_yaml_is_rejected(self) -> None:
        config = self.root / "nested.yaml"
        config.write_text("wrapper:\n  content_draft_destination: /tmp/example\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(RESOLVER), "--role", "draft", "--config", str(config)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("unsupported key", result.stdout)

    def test_relative_file_destination_is_rejected(self) -> None:
        config = self.root / "relative.yaml"
        config.write_text("content_draft_destination: relative-target\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(RESOLVER), "--role", "draft", "--config", str(config)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("destination_must_be_absolute", result.stdout)

    def test_course_learning_contract_does_not_require_propagation_fields(self) -> None:
        document = self.root / "learning-only.md"
        document.write_text(
            "# 学习稿\n\n### 本课核心\n\n**判断：**学习资产与传播资产分别验证。\n",
            encoding="utf-8",
        )
        result = subprocess.run([
            sys.executable, str(COURSE_VALIDATOR), "--profile", "long-course-faithful", str(document)
        ], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_course_contract_cannot_be_satisfied_by_code_block(self) -> None:
        document = self.root / "code-only.md"
        document.write_text(
            "# 空课程\n\n```text\n本课核心\n事实核验与边界说明\nA ·\nC ·\nD ·\nE ·\n```\n",
            encoding="utf-8",
        )
        result = subprocess.run([
            sys.executable, str(COURSE_VALIDATOR), "--profile", "long-course-notes", str(document)
        ], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("profile required term missing", result.stdout)

    def test_course_contract_cannot_be_satisfied_by_indented_code(self) -> None:
        document = self.root / "indented-code-only.md"
        document.write_text(
            "# 空课程\n\n    本课核心\n    事实核验与边界说明\n    A ·\n    C ·\n    D ·\n    E ·\n",
            encoding="utf-8",
        )
        result = subprocess.run([
            sys.executable, str(COURSE_VALIDATOR), "--profile", "long-course-notes", str(document)
        ], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("profile required term missing", result.stdout)

    def test_course_contract_cannot_be_satisfied_by_blockquoted_fence(self) -> None:
        document = self.root / "blockquote-fence.md"
        document.write_text(
            "# 空课程\n\n> ```text\n> 本课核心\n> 事实核验与边界说明\n> A ·\n> C ·\n> D ·\n> E ·\n> ```\n",
            encoding="utf-8",
        )
        result = subprocess.run([
            sys.executable, str(COURSE_VALIDATOR), "--profile", "long-course-notes", str(document)
        ], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("profile required term missing", result.stdout)




if __name__ == "__main__":
    unittest.main(verbosity=2)
