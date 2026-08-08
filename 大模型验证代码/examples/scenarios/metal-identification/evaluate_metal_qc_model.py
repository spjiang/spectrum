#!/usr/bin/env python3
"""
金属质检 LoRA 微调模型验证脚本

从训练 JSONL 中抽取测试样本，对比模型输出与标准答案的关键字段（质检结论、处置建议）。

用法:
    # 先用 LLaMA-Factory 训练完成，再验证
    python examples/scenarios/metal-identification/evaluate_metal_qc_model.py \
        --lora-path saves/metal-qc-qwen7b-lora \
        --test-jsonl examples/scenarios/metal-identification/training/metal_sft_train_full.jsonl \
        --num-samples 20

    # 使用 LLaMA-Factory CLI 交互式验证（推荐）
    llamafactory-cli chat examples/scenarios/metal-identification/llamafactory/train_metal_lora.yaml
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_test_cases(jsonl_path: Path, num_samples: int, seed: int = 42) -> list[dict]:
    """从 JSONL 随机抽取测试用例。"""
    import random

    records = []
    with jsonl_path.open(encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    rng = random.Random(seed)
    if num_samples >= len(records):
        return records
    return rng.sample(records, num_samples)


def extract_field(text: str, field: str) -> str | None:
    """从助手回复中提取关键字段。"""
    pattern = rf"{field}[:：]\s*([^\n。]+)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None


def compare_outputs(expected: str, actual: str) -> dict:
    """对比质检结论和处置建议。"""
    fields = ["质检结论", "处置建议", "合格等级"]
    result = {}
    for field in fields:
        exp_val = extract_field(expected, field)
        act_val = extract_field(actual, field)
        result[field] = {
            "expected": exp_val,
            "actual": act_val,
            "match": exp_val == act_val if exp_val and act_val else False,
        }
    return result


def run_inference(
    base_model: str,
    lora_path: str,
    messages: list[dict],
    max_new_tokens: int = 512,
) -> str:
    """加载基座 + LoRA 并推理。"""
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(model, lora_path)
    model.eval()

    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.1,
            do_sample=False,
        )
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # 截取 assistant 回复部分
    if "assistant" in full_text.lower():
        parts = re.split(r"assistant\s*", full_text, flags=re.IGNORECASE)
        return parts[-1].strip() if len(parts) > 1 else full_text
    return full_text


def print_report(results: list[dict]) -> None:
    """打印验证报告。"""
    total = len(results)
    if total == 0:
        print("无测试样本。")
        return

    qc_correct = sum(1 for r in results if r["comparison"]["质检结论"]["match"])
    disp_correct = sum(1 for r in results if r["comparison"]["处置建议"]["match"])

    print("\n" + "=" * 60)
    print("金属质检 LoRA 模型验证报告")
    print("=" * 60)
    print(f"测试样本数：{total}")
    print(f"质检结论准确率：{qc_correct}/{total} ({100 * qc_correct / total:.1f}%)")
    print(f"处置建议准确率：{disp_correct}/{total} ({100 * disp_correct / total:.1f}%)")
    print("-" * 60)

    for i, r in enumerate(results[:5], 1):
        print(f"\n[样本 {i}]")
        comp = r["comparison"]
        qc = comp["质检结论"]
        status = "✓" if qc["match"] else "✗"
        print(f"  {status} 质检结论：期望={qc['expected']}，实际={qc['actual']}")
        if not qc["match"]:
            print(f"    模型完整回复：\n{r['model_output'][:300]}...")

    if total > 5:
        print(f"\n... 其余 {total - 5} 条样本省略显示")


def main() -> None:
    parser = argparse.ArgumentParser(description="验证金属质检 LoRA 微调效果")
    parser.add_argument(
        "--base-model",
        default="Qwen/Qwen2.5-7B-Instruct",
        help="基座模型路径或 HuggingFace ID",
    )
    parser.add_argument(
        "--lora-path",
        default=None,
        help="LoRA 权重目录（LLaMA-Factory output_dir）",
    )
    parser.add_argument(
        "--test-jsonl",
        type=Path,
        default=Path("examples/scenarios/metal-identification/training/metal_sft_train_full.jsonl"),
    )
    parser.add_argument("--num-samples", type=int, default=20, help="随机抽取测试样本数")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry-run", action="store_true", help="仅打印测试用例，不加载模型")
    args = parser.parse_args()

    test_cases = load_test_cases(args.test_jsonl, args.num_samples, args.seed)
    print(f"已加载 {len(test_cases)} 条测试样本（来源：{args.test_jsonl}）")

    if args.dry_run:
        for i, case in enumerate(test_cases[:3], 1):
            assistant = next(m["content"] for m in case["messages"] if m["role"] == "assistant")
            qc = extract_field(assistant, "质检结论")
            print(f"  [{i}] 标准答案质检结论：{qc}")
        return

    if not args.lora_path:
        raise SystemExit("错误：非 --dry-run 模式必须指定 --lora-path")

    results = []
    for case in test_cases:
        messages = [m for m in case["messages"] if m["role"] != "assistant"]
        expected = next(m["content"] for m in case["messages"] if m["role"] == "assistant")
        model_output = run_inference(args.base_model, args.lora_path, messages)
        comparison = compare_outputs(expected, model_output)
        results.append({
            "comparison": comparison,
            "model_output": model_output,
        })

    print_report(results)


if __name__ == "__main__":
    main()
