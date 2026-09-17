"""兼容 DeepSeek / OpenAI 的 Chat Completions 客户端；密钥只来自本次请求。"""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from typing import Any, Callable

import certifi

LlmClient = Callable[[list[dict[str, str]]], str]

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TIMEOUT = 60


def ssl_context() -> ssl.SSLContext:
    """用 certifi 根证书，避免本机 Python 默认 CA 校验失败。"""
    return ssl.create_default_context(cafile=certifi.where())


def _http_error_message(code: int, body: str) -> str:
    """把厂商错误转成可展示的中文，避免把整段 JSON 甩给页面。"""
    text = (body or "").lower()
    if code == 402 or ("insufficient" in text and "balance" in text):
        return "模型账户余额不足，请到服务商充值后再试。"
    if code in (401, 403) or "invalid api key" in text or "authentication" in text:
        return "模型密钥无效或未授权，请检查右上角「大模型配置」。"
    if code == 429:
        return "模型调用过于频繁，请稍后再试。"
    snippet = (body or "").replace("\n", " ").strip()[:180]
    if snippet:
        return f"模型 HTTP {code}: {snippet}"
    return f"模型 HTTP {code}"


def extract_message_text(raw_body: str) -> str:
    """从 Chat Completions 响应取出正文，并去掉 markdown 围栏。"""
    payload = json.loads(raw_body)
    choices = payload.get("choices") or []
    if not choices:
        raise ValueError("模型响应没有 choices")
    content = str((choices[0].get("message") or {}).get("content") or "").strip()
    if content.startswith("```"):
        lines = content.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()
    if not content:
        raise ValueError("模型响应正文为空")
    return content


def _chat_url(base_url: str) -> str:
    """补全 /v1/chat/completions，避免调用方漏写路径。"""
    root = base_url.strip().rstrip("/")
    if root.endswith("/chat/completions"):
        return root
    if root.endswith("/v1"):
        return root + "/chat/completions"
    return root + "/v1/chat/completions"


def complete_chat(
    messages: list[dict[str, str]],
    *,
    base_url: str,
    model: str,
    api_key: str,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """同步调用一次聊天补全，返回助手文本。"""
    body = json.dumps(
        {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        _chat_url(base_url),
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:800]
        raise OSError(_http_error_message(exc.code, detail)) from exc
    except urllib.error.URLError as exc:
        raise OSError(f"模型连接失败: {exc.reason}") from exc
    return extract_message_text(raw)


def client_from_config(config: dict[str, Any] | None) -> LlmClient | None:
    """有密钥才构造客户端；空配置返回 None，走模板。"""
    if not config:
        return None
    api_key = str(config.get("apiKey") or config.get("api_key") or "").strip()
    if not api_key:
        return None
    base_url = str(config.get("baseUrl") or config.get("base_url") or DEFAULT_BASE_URL).strip()
    model = str(config.get("model") or DEFAULT_MODEL).strip() or DEFAULT_MODEL
    timeout = float(config.get("timeout") or DEFAULT_TIMEOUT)

    def _call(messages: list[dict[str, str]]) -> str:
        return complete_chat(
            messages,
            base_url=base_url or DEFAULT_BASE_URL,
            model=model,
            api_key=api_key,
            timeout=timeout,
        )

    return _call
