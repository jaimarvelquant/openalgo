"""Base HTTP client for Jainam API built on top of HTTP helper."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Optional, Union

import httpx

from .routes import get_route
from .config import (
    get_jainam_base_url,
    JAINAM_RETRY_ATTEMPTS,
    JAINAM_RETRY_BACKOFF_MIN,
    JAINAM_RETRY_BACKOFF_MAX,
)
from .http_helper import get_api_response

logger = logging.getLogger(__name__)

def _summarise_keys(mapping: Optional[Dict[str, Any]]) -> Iterable[str]:
    if not mapping:
        return []
    return sorted(mapping.keys())


class BaseAPIClient:
    """Shared HTTP client that delegates network I/O to the helper layer."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url or get_jainam_base_url()
        self.auth_token = auth_token
        self.default_timeout = timeout

    def set_auth_token(self, token: str) -> None:
        """Set or update authentication token."""

        self.auth_token = token

    def _build_headers(
        self,
        additional_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = self.auth_token
        if additional_headers:
            headers.update(additional_headers)
        return headers

    def _request(
        self,
        route_key: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        content: Optional[Union[str, bytes]] = None,
        timeout: Optional[float] = None,
        use_standard_marketdata: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute HTTP request against Jainam API."""

        route_path = get_route(route_key, use_standard_marketdata=use_standard_marketdata)

        headers = self._build_headers(kwargs.pop("headers", None))
        timeout_value = timeout if timeout is not None else self.default_timeout

        logger.info(
            "Jainam request",
            extra={
                "route": route_key,
                "method": method.upper(),
                "standard_marketdata": use_standard_marketdata,
            },
        )
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Jainam request payload metadata",
                extra={
                    "route": route_key,
                    "method": method.upper(),
                    "timeout": timeout_value,
                    "has_params": bool(params),
                    "has_json": isinstance(json_data, dict),
                    "params_keys": list(_summarise_keys(params)),
                    "json_keys": list(_summarise_keys(json_data) if isinstance(json_data, dict) else []),
                    "has_content": content is not None,
                },
            )

        helper_payload = {
            "_params": params,
            "_json": json_data,
            "_content": content,
            "_headers": headers,
            "_timeout": timeout_value,
        }

        helper_response = get_api_response(
            route_path,
            self.auth_token or "",
            method=method,
            payload=helper_payload,
            retries=kwargs.pop("retries", JAINAM_RETRY_ATTEMPTS),
            backoff_min=kwargs.pop("backoff_min", JAINAM_RETRY_BACKOFF_MIN),
            backoff_max=kwargs.pop("backoff_max", JAINAM_RETRY_BACKOFF_MAX),
            base_url=self.base_url,
        )

        response = helper_response.raw_response

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self._handle_http_error(route_key, exc)
            raise

        return dict(helper_response)

    def _handle_http_error(self, route_key: str, exc: httpx.HTTPStatusError) -> None:
        status_code = exc.response.status_code

        if status_code == 400:
            try:
                error_data = exc.response.json()
            except ValueError:
                error_data = {}

            error_code = str(error_data.get("code", ""))
            description = str(error_data.get("description", "")).lower()

            no_data_error_codes = {
                "e-orders-0005",
                "e-tradebook-0005",
                "e-portfolio-0005",
                "e-holdings-0005",
                "e-funds-0005",
                "e-balance-0005",
            }

            if error_code.lower() in {code.lower() for code in no_data_error_codes} or "data not available" in description:
                logger.debug(
                    "HTTP 400 for %s: Data Not Available (code: %s) - Expected when no data exists",
                    route_key,
                    error_code,
                )
            else:
                logger.error(
                    "HTTP %s error for %s: %s",
                    status_code,
                    route_key,
                    exc.response.text[:500],
                )
        else:
            logger.error(
                "HTTP %s error for %s: %s",
                status_code,
                route_key,
                exc.response.text[:500],
            )

    def _get(self, route_key: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        return self._request(route_key, "GET", params=params, **kwargs)

    def _post(
        self,
        route_key: str,
        json_data: Optional[Dict[str, Any]] = None,
        content: Optional[Union[str, bytes]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self._request(route_key, "POST", json_data=json_data, content=content, **kwargs)

    def _put(
        self,
        route_key: str,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self._request(route_key, "PUT", json_data=json_data, **kwargs)

    def _delete(
        self,
        route_key: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self._request(route_key, "DELETE", params=params, **kwargs)

    def close(self) -> None:
        """Shared client handled by helper; nothing to close here."""

    def __enter__(self) -> "BaseAPIClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
