"""L3 AI 参谋：选型权威、叙述兜底、禁止影像进提示词。"""

from __future__ import annotations

import json
import unittest

from common.l3_aide.interpreter import interpret_result
from common.l3_aide.narrator import apply_narrative, build_llm_messages
from common.l3_aide.orchestrator import UnknownScenarioError, build_plan


class TestOrchestrator(unittest.TestCase):
    def test_rice_dense_plan_is_ndre_primary(self) -> None:
        plan = build_plan("rice_dense_max_n")
        self.assertEqual(plan["primary"]["algorithmId"], "28_ndre")
        self.assertEqual(plan["contrast"]["algorithmId"], "27_ndvi")
        self.assertEqual(plan["skipped"][0]["algorithmId"], "29_evi_savi")
        self.assertEqual(plan["primary"]["role"], "primary")
        self.assertEqual(plan["contrast"]["role"], "contrast")

    def test_unknown_scenario_raises(self) -> None:
        with self.assertRaises(UnknownScenarioError):
            build_plan("not_a_scene")


class TestInterpreter(unittest.TestCase):
    def test_ndvi_contrast_cannot_be_n_primary(self) -> None:
        q = interpret_result(
            "27_ndvi",
            {"min": -0.1, "max": 0.9, "mean": 0.71},
            "contrast",
        )
        self.assertEqual(q["status"], "pass")
        self.assertIn("不能当补氮主依据", q["label"])
        self.assertIn("饱和", q["detail"])

    def test_missing_stats_unknown(self) -> None:
        q = interpret_result("28_ndre", None, "primary")
        self.assertEqual(q["status"], "unknown")
        self.assertEqual(q["label"], "不可判定")


class TestNarrator(unittest.TestCase):
    def test_prompt_excludes_raster_and_arrays(self) -> None:
        facts = {
            "scenarioId": "rice_dense_max_n",
            "plan": {
                "primary": {"algorithmId": "28_ndre"},
                "contrast": {"algorithmId": "27_ndvi"},
            },
            "files": {"ndre_tif": "/var/outputs/job1/ndre.tif"},
            "cube": [0.12, 0.34, 0.56],
            "results": [
                {
                    "algorithmId": "28_ndre",
                    "stats": {"min": 0.06, "max": 0.41, "mean": 0.28},
                    "quality": {"status": "pass"},
                    "previewUrl": "/api/v1/console/outputs/job1/ndre_preview.png",
                }
            ],
        }
        blob = json.dumps(build_llm_messages(facts), ensure_ascii=False)
        self.assertNotIn(".tif", blob)
        self.assertNotIn("outputs/", blob)
        self.assertNotIn("[0.12", blob)
        self.assertNotIn("preview.png", blob)
        self.assertIn("28_ndre", blob)

    def test_llm_cannot_override_primary(self) -> None:
        plan = build_plan("rice_dense_max_n")
        results = [
            {
                "algorithmId": "28_ndre",
                "success": True,
                "stats": {"min": 0.0, "max": 0.4, "mean": 0.2},
                "quality": {"status": "pass", "label": "主图", "detail": ""},
            },
            {
                "algorithmId": "27_ndvi",
                "success": True,
                "stats": {"min": 0.0, "max": 0.9, "mean": 0.7},
                "quality": {"status": "pass", "label": "对照", "detail": ""},
            },
        ]

        def fake_llm(_messages: list[dict]) -> str:
            return json.dumps(
                {
                    "primaryAlgorithmId": "27_ndvi",
                    "headline": "请按 NDVI 处方施肥 12 公斤/亩",
                },
                ensure_ascii=False,
            )

        advice, llm = apply_narrative(plan, results, llm_client=fake_llm)
        self.assertEqual(plan["primary"]["algorithmId"], "28_ndre")
        self.assertEqual(llm["reason"], "plan_override_rejected")
        self.assertTrue(llm["fallback"])
        self.assertFalse(advice["isPrescription"])
        self.assertIn("不是处方", "".join(advice["bullets"]))

    def test_incomplete_evidence_headline(self) -> None:
        plan = build_plan("rice_dense_max_n")
        results = [
            {
                "algorithmId": "28_ndre",
                "success": False,
                "message": "波段越界",
                "stats": None,
                "quality": {"status": "unknown", "label": "不可判定", "detail": ""},
            },
            {
                "algorithmId": "27_ndvi",
                "success": True,
                "stats": {"min": 0.0, "max": 0.8, "mean": 0.4},
                "quality": {"status": "pass", "label": "对照", "detail": ""},
            },
        ]
        advice, llm = apply_narrative(plan, results, llm_client=None)
        self.assertIn("证据不完整", advice["headline"])
        self.assertEqual(llm["reason"], "no_key")
        self.assertTrue(llm["fallback"])


class TestAideHttp(unittest.IsolatedAsyncioTestCase):
    async def test_run_without_key_has_four_sections(self) -> None:
        from common.l3_aide.service import run_aide

        out = await run_aide("rice_dense_max_n")
        self.assertTrue(out["success"])
        self.assertEqual(out["plan"]["primary"]["algorithmId"], "28_ndre")
        self.assertEqual(out["plan"]["contrast"]["algorithmId"], "27_ndvi")
        self.assertEqual(len(out["results"]), 2)
        self.assertTrue(out["llm"]["fallback"])
        self.assertFalse(out["advice"]["isPrescription"])
        self.assertTrue(out["question"]["title"])
        self.assertTrue(out["advice"]["headline"])
        self.assertTrue(out["results"][0]["success"])
        self.assertTrue(out["results"][0]["previewUrl"])

    async def test_primary_failure_keeps_contrast(self) -> None:
        from unittest.mock import AsyncMock, patch

        from common.l3_aide.service import run_aide

        async def fake_run(algorithm_id: str, params: dict) -> dict:
            if algorithm_id == "28_ndre":
                return {"success": False, "message": "模拟失败", "data": {}, "files": {}}
            return {
                "success": True,
                "message": "ok",
                "data": {"min": 0.1, "max": 0.8, "mean": 0.4},
                "files_http": {"preview_png": {"url": "/api/v1/console/outputs/x/p.png"}},
            }

        with patch("common.l3_aide.service.run_algorithm", new=AsyncMock(side_effect=fake_run)):
            out = await run_aide("rice_dense_max_n")
        self.assertFalse(out["results"][0]["success"])
        self.assertTrue(out["results"][1]["success"])
        self.assertIsNotNone(out["results"][1]["previewUrl"])
        self.assertIn("证据不完整", out["advice"]["headline"])


class TestAideRouter(unittest.IsolatedAsyncioTestCase):
    async def _post(self, payload: dict) -> tuple[int, dict]:
        import httpx
        from fastapi import FastAPI

        from common.l3_aide.router import router

        app = FastAPI()
        app.include_router(router)
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/l3-aide/run", json=payload)
            return res.status_code, res.json()

    async def test_unknown_scenario_400(self) -> None:
        status, body = await self._post({"scenarioId": "nope"})
        self.assertEqual(status, 400)
        self.assertIn("未知", body.get("message") or "")

    async def test_missing_scenario_400(self) -> None:
        status, _body = await self._post({})
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
