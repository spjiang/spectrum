"""L3 AI 参谋：选型权威、叙述兜底、禁止影像进提示词。"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from common.l3_aide.interpreter import interpret_result
from common.l3_aide.narrator import apply_narrative, build_llm_messages
from common.l3_aide.orchestrator import UnknownScenarioError, build_plan


class TestOrchestrator(unittest.TestCase):
    def test_index_output_review_keeps_registered_pair(self) -> None:
        plan = build_plan("index_output_review")
        self.assertEqual(plan["primary"]["algorithmId"], "28_ndre")
        self.assertEqual(plan["contrast"]["algorithmId"], "27_ndvi")
        self.assertEqual(plan["skipped"][0]["algorithmId"], "29_evi_savi")
        self.assertEqual(plan["primary"]["role"], "primary")
        self.assertEqual(plan["contrast"]["role"], "contrast")

    def test_unknown_scenario_raises(self) -> None:
        with self.assertRaises(UnknownScenarioError):
            build_plan("not_a_scene")


class TestInterpreter(unittest.TestCase):
    def test_ndvi_contrast_is_only_same_scene_comparison(self) -> None:
        q = interpret_result(
            "27_ndvi",
            {"min": -0.1, "max": 0.9, "mean": 0.71},
            "contrast",
        )
        self.assertEqual(q["status"], "pass")
        self.assertIn("仅作同景对照", q["label"])
        self.assertIn("不能据此作业务决策", q["detail"])
        self.assertIn("饱和", q["detail"])

    def test_missing_stats_unknown(self) -> None:
        q = interpret_result("28_ndre", None, "primary")
        self.assertEqual(q["status"], "unknown")
        self.assertEqual(q["label"], "不可判定")


class TestNarrator(unittest.TestCase):
    def test_prompt_excludes_raster_and_arrays(self) -> None:
        facts = {
            "scenarioId": "index_output_review",
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
        plan = build_plan("index_output_review")
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
        plan = build_plan("index_output_review")
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

    def test_valid_narrative_uses_model_advice(self) -> None:
        plan = build_plan("index_output_review")
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
                    "primaryAlgorithmId": "28_ndre",
                    "headline": "先看 NDRE 弱区，再决定要不要下地",
                    "bullets": ["这不是处方。", "对照 NDVI 只说明冠层已封垄。"],
                },
                ensure_ascii=False,
            )

        advice, llm = apply_narrative(plan, results, llm_client=fake_llm)
        self.assertFalse(llm["fallback"])
        self.assertEqual(advice["headline"], "先看 NDRE 弱区，再决定要不要下地")
        self.assertIn("不是处方", "".join(advice["bullets"]))


class TestAideHttp(unittest.IsolatedAsyncioTestCase):
    async def test_run_without_key_has_four_sections(self) -> None:
        from common.l3_aide.service import run_aide

        out = await run_aide("index_output_review")
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
            out = await run_aide("index_output_review")
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


L3_IDS = {
    "27_ndvi",
    "28_ndre",
    "29_evi_savi",
    "30_ndmi_ndwi",
    "31_red_edge_params",
    "32_regression_inversion",
    "33_physical_inversion",
    "34_svm_rf_classify",
    "35_spectral_matching",
    "36_cnn1d_classify",
    "37_cnn3d_classify",
    "38_transformer_classify",
    "39_few_shot_classify",
    "40_detect_segment",
    "41_unmixing",
    "42_anomaly_detect",
    "43_change_detect",
    "46_reci",
    "47_gndvi",
    "48_osavi",
    "49_arvi",
    "50_vari",
    "51_lai_index",
    "52_nbr",
    "53_sipi",
    "54_gci",
    "55_ndsi",
}


class TestAideKnowledge(unittest.TestCase):
    def test_list_has_all_l3_aide_index_classify_mix_ids(self) -> None:
        from common.l3_aide.knowledge import list_algorithm_groups

        groups = list_algorithm_groups()
        self.assertEqual([g["id"] for g in groups], ["index", "classify", "mix"])
        ids = [item["id"] for g in groups for item in g["items"]]
        self.assertEqual(len(ids), 27)
        self.assertEqual(set(ids), L3_IDS)

    def test_each_entry_has_accuracy_without_llm(self) -> None:
        from common.l3_aide.knowledge import get_algorithm, list_algorithm_ids

        for aid in list_algorithm_ids():
            doc = get_algorithm(aid)
            self.assertIsNotNone(doc)
            assert doc is not None
            self.assertGreaterEqual(len(doc["accuracy"]), 3)
            self.assertGreaterEqual(len(doc["llmMay"]), 1)
            self.assertGreaterEqual(len(doc["llmMustNot"]), 1)
            self.assertIn(doc["title"], doc["llmPrompt"])
            self.assertIn("runComment", doc["llmPrompt"])
            self.assertIn("现象", doc["llmPrompt"])
            self.assertIn("边界", doc["llmPrompt"])
            self.assertIn("下一步", doc["llmPrompt"])
            self.assertIn("禁止只复述", doc["llmPrompt"])
            self.assertIn("不是处方", doc["llmPrompt"])
            self.assertIn("不要改推其他算法", doc["llmPrompt"])
            self.assertGreaterEqual(len(doc["llmPrompt"]), 280)
            self.assertGreaterEqual(len(doc["readout"]), 3)
            for line in doc["accuracy"]:
                self.assertNotIn("大模型", line)

    def test_every_algorithm_has_llm_leverage(self) -> None:
        from common.l3_aide.knowledge import get_algorithm, list_algorithm_ids, llm_leverage_of

        for aid in list_algorithm_ids():
            lev = llm_leverage_of(aid)
            self.assertEqual(lev["max"], 9)
            self.assertEqual(lev["score"], sum(d["score"] for d in lev["dims"]))
            self.assertEqual(lev["percent"], round(100 * lev["score"] / 9))
            self.assertIn(lev["band"], {"偏低", "中等", "偏高"})
            self.assertIn("不是精度贡献", lev["note"])
            self.assertEqual([d["id"] for d in lev["dims"]], ["readout", "bounds", "guard"])
            self.assertEqual([d["label"] for d in lev["dims"]], ["帮你读返回", "点出方法限制", "拦住说错"])
            self.assertNotIn("选型建议", " ".join(d["label"] for d in lev["dims"]))
            for dim in lev["dims"]:
                self.assertGreaterEqual(dim["score"], 0)
                self.assertLessEqual(dim["score"], 3)
                self.assertTrue(dim["why"])
                self.assertFalse(dim["why"].startswith("大模型会"))
                self.assertIn(dim["effect"], {"几乎帮不上", "效果有限", "能看出来", "作用明显"})
            doc = get_algorithm(aid)
            assert doc is not None
            self.assertEqual(doc["llmLeverage"]["score"], lev["score"])

    def test_ndvi_leverage_is_medium(self) -> None:
        from common.l3_aide.knowledge import llm_leverage_of

        lev = llm_leverage_of("27_ndvi")
        self.assertEqual(lev["score"], 6)
        self.assertEqual(lev["band"], "中等")
        readout = next(d for d in lev["dims"] if d["id"] == "readout")
        self.assertEqual(readout["score"], 2)

    def test_all_catalog_algorithms_have_analysis_sections(self) -> None:
        from common.catalog import ALGORITHMS as CATALOG
        from common.l3_aide.knowledge import get_algorithm, llm_leverage_of

        ids = [row["id"] for row in CATALOG]
        self.assertEqual(len(ids), 55)
        labels = ["提高本次运行", "接到应用", "方法限制", "拦住说错"]
        improve_texts = set()
        app_texts = set()
        for aid in ids:
            lev = llm_leverage_of(aid)
            sections = lev["sections"]
            self.assertEqual([row["label"] for row in sections], labels)
            by_id = {row["id"]: row["text"] for row in sections}
            self.assertGreater(len(by_id["improveRun"]), 20)
            self.assertIn("这是下游用法", by_id["toApplication"])
            self.assertNotIn("处方", by_id["toApplication"])
            self.assertNotIn("喷药", by_id["toApplication"])
            improve_texts.add(by_id["improveRun"])
            app_texts.add(by_id["toApplication"])
            doc = get_algorithm(aid)
            assert doc is not None
            self.assertEqual(doc["llmLeverage"]["sections"], sections)
            self.assertIn("后续用法，不是本页已交付产品", doc["llmPrompt"])
        self.assertEqual(len(improve_texts), 55)
        self.assertEqual(len(app_texts), 55)

    def test_ndvi_analysis_covers_run_app_and_guards(self) -> None:
        from common.l3_aide.knowledge import llm_leverage_of

        lev = llm_leverage_of("27_ndvi")
        blob = " ".join(row["text"] for row in lev["sections"])
        self.assertIn("red_band", blob)
        self.assertIn("nir_band", blob)
        self.assertIn("饱和", blob)
        self.assertIn("不能直接作为叶绿素含量或生物量定量产品", blob)
        self.assertIn("这是下游用法", blob)
        self.assertIn("NDVI GeoTIFF", blob)

    def test_knowledge_stays_on_current_algorithm(self) -> None:
        from common.l3_aide.knowledge import get_algorithm, list_algorithm_ids, llm_leverage_of

        banned = ("改看", "封垄", "主图", "选型建议")
        for aid in list_algorithm_ids():
            doc = get_algorithm(aid)
            assert doc is not None
            blob = " ".join(
                [*doc["accuracy"], *doc["llmMay"], *doc["readout"], *doc["llmMustNot"]]
            )
            for word in banned:
                self.assertNotIn(word, blob, f"{aid} 不应出现「{word}」")
            lev = llm_leverage_of(aid)
            why = " ".join(d["why"] for d in lev["dims"])
            for word in banned:
                self.assertNotIn(word, why, f"{aid} 赋能说明不应出现「{word}」")

    def test_ai_copy_has_no_fixed_crop_scenario_or_action_recommendation(self) -> None:
        """通用 AI 解读不能绑定作物、处方动作或跨算法主图选择。"""
        aide_root = Path(__file__).parents[1] / "common" / "l3_aide"
        text = "\n".join(
            (aide_root / name).read_text(encoding="utf-8")
            for name in ("interpreter.py", "layers.py", "scenarios.py")
        )
        fixed_scene_words = ("封垄", "补氮", "水稻", "撒氮", "撒尿素", "施肥", "主图")
        for word in fixed_scene_words:
            self.assertNotIn(word, text)

        from common.l3_aide.knowledge import get_algorithm, list_algorithm_ids

        for algorithm_id in list_algorithm_ids():
            doc = get_algorithm(algorithm_id)
            assert doc is not None
            guard = " ".join(doc["llmMustNot"])
            self.assertIn("不得推荐其他算法", guard)
            self.assertIn("不得输出处方或业务决策", guard)

    def test_unmixing_leverage_is_high(self) -> None:
        from common.l3_aide.knowledge import llm_leverage_of

        lev = llm_leverage_of("41_unmixing")
        self.assertGreaterEqual(lev["score"], 7)
        self.assertEqual(lev["band"], "偏高")

    def test_l4_handwritten_knowledge_stays_algorithm_local(self) -> None:
        """#44/#45 必须使用手写知识并禁止场景、推荐和决策外推。"""
        from common.l3_aide.knowledge import get_algorithm

        postprocess = get_algorithm("44_postprocess_smooth")
        zonal = get_algorithm("45_parcel_zonal_stats")
        assert postprocess is not None and zonal is not None
        self.assertIn("n_changed", " ".join(postprocess["llmMay"]))
        self.assertIn("NoData", " ".join(zonal["accuracy"]))
        self.assertIn("空有效区", " ".join(zonal["accuracy"]))
        for doc in (postprocess, zonal):
            guard = " ".join(doc["llmMustNot"])
            self.assertIn("不得推荐其他算法", guard)
            self.assertIn("不得输出处方或业务决策", guard)
        self.assertIn("不得预设", " ".join(zonal["llmMustNot"]))

    def test_narrowed_titles_match_only_implemented_capabilities(self) -> None:
        from common.l3_aide.knowledge import get_algorithm

        expected = {
            "36_cnn1d_classify": "1D-CNN光谱分类",
            "38_transformer_classify": "SpectralFormer光谱分类",
            "39_few_shot_classify": "SAM均值原型少样本分类",
            "40_detect_segment": "低NDVI种子ACE目标检测",
        }
        for algorithm_id, title in expected.items():
            doc = get_algorithm(algorithm_id)
            assert doc is not None
            self.assertEqual(title, doc["title"])

    def test_ndvi_llm_may_reads_returned_fields(self) -> None:
        from common.l3_aide.knowledge import get_algorithm

        doc = get_algorithm("27_ndvi")
        assert doc is not None
        joined = " ".join(doc["llmMay"])
        self.assertIn("red_band", joined)
        self.assertIn("nir_band", joined)
        self.assertNotIn("不得重算", joined)

    def test_unknown_algorithm_is_none(self) -> None:
        from common.l3_aide.knowledge import get_algorithm

        self.assertIsNone(get_algorithm("not_an_algorithm"))

    def test_catalog_algorithm_falls_back_to_output_summary(self) -> None:
        from common.l3_aide.knowledge import get_algorithm

        doc = get_algorithm("01_flight_planning")
        assert doc is not None
        self.assertEqual(doc["id"], "01_flight_planning")
        self.assertIn("航线", doc["title"])
        self.assertIn("航线", doc["definition"])
        self.assertEqual(doc["llmLeverage"]["score"], 6)
        self.assertIn("不得改推其他算法", " ".join(doc["llmMustNot"]))
        self.assertNotIn("{mean", " ".join(doc["readout"]))


class TestAideAlgoPrompt(unittest.TestCase):
    def test_algo_prompt_excludes_raster(self) -> None:
        from common.l3_aide.narrator import build_algo_llm_messages

        messages = build_algo_llm_messages(
            {
                "id": "27_ndvi",
                "llmPrompt": "你是 NDVI植被指数 的解读器。不得把立方体送进大模型。",
                "llmMustNot": ["不得把立方体送进大模型。"],
                "stats": {"min": 0.1, "max": 0.8, "mean": 0.4},
                "files": {"ndvi_tif": "/var/outputs/job/ndvi.tif"},
                "previewUrl": "/api/v1/console/outputs/job/ndvi_preview.png",
            }
        )
        blob = json.dumps(messages, ensure_ascii=False)
        self.assertNotIn(".tif", blob)
        self.assertNotIn("outputs/", blob)
        self.assertNotIn("preview.png", blob)
        self.assertIn("27_ndvi", blob)

    def test_prescription_comment_rejected(self) -> None:
        from common.l3_aide.narrator import apply_run_comment

        def fake_llm(_messages: list[dict]) -> str:
            return json.dumps({"runComment": "必须补氮 10 公斤/亩"}, ensure_ascii=False)

        comment, llm, _preview = apply_run_comment(
            "27_ndvi",
            {"min": 0.1, "max": 0.8, "mean": 0.4},
            {"status": "pass", "label": "ok", "detail": ""},
            ["不得把立方体送进大模型。"],
            llm_client=fake_llm,
        )
        self.assertEqual(llm["reason"], "invalid")
        self.assertTrue(llm["fallback"])
        self.assertNotIn("公斤", comment)
        self.assertIn("不是处方", comment)

    def test_cannot_serve_as_prescription_is_accepted(self) -> None:
        from common.l3_aide.narrator import apply_run_comment

        def fake_llm(_messages: list[dict]) -> str:
            return json.dumps(
                {"runComment": "均值落在绿度常见区间，不能作为处方，也不是农情验收。"},
                ensure_ascii=False,
            )

        comment, llm, _preview = apply_run_comment(
            "27_ndvi",
            {"min": 0.1, "max": 0.8, "mean": 0.4},
            {"status": "pass", "label": "ok", "detail": ""},
            ["不得把立方体送进大模型。"],
            llm_client=fake_llm,
        )
        self.assertFalse(llm["fallback"])
        self.assertEqual(llm["reason"], "ok")
        self.assertIn("不能作为处方", comment)

    def test_timeout_is_not_labeled_invalid(self) -> None:
        from common.l3_aide.narrator import apply_run_comment

        def fake_llm(_messages: list[dict]) -> str:
            raise TimeoutError("timed out")

        _comment, llm, _preview = apply_run_comment(
            "27_ndvi",
            {"min": 0.1, "max": 0.8, "mean": 0.4},
            {"status": "pass", "label": "ok", "detail": ""},
            ["不得把立方体送进大模型。"],
            llm_client=fake_llm,
        )
        self.assertEqual(llm["reason"], "timeout")
        self.assertTrue(llm["fallback"])

    def test_http_error_keeps_detail(self) -> None:
        from common.l3_aide.narrator import apply_run_comment

        def fake_llm(_messages: list[dict]) -> str:
            raise OSError("模型 HTTP 401: Authentication Fails")

        _comment, llm, _preview = apply_run_comment(
            "27_ndvi",
            {"min": 0.1, "max": 0.8, "mean": 0.4},
            {"status": "pass", "label": "ok", "detail": ""},
            ["不得把立方体送进大模型。"],
            llm_client=fake_llm,
        )
        self.assertEqual(llm["reason"], "http_error")
        self.assertIn("401", llm.get("detail") or "")

    def test_valid_run_comment_uses_model_text(self) -> None:
        from common.l3_aide.narrator import apply_run_comment

        def fake_llm(_messages: list[dict]) -> str:
            return json.dumps(
                {"runComment": "均值落在常见区间，只能当演示样例，不是处方。"},
                ensure_ascii=False,
            )

        comment, llm, preview = apply_run_comment(
            "27_ndvi",
            {"min": 0.1, "max": 0.8, "mean": 0.4},
            {"status": "pass", "label": "ok", "detail": ""},
            ["不得把立方体送进大模型。"],
            llm_client=fake_llm,
            llm_prompt="你是 NDVI植被指数 的解读器。",
        )
        self.assertIn("NDVI植被指数", preview["system"])
        self.assertFalse(llm["fallback"])
        self.assertEqual(llm["reason"], "ok")
        self.assertIn("演示样例", comment)
        self.assertNotEqual(
            comment,
            "本次 min 0.100、max 0.800、mean 0.400。这是演示数据统计，不能当农情或业务验收结论。",
        )

    def test_ndvi_fallback_reads_domain_not_echo(self) -> None:
        from common.l3_aide.narrator import template_run_comment

        text = template_run_comment(
            "27_ndvi",
            {"min": -0.623, "max": 0.857, "mean": 0.331},
            {"status": "pass", "label": "统计落在指数常见区间", "detail": ""},
        )
        self.assertNotIn("本次 min -0.623、max 0.857、mean 0.331。", text)
        self.assertIn("0.33", text)
        self.assertIn("公式饱和", text)
        self.assertNotIn("NDRE", text)
        self.assertIn("不是处方", text)
        self.assertGreaterEqual(len(text), 80)

    def test_user_prompt_carries_task_not_raster(self) -> None:
        from common.l3_aide.narrator import build_algo_llm_messages

        messages = build_algo_llm_messages(
            {
                "id": "27_ndvi",
                "title": "NDVI植被指数",
                "definition": "归一化差值植被指数 NDVI = (近红外反射率 − 红光反射率) / (近红外反射率 + 红光反射率)，用于表征植被绿度、活力及冠层覆盖状况。",
                "llmPrompt": "你是 NDVI植被指数 的解读器。",
                "stats": {"min": 0.1, "max": 0.8, "mean": 0.4},
                "data": {
                    "min": 0.1,
                    "max": 0.8,
                    "mean": 0.4,
                    "preview": "/api/v1/console/outputs/job/ndvi_preview.png",
                    "cube": [0.1, 0.2, 0.3],
                },
                "files": {"ndvi_tif": "/var/outputs/job/ndvi.tif"},
                "quality": {"status": "pass", "label": "ok", "detail": "区间合理"},
            }
        )
        user = messages[1]["content"]
        self.assertIn("对照字段说明解读", user)
        self.assertIn("NDVI植被指数", user)
        self.assertIn("NDVI均值", user)
        self.assertIn("businessMeaning", user)
        self.assertIn('"mean": 0.4', user)
        self.assertIn("ndvi_tif", user)
        self.assertNotIn(".tif", user)
        self.assertNotIn("preview.png", user)
        self.assertNotIn("[0.1, 0.2", user)


class TestLlmClient(unittest.TestCase):
    def test_empty_key_returns_none(self) -> None:
        from common.l3_aide.llm_client import client_from_config

        self.assertIsNone(client_from_config({"apiKey": "", "baseUrl": "https://api.deepseek.com"}))

    def test_parse_fenced_json(self) -> None:
        from common.l3_aide.llm_client import extract_message_text

        raw = json.dumps(
            {
                "choices": [
                    {
                        "message": {
                            "content": '```json\n{"runComment":"区间合理，不是处方"}\n```',
                        }
                    }
                ]
            }
        )
        self.assertEqual(extract_message_text(raw), '{"runComment":"区间合理，不是处方"}')

    def test_ssl_context_uses_certifi(self) -> None:
        from common.l3_aide.llm_client import ssl_context

        ctx = ssl_context()
        self.assertIsNotNone(ctx)


class TestAideAlgoRouter(unittest.IsolatedAsyncioTestCase):
    async def _client(self):
        import httpx
        from fastapi import FastAPI

        from common.l3_aide.router import router

        app = FastAPI()
        app.include_router(router)
        transport = httpx.ASGITransport(app=app)
        return httpx.AsyncClient(transport=transport, base_url="http://test")

    async def test_l0_algorithm_has_knowledge(self) -> None:
        async with await self._client() as client:
            res = await client.get("/api/v1/l3-aide/algorithms/01_flight_planning")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["id"], "01_flight_planning")
        self.assertIn("航线", body["definition"])

    async def test_unknown_algorithm_404(self) -> None:
        async with await self._client() as client:
            res = await client.get("/api/v1/l3-aide/algorithms/not_an_algorithm")
        self.assertEqual(res.status_code, 404)

    async def test_ndvi_run_comment_has_no_prescription(self) -> None:
        async with await self._client() as client:
            res = await client.post("/api/v1/l3-aide/algorithms/27_ndvi/run")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body.get("success"))
        self.assertNotIn("公斤", body.get("runComment") or "")
        self.assertIn("不是处方", body.get("runComment") or "")


class TestInterpretFromStats(unittest.TestCase):
    def test_does_not_run_algorithm(self) -> None:
        from unittest.mock import patch

        from common.l3_aide.service import interpret_from_stats

        with patch("common.l3_aide.service.run_algorithm_testdata") as mocked:
            out = interpret_from_stats("27_ndvi", {"min": 0.1, "max": 0.8, "mean": 0.4})
        mocked.assert_not_called()
        self.assertTrue(out["success"])
        self.assertEqual(out["algorithmId"], "27_ndvi")
        self.assertEqual(out["stats"]["mean"], 0.4)
        self.assertTrue(out["runComment"])
        self.assertIn("NDVI", out["prompt"]["system"])
        self.assertTrue(out["llm"]["fallback"])

    def test_unknown_algorithm_raises(self) -> None:
        from common.l3_aide.service import interpret_from_stats

        with self.assertRaises(KeyError):
            interpret_from_stats("not_an_algorithm", {"min": 0.0, "max": 1.0, "mean": 0.5})


class TestAideInterpretRouter(unittest.IsolatedAsyncioTestCase):
    async def _client(self):
        import httpx
        from fastapi import FastAPI

        from common.l3_aide.router import router

        app = FastAPI()
        app.include_router(router)
        transport = httpx.ASGITransport(app=app)
        return httpx.AsyncClient(transport=transport, base_url="http://test")

    async def test_interpret_unknown_404(self) -> None:
        async with await self._client() as client:
            res = await client.post(
                "/api/v1/l3-aide/algorithms/not_an_algorithm/interpret",
                json={"stats": {"min": 0.1, "max": 0.8, "mean": 0.4}},
            )
        self.assertEqual(res.status_code, 404)

    async def test_interpret_l0_uses_output_summary(self) -> None:
        async with await self._client() as client:
            res = await client.post(
                "/api/v1/l3-aide/algorithms/01_flight_planning/interpret",
                json={"stats": {"min": 0.1, "max": 0.8, "mean": 0.4}},
            )
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body.get("success"))
        self.assertEqual(body.get("algorithmId"), "01_flight_planning")
        self.assertIn("不是处方", body.get("runComment") or "")

    async def test_interpret_uses_posted_stats(self) -> None:
        from unittest.mock import patch

        async with await self._client() as client:
            with patch("common.l3_aide.service.run_algorithm_testdata") as mocked:
                res = await client.post(
                    "/api/v1/l3-aide/algorithms/27_ndvi/interpret",
                    json={
                        "data": {
                            "min": 0.1,
                            "max": 0.8,
                            "mean": 0.4,
                            "path": "/var/outputs/job/ndvi.tif",
                        },
                        "files": {"ndvi_tif": "/var/outputs/job/ndvi.tif"},
                    },
                )
        mocked.assert_not_called()
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body.get("success"))
        self.assertIn("0.40", body.get("runComment") or "")
        self.assertIn("不是处方", body.get("runComment") or "")
        self.assertNotIn("公斤", body.get("runComment") or "")
        user = (body.get("prompt") or {}).get("user") or ""
        self.assertIn("NDVI均值", user)
        self.assertIn('"mean": 0.4', user)
        self.assertNotIn(".tif", user)

    async def test_interpret_uses_posted_prompt_override(self) -> None:
        async with await self._client() as client:
            res = await client.post(
                "/api/v1/l3-aide/algorithms/27_ndvi/interpret",
                json={
                    "data": {"min": 0.1, "max": 0.8, "mean": 0.4},
                    "prompt": {
                        "system": "你是自定义系统提示。不要改推其他算法。",
                        "user": '{"id":"27_ndvi","task":"自定义用户提示"}',
                    },
                },
            )
        self.assertEqual(res.status_code, 200)
        prompt = (res.json().get("prompt") or {})
        self.assertIn("自定义系统提示", prompt.get("system") or "")
        self.assertIn("自定义用户提示", prompt.get("user") or "")


class TestLayerCatalog(unittest.TestCase):
    def test_max_s810_is_not_called_hyperspectral(self) -> None:
        import re

        text = (
            Path(__file__).parents[1] / "common" / "l3_aide" / "layers.py"
        ).read_text(encoding="utf-8")
        leaked = [
            sentence.strip()
            for sentence in re.split(r"[。！？\n]", text)
            if "MAX-S810" in sentence and "高光谱" in sentence
        ]
        self.assertEqual(leaked, [])

    def test_processing_layers_share_algorithm_local_guards(self) -> None:
        from common.l3_aide.layers import get_layer

        for layer_id in ("l0", "l0l1", "l2", "l3"):
            layer = get_layer(layer_id)
            assert layer is not None
            blob = " ".join(layer["mustNot"])
            self.assertIn("不得推荐其他算法", blob, layer_id)
            self.assertIn("不得输出处方或业务决策", blob, layer_id)

    def test_four_processing_layers(self) -> None:
        from common.l3_aide.layers import get_layer, list_layers

        rows = list_layers()
        self.assertEqual([row["id"] for row in rows], ["l0", "l0l1", "l2", "l3"])
        self.assertEqual(rows[0]["title"], "采集质检")
        self.assertIn("放行闸", rows[0]["benefit"])
        l3 = get_layer("l3")
        assert l3 is not None
        self.assertTrue(l3["traditional"]["headline"].startswith("只看彩图"))
        self.assertIn("不得推荐其他算法", "".join(l3["context"]))
        self.assertIn("统计值", "".join(l3["context"]))
        self.assertTrue(l3.get("llmIo"))
        self.assertIn("min / max / mean", " ".join(l3["llmIo"]["input"]))
        self.assertEqual(l3["jobs"][-1]["who"], "大模型")
        self.assertEqual(l3["demoAlgorithmId"], "27_ndvi")
        self.assertIn("不是处方", l3["ai"]["markdown"])
        self.assertIsNone(get_layer("not-a-layer"))


class TestLayerNarrator(unittest.TestCase):
    def test_prompt_excludes_raster(self) -> None:
        from common.l3_aide.narrator import build_layer_llm_messages

        messages = build_layer_llm_messages(
            {
                "id": "l0",
                "level": "L0",
                "title": "采集质检",
                "question": "要不要整包送进辐射？",
                "traditional": {"headline": "固定流水线", "bullets": ["全开"]},
                "ai": {"headline": "先质检", "markdown": "这不是处方。"},
                "mustNot": ["不得把立方体送进大模型。"],
                "evidence": {
                    "demoAlgorithmId": "04_flight_qc",
                    "success": True,
                    "previewUrl": "/api/v1/console/outputs/job/qc.png",
                    "data": {"passed": True, "path": "/var/outputs/job/qc.tif"},
                },
            }
        )
        blob = json.dumps(messages, ensure_ascii=False)
        self.assertIn("采集质检", blob)
        self.assertIn("固定流水线", blob)
        self.assertNotIn(".tif", blob)
        self.assertNotIn("qc.png", blob)
        self.assertNotIn("/var/", blob)

    def test_prescription_falls_back(self) -> None:
        from common.l3_aide.narrator import apply_layer_narrative

        case = {
            "id": "l3",
            "level": "L3",
            "title": "指数与识别",
            "question": "要不要补氮？",
            "traditional": {"headline": "看 NDVI", "bullets": ["绿度阈值"]},
            "ai": {"headline": "主看 NDRE", "markdown": "建议巡田。这不是处方。"},
            "mustNot": ["不得输出施肥剂量。"],
        }

        def bad(_messages: list[dict[str, str]]) -> str:
            return json.dumps({"headline": "补氮", "aiMarkdown": "建议 12 公斤/亩。"}, ensure_ascii=False)

        ai, llm, _prompt = apply_layer_narrative(case, {}, llm_client=bad)
        self.assertTrue(llm["fallback"])
        self.assertIn("不是处方", ai["markdown"])
        self.assertNotIn("公斤", ai["markdown"])


class TestLayerRouter(unittest.IsolatedAsyncioTestCase):
    async def _client(self):
        import httpx
        from fastapi import FastAPI

        from common.l3_aide.router import router

        app = FastAPI()
        app.include_router(router)
        transport = httpx.ASGITransport(app=app)
        return httpx.AsyncClient(transport=transport, base_url="http://test")

    async def test_list_and_unknown(self) -> None:
        async with await self._client() as client:
            listed = await client.get("/api/v1/l3-aide/layers")
            missing = await client.get("/api/v1/l3-aide/layers/not-a-layer")
        self.assertEqual(listed.status_code, 200)
        ids = [row["id"] for row in listed.json()["layers"]]
        self.assertEqual(ids, ["l0", "l0l1", "l2", "l3"])
        self.assertEqual(missing.status_code, 404)

    async def test_run_l0_does_not_need_catalog_algorithm(self) -> None:
        from unittest.mock import AsyncMock, patch

        fake = {
            "success": True,
            "message": "",
            "data": {"passed": True, "saturated_ratio": 0.002},
            "files": {"report_json": "/var/outputs/job/qc.json"},
            "files_http": {"preview_png": {"url": "/api/v1/console/outputs/job/qc.png"}},
        }
        async with await self._client() as client:
            with patch(
                "common.l3_aide.service.run_algorithm_testdata",
                new=AsyncMock(return_value=fake),
            ) as mocked:
                res = await client.post("/api/v1/l3-aide/layers/l0/run", json={})
        mocked.assert_awaited_once()
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body.get("success"))
        self.assertEqual(body["layerId"], "l0")
        self.assertIn("流水线", body["traditional"]["headline"])
        self.assertIn("不是处方", body["ai"]["markdown"])
        self.assertTrue(body["llm"]["fallback"])
        self.assertEqual(body["llm"]["reason"], "no_key")
        self.assertTrue(body["demo"]["success"])
        user = (body.get("prompt") or {}).get("user") or ""
        self.assertNotIn(".tif", user)
        self.assertNotIn("/var/", user)


if __name__ == "__main__":
    unittest.main()

