"""
Enterprise-grade broker API client with resilience patterns.

Features:
- Retry logic with exponential backoff
- Circuit breaker pattern for failing endpoints
- Standardized error response format
- Comprehensive telemetry and logging
- Graceful degradation
- Request/response correlation tracking
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, Optional

import httpx
from utils.httpx_client import get_httpx_client
from utils.logging import get_logger

logger = get_logger(__name__)


class ErrorCode(Enum):
    """Standardized error codes for broker API responses."""
    HTTP_4XX = "HTTP_CLIENT_ERROR"
    HTTP_5XX = "HTTP_SERVER_ERROR"
    TIMEOUT = "REQUEST_TIMEOUT"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    CIRCUIT_OPEN = "CIRCUIT_BREAKER_OPEN"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Endpoint failing, reject requests
    HALF_OPEN = "half_open"  # Testing if endpoint recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for endpoint resilience.

    Prevents cascading failures by stopping requests to failing endpoints.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to track
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitBreakerState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.

        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function

        Returns:
            Function result

        Raises:
            Exception: If circuit is open
        """
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN - endpoint unavailable")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        return (
            self.last_failure_time is not None and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )

    def _on_success(self):
        """Reset circuit breaker on successful call."""
        self.failure_count = 0
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            logger.info("Circuit breaker reset to CLOSED state")

    def _on_failure(self):
        """Track failure and potentially open circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                f"Circuit breaker OPENED after {self.failure_count} failures"
            )


class BrokerAPIClient:
    """
    Enterprise-grade broker API client with resilience patterns.

    Usage:
        client = BrokerAPIClient(broker_name="jainam", base_url="https://api.broker.com")
        response = client.get("/portfolio/holdings", auth_token="...")
    """

    def __init__(
        self,
        broker_name: str,
        base_url: str,
        max_retries: int = 3,
        retry_backoff_factor: float = 1.0,
        timeout: float = 10.0,
        enable_circuit_breaker: bool = True
    ):
        """
        Initialize broker API client.

        Args:
            broker_name: Broker identifier for logging
            base_url: Base URL for API endpoints
            max_retries: Maximum number of retry attempts
            retry_backoff_factor: Exponential backoff multiplier
            timeout: Request timeout in seconds
            enable_circuit_breaker: Enable circuit breaker pattern
        """
        self.broker_name = broker_name
        self.base_url = base_url.rstrip('/')
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor
        self.timeout = timeout

        # Circuit breaker per endpoint
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.enable_circuit_breaker = enable_circuit_breaker

        # Metrics tracking
        self.request_count = 0
        self.error_count = 0

    def _get_circuit_breaker(self, endpoint: str) -> Optional[CircuitBreaker]:
        """Get or create circuit breaker for endpoint."""
        if not self.enable_circuit_breaker:
            return None

        if endpoint not in self.circuit_breakers:
            self.circuit_breakers[endpoint] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=60.0
            )
        return self.circuit_breakers[endpoint]

    def _create_error_response(
        self,
        error_code: ErrorCode,
        message: str,
        endpoint: str,
        http_status: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standardized error response.

        Args:
            error_code: Error code enum
            message: Human-readable error message
            endpoint: API endpoint that failed
            http_status: HTTP status code if applicable
            details: Additional error details
            correlation_id: Request correlation ID

        Returns:
            Standardized error response dict
        """
        return {
            'status': 'error',
            'error_code': error_code.value,
            'message': message,
            'endpoint': endpoint,
            'http_status': http_status,
            'details': details or {},
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'correlation_id': correlation_id,
            'broker': self.broker_name
        }

    def _execute_with_retry(
        self,
        method: str,
        endpoint: str,
        headers: Dict[str, str],
        correlation_id: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute HTTP request with retry logic and exponential backoff.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            headers: Request headers
            correlation_id: Request correlation ID
            json_data: JSON payload for POST/PUT
            params: Query parameters for GET

        Returns:
            API response dict (success or error)
        """
        url = f"{self.base_url}{endpoint}"
        client = get_httpx_client()

        last_exception = None

        for attempt in range(self.max_retries):
            try:
                # Log request attempt
                logger.info(
                    f"[{correlation_id}] {self.broker_name} API request: "
                    f"{method} {endpoint} (attempt {attempt + 1}/{self.max_retries})"
                )

                # Execute request
                start_time = time.perf_counter()

                if method.upper() == "GET":
                    response = client.get(
                        url,
                        headers=headers,
                        params=params,
                        timeout=self.timeout
                    )
                elif method.upper() == "POST":
                    response = client.post(
                        url,
                        headers=headers,
                        json=json_data,
                        timeout=self.timeout
                    )
                elif method.upper() == "PUT":
                    response = client.put(
                        url,
                        headers=headers,
                        json=json_data,
                        timeout=self.timeout
                    )
                elif method.upper() == "DELETE":
                    response = client.delete(
                        url,
                        headers=headers,
                        timeout=self.timeout
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                elapsed = time.perf_counter() - start_time

                # Log response metrics
                logger.info(
                    f"[{correlation_id}] {self.broker_name} API response: "
                    f"HTTP {response.status_code} in {elapsed:.3f}s"
                )

                # Handle HTTP errors
                if response.status_code >= 500:
                    # Server errors - retry
                    error_msg = f"Server error: HTTP {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg = error_detail.get('message', error_msg)
                    except:
                        error_msg = response.text[:200] if response.text else error_msg

                    logger.warning(
                        f"[{correlation_id}] {self.broker_name} server error: {error_msg}"
                    )

                    # Retry on 5xx errors with exponential backoff
                    if attempt < self.max_retries - 1:
                        backoff = self.retry_backoff_factor * (2 ** attempt)
                        logger.info(f"[{correlation_id}] Retrying in {backoff}s...")
                        time.sleep(backoff)
                        continue

                    # Max retries exhausted
                    return self._create_error_response(
                        ErrorCode.HTTP_5XX,
                        error_msg,
                        endpoint,
                        http_status=response.status_code,
                        details={'response_text': response.text[:500]},
                        correlation_id=correlation_id
                    )

                elif response.status_code >= 400:
                    # Client errors - don't retry
                    error_msg = f"Client error: HTTP {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg = error_detail.get('message', error_msg)
                    except:
                        error_msg = response.text[:200] if response.text else error_msg

                    logger.error(
                        f"[{correlation_id}] {self.broker_name} client error: {error_msg}"
                    )

                    return self._create_error_response(
                        ErrorCode.HTTP_4XX,
                        error_msg,
                        endpoint,
                        http_status=response.status_code,
                        details={'response_text': response.text[:500]},
                        correlation_id=correlation_id
                    )

                # Success - parse response
                try:
                    response_data = response.json()
                    logger.debug(f"[{correlation_id}] Response parsed successfully")
                    return response_data
                except Exception as e:
                    logger.error(f"[{correlation_id}] Failed to parse JSON response: {e}")
                    return self._create_error_response(
                        ErrorCode.INVALID_RESPONSE,
                        f"Invalid JSON response: {str(e)}",
                        endpoint,
                        http_status=response.status_code,
                        details={'response_text': response.text[:500]},
                        correlation_id=correlation_id
                    )

            except httpx.TimeoutException as e:
                logger.warning(f"[{correlation_id}] Request timeout: {e}")
                last_exception = e
                if attempt < self.max_retries - 1:
                    backoff = self.retry_backoff_factor * (2 ** attempt)
                    logger.info(f"[{correlation_id}] Retrying in {backoff}s...")
                    time.sleep(backoff)
                    continue

            except httpx.ConnectError as e:
                logger.error(f"[{correlation_id}] Connection error: {e}")
                last_exception = e
                if attempt < self.max_retries - 1:
                    backoff = self.retry_backoff_factor * (2 ** attempt)
                    logger.info(f"[{correlation_id}] Retrying in {backoff}s...")
                    time.sleep(backoff)
                    continue

            except Exception as e:
                logger.exception(f"[{correlation_id}] Unexpected error: {e}")
                last_exception = e
                break  # Don't retry on unexpected errors

        # All retries exhausted or unexpected error
        if isinstance(last_exception, httpx.TimeoutException):
            error_code = ErrorCode.TIMEOUT
            message = f"Request timeout after {self.max_retries} attempts"
        elif isinstance(last_exception, httpx.ConnectError):
            error_code = ErrorCode.CONNECTION_ERROR
            message = f"Connection failed after {self.max_retries} attempts"
        else:
            error_code = ErrorCode.UNKNOWN_ERROR
            message = f"Request failed: {str(last_exception)}"

        return self._create_error_response(
            error_code,
            message,
            endpoint,
            details={'exception': str(last_exception)},
            correlation_id=correlation_id
        )

    def request(
        self,
        method: str,
        endpoint: str,
        auth_token: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        extra_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make API request with full resilience stack.

        Args:
            method: HTTP method
            endpoint: API endpoint path (e.g., "/portfolio/holdings")
            auth_token: Authentication token
            json_data: JSON payload for POST/PUT
            params: Query parameters
            extra_headers: Additional headers

        Returns:
            API response dict (success or standardized error)
        """
        correlation_id = str(uuid.uuid4())[:8]
        self.request_count += 1

        # Build headers
        headers = {
            'Authorization': auth_token,
            'Content-Type': 'application/json',
            'X-Correlation-ID': correlation_id
        }
        if extra_headers:
            headers.update(extra_headers)

        # Check circuit breaker
        circuit_breaker = self._get_circuit_breaker(endpoint)
        if circuit_breaker and circuit_breaker.state == CircuitBreakerState.OPEN:
            if not circuit_breaker._should_attempt_reset():
                logger.warning(
                    f"[{correlation_id}] Circuit breaker OPEN for {endpoint} - "
                    f"rejecting request"
                )
                self.error_count += 1
                return self._create_error_response(
                    ErrorCode.CIRCUIT_OPEN,
                    f"Endpoint {endpoint} is currently unavailable (circuit breaker open)",
                    endpoint,
                    correlation_id=correlation_id
                )

        # Execute request
        try:
            # Execute the request
            result = self._execute_with_retry(
                method,
                endpoint,
                headers,
                correlation_id,
                json_data,
                params
            )

            # Track errors and manage circuit breaker manually
            if isinstance(result, dict) and result.get('status') == 'error':
                self.error_count += 1

                # Manually track failure in circuit breaker for error responses
                if circuit_breaker:
                    circuit_breaker._on_failure()
            else:
                # Success - reset circuit breaker
                if circuit_breaker:
                    circuit_breaker._on_success()

            return result

        except Exception as e:
            logger.exception(f"[{correlation_id}] Circuit breaker call failed: {e}")
            self.error_count += 1
            return self._create_error_response(
                ErrorCode.CIRCUIT_OPEN,
                str(e),
                endpoint,
                correlation_id=correlation_id
            )

    def get(self, endpoint: str, auth_token: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """GET request."""
        return self.request("GET", endpoint, auth_token, params=params, **kwargs)

    def post(self, endpoint: str, auth_token: str, json_data: Dict, **kwargs) -> Dict[str, Any]:
        """POST request."""
        return self.request("POST", endpoint, auth_token, json_data=json_data, **kwargs)

    def put(self, endpoint: str, auth_token: str, json_data: Dict, **kwargs) -> Dict[str, Any]:
        """PUT request."""
        return self.request("PUT", endpoint, auth_token, json_data=json_data, **kwargs)

    def delete(self, endpoint: str, auth_token: str, **kwargs) -> Dict[str, Any]:
        """DELETE request."""
        return self.request("DELETE", endpoint, auth_token, **kwargs)

    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics for monitoring."""
        return {
            'broker': self.broker_name,
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': self.error_count / self.request_count if self.request_count > 0 else 0,
            'circuit_breakers': {
                endpoint: {
                    'state': cb.state.value,
                    'failure_count': cb.failure_count
                }
                for endpoint, cb in self.circuit_breakers.items()
            }
        }
