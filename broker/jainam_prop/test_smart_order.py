"""
Unit tests for place_smartorder_api covering delta calculations and error handling.
"""
import logging
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from broker.jainam_prop.api.order_api import place_smartorder_api


@pytest.fixture
def base_payload():
    return {
        'symbol': 'SBIN-EQ',
        'exchange': 'NSE',
        'product': 'MIS',
        'position_size': 150,
        'price_type': 'MARKET'
    }


class TestPlaceSmartOrder:
    """Test suite for Jainam place_smartorder_api logic."""

    def test_places_buy_order_when_target_greater_than_current(self, base_payload):
        with patch('broker.jainam_prop.api.order_api.get_open_position') as mock_get_pos, \
             patch('broker.jainam_prop.api.order_api.place_order_api') as mock_place_order:
            mock_get_pos.return_value = '100'
            mock_place_order.return_value = (
                SimpleNamespace(status=200),
                {'status': 'success'},
                'OID123'
            )

            res, response, orderid = place_smartorder_api(base_payload, 'token')

            assert response['status'] == 'success'
            assert response['orderid'] == 'OID123'
            assert orderid == 'OID123'
            assert base_payload['action'] == 'BUY'
            assert base_payload['quantity'] == '50'

            order_call_payload = mock_place_order.call_args[0][0]
            assert order_call_payload['action'] == 'BUY'
            assert order_call_payload['quantity'] == '50'

    def test_places_sell_order_when_target_less_than_current(self, base_payload):
        payload = base_payload.copy()
        payload['position_size'] = 40
        with patch('broker.jainam_prop.api.order_api.get_open_position') as mock_get_pos, \
             patch('broker.jainam_prop.api.order_api.place_order_api') as mock_place_order:
            mock_get_pos.return_value = '100'
            mock_place_order.return_value = (
                SimpleNamespace(status=200),
                {'status': 'success'},
                'OID456'
            )

            res, response, orderid = place_smartorder_api(payload, 'token')

            assert response['status'] == 'success'
            assert response['orderid'] == 'OID456'
            assert payload['action'] == 'SELL'
            assert payload['quantity'] == '60'

            order_call_payload = mock_place_order.call_args[0][0]
            assert order_call_payload['action'] == 'SELL'
            assert order_call_payload['quantity'] == '60'

    def test_places_buy_order_from_flat_position(self, base_payload):
        payload = base_payload.copy()
        payload['position_size'] = 75
        with patch('broker.jainam_prop.api.order_api.get_open_position') as mock_get_pos, \
             patch('broker.jainam_prop.api.order_api.place_order_api') as mock_place_order:
            mock_get_pos.return_value = '0'
            mock_place_order.return_value = (
                SimpleNamespace(status=200),
                {'status': 'success'},
                'OID777'
            )

            res, response, orderid = place_smartorder_api(payload, 'token')

            assert response['status'] == 'success'
            assert response['orderid'] == 'OID777'
            assert orderid == 'OID777'
            assert payload['action'] == 'BUY'
            assert payload['quantity'] == '75'

            order_call_payload = mock_place_order.call_args[0][0]
            assert order_call_payload['action'] == 'BUY'
            assert order_call_payload['quantity'] == '75'

    def test_places_sell_order_to_flatten_position(self, base_payload):
        payload = base_payload.copy()
        payload['position_size'] = 0
        with patch('broker.jainam_prop.api.order_api.get_open_position') as mock_get_pos, \
             patch('broker.jainam_prop.api.order_api.place_order_api') as mock_place_order:
            mock_get_pos.return_value = '120'
            mock_place_order.return_value = (
                SimpleNamespace(status=200),
                {'status': 'success'},
                'OID888'
            )

            res, response, orderid = place_smartorder_api(payload, 'token')

            assert response['status'] == 'success'
            assert response['orderid'] == 'OID888'
            assert orderid == 'OID888'
            assert payload['action'] == 'SELL'
            assert payload['quantity'] == '120'

            order_call_payload = mock_place_order.call_args[0][0]
            assert order_call_payload['action'] == 'SELL'
            assert order_call_payload['quantity'] == '120'

    def test_places_sell_order_when_reversing_position(self, base_payload):
        payload = base_payload.copy()
        payload['position_size'] = -50
        with patch('broker.jainam_prop.api.order_api.get_open_position') as mock_get_pos, \
             patch('broker.jainam_prop.api.order_api.place_order_api') as mock_place_order:
            mock_get_pos.return_value = '100'
            mock_place_order.return_value = (
                SimpleNamespace(status=200),
                {'status': 'success'},
                'OID889'
            )

            res, response, orderid = place_smartorder_api(payload, 'token')

            assert response['status'] == 'success'
            assert response['orderid'] == 'OID889'
            assert orderid == 'OID889'
            assert payload['action'] == 'SELL'
            assert payload['quantity'] == '150'

            order_call_payload = mock_place_order.call_args[0][0]
            assert order_call_payload['action'] == 'SELL'
            assert order_call_payload['quantity'] == '150'

    def test_returns_success_when_delta_zero(self, base_payload):
        with patch('broker.jainam_prop.api.order_api.get_open_position') as mock_get_pos, \
             patch('broker.jainam_prop.api.order_api.place_order_api') as mock_place_order:
            mock_get_pos.return_value = '150'

            res, response, orderid = place_smartorder_api(base_payload, 'token')

            assert res is None
            assert response['status'] == 'success'
            assert 'No action needed' in response['message']
            assert orderid == ''
            mock_place_order.assert_not_called()

    def test_handles_get_open_position_failure(self, base_payload):
        with patch('broker.jainam_prop.api.order_api.get_open_position') as mock_get_pos:
            mock_get_pos.side_effect = RuntimeError('position lookup failed')

            res, response, orderid = place_smartorder_api(base_payload, 'token')

            assert res is None
            assert response['status'] == 'error'
            assert response['message'] == 'Failed to fetch current position'
            assert orderid is None

    def test_handles_invalid_position_size(self, base_payload):
        base_payload['position_size'] = 'not-a-number'

        res, response, orderid = place_smartorder_api(base_payload, 'token')

        assert res is None
        assert response['status'] == 'error'
        assert 'Invalid position_size' in response['message']
        assert orderid is None

    def test_handles_invalid_response_from_place_order(self, base_payload):
        with patch('broker.jainam_prop.api.order_api.get_open_position') as mock_get_pos, \
             patch('broker.jainam_prop.api.order_api.place_order_api') as mock_place_order:
            mock_get_pos.return_value = '10'
            mock_place_order.return_value = (SimpleNamespace(status=200), 'unexpected', 'OID789')

            res, response, orderid = place_smartorder_api(base_payload, 'token')

            assert res is None
            assert response['status'] == 'error'
            assert response['message'] == 'Invalid response from order placement'
            assert orderid is None

    def test_records_latency_metadata_and_warns_when_threshold_exceeded(self, base_payload, caplog):
        payload = base_payload.copy()
        payload['position_size'] = 200
        with patch('broker.jainam_prop.api.order_api.get_open_position') as mock_get_pos, \
             patch('broker.jainam_prop.api.order_api.place_order_api') as mock_place_order, \
             patch('broker.jainam_prop.api.order_api.time.perf_counter', side_effect=[1000.0, 1011.5]):
            mock_get_pos.return_value = '0'
            mock_place_order.return_value = (
                SimpleNamespace(status=200),
                {'status': 'success'},
                'OID999'
            )

            with caplog.at_level(logging.WARNING):
                res, response, orderid = place_smartorder_api(payload, 'token')

        assert res.status == 200
        assert response['status'] == 'success'
        assert orderid == 'OID999'
        assert response['latency_status'] == 'exceeded_threshold'
        assert response['latency_threshold_seconds'] == pytest.approx(10.0)
        assert response['latency_seconds'] == pytest.approx(11.5, rel=1e-3)
        assert any(
            record.levelno == logging.WARNING and 'duration=11.500' in record.getMessage()
            for record in caplog.records
        )
