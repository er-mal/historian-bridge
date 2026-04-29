"""Error mapping for the gateway."""
from __future__ import annotations

from typing import Any


class GatewayError(Exception):
    """Base for gateway-level errors."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str, *, code: str | None = None, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code

    def to_problem(self) -> dict[str, Any]:
        return {"type": f"about:blank#{self.code}", "title": self.code, "status": self.status_code, "detail": self.message}


class BadRequest(GatewayError):
    status_code = 400
    code = "bad_request"


class BackendUnavailable(GatewayError):
    status_code = 503
    code = "backend_unavailable"


class NotImplementedYet(GatewayError):
    status_code = 501
    code = "not_implemented"
