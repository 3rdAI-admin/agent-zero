from __future__ import annotations

from dataclasses import dataclass, field
import threading
import time
from typing import Any


@dataclass
class StartupPhase:
    required: bool
    status: str = "pending"
    detail: str = ""
    error: str = ""
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "required": self.required,
            "status": self.status,
            "detail": self.detail,
            "error": self.error,
            "updated_at": self.updated_at,
        }


class StartupState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._phases: dict[str, StartupPhase] = {}

    def reset(self) -> None:
        with self._lock:
            self._phases = {}

    def mark_running(self, name: str, *, required: bool, detail: str = "") -> None:
        self._set_phase(name, required=required, status="running", detail=detail)

    def mark_ready(self, name: str, *, detail: str = "") -> None:
        self._set_phase(name, status="ready", detail=detail, error="")

    def mark_failed(self, name: str, *, error: str, detail: str = "") -> None:
        self._set_phase(name, status="failed", detail=detail, error=error)

    def update_detail(self, name: str, *, detail: str) -> None:
        self._set_phase(name, detail=detail)

    def snapshot(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            return {
                name: phase.to_dict()
                for name, phase in sorted(self._phases.items(), key=lambda item: item[0])
            }

    def ready(self) -> tuple[bool, dict[str, dict[str, Any]]]:
        phases = self.snapshot()
        is_ready = all(
            phase["status"] == "ready"
            for phase in phases.values()
            if phase["required"]
        )
        return is_ready, phases

    def _set_phase(
        self,
        name: str,
        *,
        required: bool | None = None,
        status: str | None = None,
        detail: str | None = None,
        error: str | None = None,
    ) -> None:
        with self._lock:
            phase = self._phases.get(name)
            if phase is None:
                phase = StartupPhase(required=required if required is not None else False)
                self._phases[name] = phase

            if required is not None:
                phase.required = required
            if status is not None:
                phase.status = status
            if detail is not None:
                phase.detail = detail
            if error is not None:
                phase.error = error
            phase.updated_at = time.time()
