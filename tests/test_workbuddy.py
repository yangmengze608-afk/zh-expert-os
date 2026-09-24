from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from zh_expert_os.models import Expert
from zh_expert_os.workbuddy import (
    ArtifactRef,
    EvidenceClaim,
    EvidenceRef,
    ExpertEnvelope,
    MessageDeliveryState,
    NativeExpertSpec,
    WorkBuddyContractError,
    WorkBuddyNodeState,
    WorkBuddyTeamPlan,
    extract_expert_envelope,
    native_spec_from_expert,
    render_native_expert,
    sha256_file,
    write_native_expert,
)


class WorkBuddyContractTests(unittest.TestCase):
    def test_evidence_claim_requires_provenance(self):
        claim = EvidenceClaim("结论", 0.8, [])
        with self.assertRaises(WorkBuddyContractError):
            claim.validate()

    def test_derived_evidence_requires_parents(self):
        ref = EvidenceRef("task-1", "derived", "calc:mean")
        with self.assertRaises(WorkBuddyContractError):
            ref.validate()

    def test_artifact_requires_relative_path_and_sha(self):
        bad = ArtifactRef("/tmp/x.txt", "0" * 64)
        with self.assertRaises(WorkBuddyContractError):
            bad.validate()
        good = ArtifactRef("worker-a/evidence.json", "a" * 64)
        good.validate()

    def test_message_delivery_is_three_stage(self):
        with self.assertRaises(WorkBuddyContractError):
            MessageDeliveryState(route_accepted=True, consumed=False, acked=True).validate()
        state = MessageDeliveryState(True, True, True)
        self.assertTrue(state.confirmed)

    def test_host_and_envelope_status_stay_separate(self):
        env = ExpertEnvelope(
            agent_id="expert-a",
            task_id="task-a",
            status="partial",
            confidence=0.7,
            summary="预算不足，已完成部分工作",
        )
        node = WorkBuddyNodeState("host-task-123", "task-a", "expert-a", "cancelled", env)
        data = node.to_dict()
        self.assertEqual(data["host_task_id"], "host-task-123")
        self.assertEqual(data["assignment_id"], "task-a")
        self.assertEqual(data["host_status"], "cancelled")
        self.assertEqual(data["envelope"]["status"], "partial")
        self.assertTrue(data["terminal"])

    def test_node_rejects_envelope_from_different_agent(self):
        env = ExpertEnvelope(
            agent_id="expert-b",
            task_id="task-a",
            status="ok",
            confidence=0.9,
            summary="done",
        )
        node = WorkBuddyNodeState("host-task-123", "task-a", "expert-a", "completed", env)
        with self.assertRaises(WorkBuddyContractError):
            node.validate()

    def test_flat_team_plan_requires_unique_namespaces(self):
        plan = WorkBuddyTeamPlan(
            lead_id="lead",
            worker_ids=["a", "b"],
            artifact_namespaces={"a": "run/a", "b": "run/b"},
        )
        plan.validate()
        bad = WorkBuddyTeamPlan(
            lead_id="lead",
            worker_ids=["a", "b"],
            artifact_namespaces={"a": "run/shared", "b": "run/shared"},
        )
        with self.assertRaises(WorkBuddyContractError):
            bad.validate()

    def test_renderer_emits_compatibility_max_turns_only(self):
        spec = NativeExpertSpec(
            id="demo-expert",
            display_name_zh="示例专家",
            display_name_en="Demo Expert",
            profession_zh="验证",
            profession_en="Validation",
            description="用于测试",
            instructions="# Instructions\nDo the task.",
        )
        text = render_native_expert(spec)
        self.assertIn("name: demo-expert", text)
        self.assertIn("ZEOS_ENVELOPE", text)
        self.assertIn("maxTurns: 200", text)

    def test_extract_envelope_from_agent_output(self):
        text = """完成。\nZEOS_ENVELOPE\n{\n  \"agent_id\": \"a\",\n  \"task_id\": \"t\",\n  \"status\": \"ok\",\n  \"confidence\": 0.9,\n  \"summary\": \"done\",\n  \"claims\": [],\n  \"artifacts\": [],\n  \"open_questions\": []\n}\n"""
        env = extract_expert_envelope(text)
        self.assertEqual(env.agent_id, "a")
        self.assertEqual(env.status, "ok")
        bad = text.replace('\"open_questions\": []', '\"open_questions\": [], \"unexpected\": 1')
        with self.assertRaises(WorkBuddyContractError):
            extract_expert_envelope(bad)

    def test_extract_envelope_rejects_wrong_container_types(self):
        bad_open_questions = """ZEOS_ENVELOPE
{
  "agent_id": "a",
  "task_id": "t",
  "status": "ok",
  "confidence": 0.9,
  "summary": "done",
  "claims": [],
  "artifacts": [],
  "open_questions": "not-a-list"
}
"""
        with self.assertRaises(WorkBuddyContractError):
            extract_expert_envelope(bad_open_questions)

        bad_evidence = """ZEOS_ENVELOPE
{
  "agent_id": "a",
  "task_id": "t",
  "status": "ok",
  "confidence": 0.9,
  "summary": "done",
  "claims": [
    {
      "statement": "x",
      "confidence": 0.8,
      "evidence": [
        {
          "source_task_id": "t",
          "kind": "tool_result",
          "locator": "tool:1",
          "unexpected": "no"
        }
      ]
    }
  ],
  "artifacts": [],
  "open_questions": []
}
"""
        with self.assertRaises(WorkBuddyContractError):
            extract_expert_envelope(bad_evidence)

    def test_boolean_confidence_is_rejected(self):
        env = ExpertEnvelope(
            agent_id="a",
            task_id="t",
            status="ok",
            confidence=True,
            summary="done",
        )
        with self.assertRaises(WorkBuddyContractError):
            env.validate()

    def test_candidate_cannot_be_exported_as_native_expert(self):
        expert = Expert(
            id="candidate-demo",
            name_zh="候选专家",
            version="0.1",
            status="candidate",
            role="研究",
            source="test",
            license="MIT",
        )
        with self.assertRaises(WorkBuddyContractError):
            native_spec_from_expert(expert)

    def test_registry_expert_can_be_rendered_and_written(self):
        expert = Expert(
            id="shadow-demo",
            name_zh="影子专家",
            version="0.1",
            status="probation",
            role="证据研究",
            source="test",
            license="MIT",
            mission="独立核验证据。",
        )
        spec = native_spec_from_expert(expert)
        self.assertEqual(spec.id, "shadow-demo")
        self.assertNotIn("MIT", spec.instructions)
        with tempfile.TemporaryDirectory() as td:
            path = write_native_expert(expert, Path(td))
            self.assertTrue(path.exists())
            self.assertIn("独立核验证据", path.read_text(encoding="utf-8"))
            with self.assertRaises(FileExistsError):
                write_native_expert(expert, Path(td))

    def test_force_replaces_symlink_without_modifying_symlink_source(self):
        expert = Expert(
            id="shadow-demo",
            name_zh="影子专家",
            version="0.1",
            status="probation",
            role="证据研究",
            source="test",
            license="MIT",
            mission="独立核验证据。",
        )
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "external.md"
            source.write_text("DO NOT MODIFY", encoding="utf-8")
            out = root / "agents"
            out.mkdir()
            target = out / "shadow-demo.md"
            target.symlink_to(source)
            path = write_native_expert(expert, out, overwrite=True)
            self.assertEqual(source.read_text(encoding="utf-8"), "DO NOT MODIFY")
            self.assertFalse(path.is_symlink())
            self.assertIn("ZEOS_ENVELOPE", path.read_text(encoding="utf-8"))

    def test_sha256_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.txt"
            p.write_text("abc", encoding="utf-8")
            self.assertEqual(
                sha256_file(p),
                "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
            )


if __name__ == "__main__":
    unittest.main()
