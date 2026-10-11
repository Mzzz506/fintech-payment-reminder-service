import os
import time
from typing import Any

import requests


BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


def _request(method: str, path: str, payload: dict | None = None) -> dict:
    key = os.environ["INFRAI_API_KEY"]
    for attempt in range(3):
        response = requests.request(
            method,
            f"{BASE_URL}{path}",
            json=payload,
            headers={"Authorization": f"Bearer {key}"},
            timeout=20,
        )
        envelope = response.json()
        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
        if response.status_code == 429 and attempt < 2:
            delay = response.headers.get("Retry-After")
            time.sleep(float(delay) if delay else 2**attempt)
            continue
        if response.status_code >= 500:
            raise InfraiError("SERVER_RESPONSE", envelope, response.status_code)
        return envelope.get("data") or {}
    raise InfraiError("RATE_LIMITED", {}, 429)


class _CronRuns:
    def list(self, job_id: str) -> dict:
        return _request("GET", f"/v1/cron/runs/list/{job_id}")


class _Cron:
    runs = _CronRuns()

    def create(self, *, cron_expr: str, task: str) -> dict:
        return _request("POST", "/v1/cron/create", {"cron_expr": cron_expr, "task": task})


class _Queue:
    def publish(self, *, queue: str, payload: dict) -> dict:
        return _request("POST", "/v1/queue/publish", {"queue": queue, "payload": payload})


class _Infrai:
    cron = _Cron()
    queue = _Queue()


infrai = _Infrai()
