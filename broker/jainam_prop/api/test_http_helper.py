"""Unit tests for Jainam HTTP helper."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from typing import Dict, Optional
from unittest.mock import MagicMock

import httpx
import pytest

from broker.jainam_prop.api import http_helper


@pytest.fixture
def mock_client(monkeypatch):
    client = MagicMock()
    monkeypatch.setattr(http_helper, "get_httpx_client", lambda: client)
    monkeypatch.setattr(http_helper, "get_jainam_base_url", lambda: "https://api.jainam.test")
    return client


def _build_response(
    method: str,
    endpoint: str,
    status: int,
    json_body: dict,
    headers: Optional[Dict[str, str]] = None,
    base_url: str = "https://api.jainam.test",
) -> httpx.Response:
    request = httpx.Request(method, f"{base_url}{endpoint}")
    return httpx.Response(status, request=request, json=json_body, headers=headers)


def test_successful_request_sets_status(mock_client):
    response = _build_response("GET", "/interactive/orders", 200, {"ok": True})
    mock_client.request.return_value = response

    result = http_helper.get_api_response("/interactive/orders", "Bearer token")

    assert result == {"ok": True}
    assert result.status == 200
    assert response.status == 200
    mock_client.request.assert_called_once()
    method, url = mock_client.request.call_args[0][:2]
    assert method == "GET"
    assert url == "https://api.jainam.test/interactive/orders"
    headers = mock_client.request.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer token"


def test_retries_on_500(monkeypatch, mock_client):
    first = _build_response("GET", "/interactive/orders", 500, {"status": "error"})
    second = _build_response("GET", "/interactive/orders", 200, {"status": "success"})
    mock_client.request.side_effect = [first, second]

    sleep_calls = []

    def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr(http_helper.time, "sleep", fake_sleep)

    result = http_helper.get_api_response(
        "/interactive/orders",
        "Bearer token",
        retries=2,
        backoff_min=0.25,
        backoff_max=2.0,
    )

    assert result["status"] == "success"
    assert mock_client.request.call_count == 2
    assert sleep_calls == [0.25]


def test_no_retry_on_client_error(monkeypatch, mock_client):
    client_error = _build_response("GET", "/interactive/orders", 400, {"status": "error"})
    mock_client.request.return_value = client_error

    sleep_mock = MagicMock()
    monkeypatch.setattr(http_helper.time, "sleep", sleep_mock)

    result = http_helper.get_api_response(
        "/interactive/orders",
        "Bearer token",
        retries=3,
    )

    assert result.status == 400
    sleep_mock.assert_not_called()
    mock_client.request.assert_called_once()


def test_retry_on_timeout(monkeypatch, mock_client):
    request_obj = httpx.Request("GET", "https://api.jainam.test/interactive/orders")
    timeout_error = httpx.TimeoutException("timeout", request=request_obj)
    success = _build_response("GET", "/interactive/orders", 200, {"status": "success"})
    mock_client.request.side_effect = [timeout_error, success]

    sleep_calls = []
    monkeypatch.setattr(http_helper.time, "sleep", lambda delay: sleep_calls.append(delay))

    result = http_helper.get_api_response(
        "/interactive/orders",
        "Bearer token",
        retries=2,
        backoff_min=0.5,
        backoff_max=1.0,
    )

    assert result["status"] == "success"
    assert sleep_calls == [0.5]
    assert mock_client.request.call_count == 2


def test_retry_after_header_overrides_backoff(monkeypatch, mock_client):
    rate_limited = _build_response(
        "GET",
        "/interactive/orders",
        429,
        {"status": "rate_limited"},
        headers={"Retry-After": "3"},
    )
    success = _build_response("GET", "/interactive/orders", 200, {"status": "success"})
    mock_client.request.side_effect = [rate_limited, success]

    delays: list[float] = []
    monkeypatch.setattr(http_helper.time, "sleep", lambda delay: delays.append(delay))

    result = http_helper.get_api_response(
        "/interactive/orders",
        "Bearer token",
        retries=2,
        backoff_min=0.1,
        backoff_max=0.2,
    )

    assert result["status"] == "success"
    assert pytest.approx(delays[0], rel=0.0, abs=0.001) == 3.0
    assert mock_client.request.call_count == 2


def test_retry_after_http_date(monkeypatch, mock_client):
    fixed_now = datetime(2025, 10, 12, 12, 0, 0, tzinfo=timezone.utc)
    header_value = format_datetime(fixed_now + timedelta(seconds=5))

    class _FixedDateTime:
        @staticmethod
        def now(tz=None):
            if tz is None:
                return fixed_now.replace(tzinfo=None)
            return fixed_now

    monkeypatch.setattr(http_helper, "datetime", _FixedDateTime)

    rate_limited = _build_response(
        "GET",
        "/interactive/orders",
        429,
        {"status": "retry"},
        headers={"Retry-After": header_value},
    )
    success = _build_response("GET", "/interactive/orders", 200, {"status": "ok"})
    mock_client.request.side_effect = [rate_limited, success]

    delays: list[float] = []
    monkeypatch.setattr(http_helper.time, "sleep", lambda delay: delays.append(delay))

    result = http_helper.get_api_response(
        "/interactive/orders",
        "Bearer token",
        retries=2,
        backoff_min=0.25,
        backoff_max=1.0,
    )

    assert result.status == 200
    assert delays and pytest.approx(delays[0], rel=0.0, abs=1e-6) == 5.0
    assert mock_client.request.call_count == 2


def test_retry_after_invalid_value_falls_back(monkeypatch, mock_client):
    rate_limited = _build_response(
        "GET",
        "/interactive/orders",
        429,
        {"status": "retry"},
        headers={"Retry-After": "invalid"},
    )
    success = _build_response("GET", "/interactive/orders", 200, {"status": "ok"})
    mock_client.request.side_effect = [rate_limited, success]

    delays: list[float] = []
    monkeypatch.setattr(http_helper.time, "sleep", lambda delay: delays.append(delay))

    result = http_helper.get_api_response(
        "/interactive/orders",
        "Bearer token",
        retries=2,
        backoff_min=0.4,
        backoff_max=1.0,
    )

    assert result.status == 200
    assert delays == [0.4]
    assert mock_client.request.call_count == 2


def test_structured_logging_contains_metadata(caplog, mock_client):
    response = _build_response("POST", "/interactive/orders", 200, {"status": "ok"})
    mock_client.request.return_value = response

    caplog.set_level(logging.INFO, logger=http_helper.logger.name)

    http_helper.get_api_response(
        "/interactive/orders",
        "Bearer token",
        method="POST",
        payload={"order": "data"},
    )

    records = [record for record in caplog.records if record.levelno == logging.INFO]
    assert records, "Expected at least one info log entry"
    log_record = records[-1]
    assert getattr(log_record, "endpoint") == "/interactive/orders"
    assert getattr(log_record, "method") == "POST"
    assert getattr(log_record, "status") == 200
    assert getattr(log_record, "attempt") == 1


def test_custom_base_url_overrides_config(mock_client):
    custom_base = "https://staging.jainam.test/api/"
    response = _build_response(
        "GET",
        "/interactive/orders",
        200,
        {"ok": True},
        base_url="https://staging.jainam.test/api",
    )
    mock_client.request.return_value = response

    result = http_helper.get_api_response(
        "/interactive/orders",
        "Bearer token",
        base_url=custom_base,
    )

    assert result.status == 200
    method, url = mock_client.request.call_args[0][:2]
    assert method == "GET"
    assert url == "https://staging.jainam.test/api/interactive/orders"
