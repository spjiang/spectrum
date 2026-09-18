from __future__ import annotations

import json
import logging
from typing import Any, Callable

import pika

from app.config import get_settings

log = logging.getLogger(__name__)

QUEUE_JOBS = "mosaic.jobs"
QUEUE_CONTROL = "mosaic.control"
QUEUE_PROGRESS = "mosaic.progress"
QUEUE_EVENTS = "mosaic.events"


class MQPublisher:
    def __init__(self, url: str | None = None) -> None:
        self.url = url or get_settings().rabbitmq_url
        self._conn: pika.BlockingConnection | None = None

    def _channel(self):
        if self._conn is None or self._conn.is_closed:
            self._conn = pika.BlockingConnection(pika.URLParameters(self.url))
        ch = self._conn.channel()
        for q in (QUEUE_JOBS, QUEUE_CONTROL, QUEUE_PROGRESS, QUEUE_EVENTS, f"{QUEUE_JOBS}.dlq"):
            ch.queue_declare(queue=q, durable=True)
        return ch

    def publish(self, queue: str, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        ch = self._channel()
        ch.basic_publish(
            exchange="",
            routing_key=queue,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )

    def publish_job(self, payload: dict[str, Any]) -> None:
        self.publish(QUEUE_JOBS, payload)

    def publish_control(self, payload: dict[str, Any]) -> None:
        self.publish(QUEUE_CONTROL, payload)

    def close(self) -> None:
        if self._conn and self._conn.is_open:
            self._conn.close()


def check_rabbitmq(url: str | None = None) -> str:
    try:
        conn = pika.BlockingConnection(pika.URLParameters(url or get_settings().rabbitmq_url))
        conn.close()
        return "ok"
    except Exception as exc:  # noqa: BLE001
        return f"error: {exc}"


class FakeMQPublisher:
    """测试用。"""

    def __init__(self) -> None:
        self.jobs: list[dict] = []
        self.controls: list[dict] = []

    def publish_job(self, payload: dict[str, Any]) -> None:
        self.jobs.append(payload)

    def publish_control(self, payload: dict[str, Any]) -> None:
        self.controls.append(payload)

    def close(self) -> None:
        return None
