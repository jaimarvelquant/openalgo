"""HTTP helper with retry logic for Jainam Prop API."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, Optional
from urllib.parse import urlsplit

import httpx

from utils.httpx_client import get_httpx_client
from utils.logging import get_logger
from broker.jainam_prop.api.config import (
    get_jainam_base_url,
    JAINAM_RETRY_ATTEMPTS,
    JAINAM_RETRY_BACKOFF_MIN,
    JAINAM_RETRY_BACKOFF_MAX,
)

logger = get_logger(__name__)

_RETRY_STATUS_CODES = {429}
_RETRY_AFTER_STATUS_CODES = {429, 503}


class HttpResponsePayload(dict):
    """Dictionary wrapper that exposes HTTP metadata."""

    __slots__ = ("status", "raw_response")

    def __init__(self, data: Dict[str, Any], status: int, raw_response: httpx.Response) -> None:
        super().__init__(data)
        self.status = status
        self.raw_response = raw_response


def _extract_request_kwargs(
    method: str,
    payload: Optional[Dict[str, Any]],
) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Optional[Any], Optional[Dict[str, str]], Optional[float]]:
    """Normalize payload into params/json/content/header/timeout components."""

    params: Optional[Dict[str, Any]] = None
    json_body: Optional[Dict[str, Any]] = None
    content: Optional[Any] = None
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[float] = None

    if not isinstance(payload, dict):
        if payload is not None and method in {"GET", "DELETE"}:
            params = payload  # type: ignore[assignment]
        else:
            json_body = payload  # type: ignore[assignment]
        return params, json_body, content, headers, timeout

    if any(key.startswith("_") for key in payload):
        params = payload.get("_params")
        json_body = payload.get("_json")
        content = payload.get("_content")
        headers = payload.get("_headers")
        timeout = payload.get("_timeout")
    else:
        if method in {"GET", "DELETE"}:
            params = payload
        else:
            json_body = payload

    return params, json_body, content, headers, timeout


def _should_retry(status_code: int) -> bool:
    return status_code >= 500 or status_code in _RETRY_STATUS_CODES


def _compute_backoff_delay(attempt: int, backoff_min: float, backoff_max: float) -> float:
    delay = backoff_min * (2 ** (attempt - 1))
    return min(delay, backoff_max)


def _parse_retry_after(header_value: Optional[str]) -> Optional[float]:
    if not header_value:
        return None

    header_value = header_value.strip()
    if not header_value:
        return None

    try:
        seconds = int(header_value)
        if seconds >= 0:
            return float(seconds)
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(header_value)
        except (TypeError, ValueError):
            return None

        if retry_at is None:
            return None

        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)

        delta = (retry_at - datetime.now(timezone.utc)).total_seconds()
        if delta > 0:
            return float(delta)

    return None


def _resolve_retry_delay(
    response: httpx.Response,
    attempt: int,
    backoff_min: float,
    backoff_max: float,
) -> float:
    if response.status_code in _RETRY_AFTER_STATUS_CODES:
        retry_after = _parse_retry_after(response.headers.get("Retry-After"))
        if retry_after is not None:
            return max(0.0, retry_after)

    return _compute_backoff_delay(attempt, backoff_min, backoff_max)


def _resolve_endpoint_and_url(endpoint: str, base_url: Optional[str]) -> tuple[str, str]:
    """Determine logging endpoint value and absolute request URL."""

    if endpoint.startswith(("http://", "https://")):
        parts = urlsplit(endpoint)
        path = parts.path or "/"
        query = f"?{parts.query}" if parts.query else ""
        sanitized_endpoint = f"{path}{query}"
        return sanitized_endpoint, endpoint

    sanitized_endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
    effective_base = (base_url or get_jainam_base_url()).rstrip("/")
    if not effective_base:
        raise ValueError("Jainam base URL cannot be empty")

    return sanitized_endpoint, f"{effective_base}{sanitized_endpoint}"


def get_api_response(
    endpoint: str,
    auth: str,
    method: str = "GET",
    payload: Optional[Dict[str, Any]] = None,
    retries: int = JAINAM_RETRY_ATTEMPTS,
    backoff_min: float = JAINAM_RETRY_BACKOFF_MIN,
    backoff_max: float = JAINAM_RETRY_BACKOFF_MAX,
    base_url: Optional[str] = None,
) -> HttpResponsePayload:
    """Execute HTTP request with retry logic and structured logging."""

    method_upper = method.upper()
    total_attempts = max(1, retries)

    params, json_body, content, extra_headers, timeout_override = _extract_request_kwargs(method_upper, payload)

    base_headers: Dict[str, str] = {"Content-Type": "application/json"}
    if auth:
        base_headers["Authorization"] = auth
    if extra_headers:
        base_headers.update(extra_headers)

    sanitized_endpoint, request_url = _resolve_endpoint_and_url(endpoint, base_url)

    client = get_httpx_client()
    last_exception: Optional[Exception] = None

    for attempt in range(1, total_attempts + 1):
        started_at = time.monotonic()
        try:
            response = client.request(
                method_upper,
                request_url,
                headers=base_headers,
                params=params,
                json=json_body,
                content=content,
                timeout=timeout_override,
            )
        except (httpx.TimeoutException, httpx.RequestError) as exc:
            latency = time.monotonic() - started_at
            logger.warning(
                "Jainam HTTP %s network error", method_upper,
                extra={
                    "endpoint": sanitized_endpoint,
                    "method": method_upper,
                    "status": "exception",
                    "latency": round(latency, 4),
                    "attempt": attempt,
                    "error": str(exc),
                },
            )
            last_exception = exc
            if attempt >= total_attempts:
                raise

            delay = _compute_backoff_delay(attempt, backoff_min, backoff_max)
            time.sleep(delay)
            continue

        latency = time.monotonic() - started_at
        status_code = response.status_code

        logger.info(
            "Jainam HTTP %s", method_upper,
            extra={
                "endpoint": sanitized_endpoint,
                "method": method_upper,
                "status": status_code,
                "latency": round(latency, 4),
                "attempt": attempt,
            },
        )

        if _should_retry(status_code) and attempt < total_attempts:
            delay = _resolve_retry_delay(response, attempt, backoff_min, backoff_max)
            logger.warning(
                "Retrying Jainam HTTP %s due to status %s", method_upper, status_code,
                extra={
                    "endpoint": sanitized_endpoint,
                    "method": method_upper,
                    "status": status_code,
                    "latency": round(latency, 4),
                    "attempt": attempt,
                    "retry_delay": round(delay, 4),
                },
            )
            time.sleep(delay)
            continue

        try:
            data = response.json()
        except ValueError:
            data = {"raw_response": response.text}

        response.status = status_code  # Maintain backward compatibility
        return HttpResponsePayload(data, status_code, response)

    if last_exception:
        raise last_exception

    raise RuntimeError("get_api_response reached unexpected termination state")
