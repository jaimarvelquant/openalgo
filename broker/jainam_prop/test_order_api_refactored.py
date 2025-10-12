"""Integration-style tests validating Jainam order API helper adoption."""

from __future__ import annotations

from unittest.mock import patch

import json
import httpx
import pytest

from broker.jainam_prop.api.order_api import OrderAPIClient, cancel_order_api
from broker.jainam_prop.api.http_helper import HttpResponsePayload


def _helper_response(method: str, endpoint: str, data: dict, status: int = 200) -> HttpResponsePayload:
    request = httpx.Request(method, f"https://api.jainam.test{endpoint}")
    response = httpx.Response(status, request=request, json=data)
    return HttpResponsePayload(data, status, response)


@pytest.fixture
def helper_patch():
    with patch("broker.jainam_prop.api.base_client.get_api_response") as mocked:
        yield mocked


def test_order_book_uses_helper_params(helper_patch):
    helper_patch.return_value = _helper_response("GET", "/interactive/orders", {"type": "success", "orders": []})

    client = OrderAPIClient(auth_token="Bearer abc123")
    result = client.get_orderbook(client_id="*****")

    assert result["type"] == "success"
    helper_patch.assert_called_once()
    endpoint, auth = helper_patch.call_args[0][:2]
    method = helper_patch.call_args.kwargs.get("method")
    payload = helper_patch.call_args.kwargs["payload"]

    assert endpoint == "/interactive/orders"
    assert auth == "Bearer abc123"
    assert method == "GET"
    assert payload["_params"] == {"clientID": "*****"}
    assert helper_patch.call_args.kwargs["base_url"] == client.base_url


def test_place_order_invokes_helper_with_json(helper_patch):
    helper_patch.return_value = _helper_response("POST", "/interactive/orders", {"type": "success", "result": {"AppOrderID": 10}})

    client = OrderAPIClient(auth_token="Bearer abc123")
    order_payload = {"symbol": "NIFTY", "quantity": 1, "clientID": "XXXXX"}
    result = client.place_order(order_payload)

    assert result["type"] == "success"
    helper_patch.assert_called_once()
    endpoint, auth = helper_patch.call_args[0][:2]
    method = helper_patch.call_args.kwargs.get("method")
    payload = helper_patch.call_args.kwargs["payload"]

    assert endpoint == "/interactive/orders"
    assert auth == "Bearer abc123"
    assert method == "POST"
    assert payload["_json"]["clientID"] == "XXXXX"
    assert payload["_timeout"] == 15.0
    assert helper_patch.call_args.kwargs["base_url"] == client.base_url


def test_custom_base_url_forwarded_to_helper(helper_patch):
    helper_patch.return_value = _helper_response("GET", "/interactive/orders", {"orders": []})

    client = OrderAPIClient(auth_token="Bearer abc123", base_url="https://staging.jainam.test/api/")
    client.get_orderbook(client_id="*****")

    helper_patch.assert_called_once()
    assert helper_patch.call_args.kwargs["base_url"] == "https://staging.jainam.test/api/"


def test_cancel_order_pro_dealer_includes_masked_client_id():
    with patch.object(OrderAPIClient, "cancel_order") as cancel_mock:
        cancel_mock.return_value = {"type": "success", "result": {"AppOrderID": 42}}

        auth_payload = {
            "interactive_token": "Bearer dealer-token",
            "clientID": "ZZJ13048",
            "user_id": "ZZJ13048",
            "isInvestorClient": False,
        }

        response_obj, payload = cancel_order_api(42, json.dumps(auth_payload))

        assert response_obj.status == 200
        assert payload["status"] == "success"
        cancel_mock.assert_called_once()
        (cancel_data,), _ = cancel_mock.call_args
        assert cancel_data["appOrderID"] == 42
        assert cancel_data["clientID"] == "*****"


def test_cancel_order_investor_uses_user_id():
    with patch.object(OrderAPIClient, "cancel_order") as cancel_mock:
        cancel_mock.return_value = {"type": "success", "result": {"AppOrderID": 77}}

        auth_payload = {
            "interactive_token": "Bearer investor-token",
            "user_id": "INVESTOR123",
            "isInvestorClient": True,
        }

        response_obj, payload = cancel_order_api(77, json.dumps(auth_payload))

        assert response_obj.status == 200
        assert payload["status"] == "success"
        cancel_mock.assert_called_once()
        (cancel_data,), _ = cancel_mock.call_args
        assert cancel_data["appOrderID"] == 77
        assert cancel_data["clientID"] == "INVESTOR123"
