import os
import re
from flask import session

from broker.jainamprop.baseurl import BASE_URL, INTERACTIVE_URL, MARKET_DATA_URL
from utils.httpx_client import get_httpx_client
from utils.logging import get_logger

logger = get_logger(__name__)


def _normalize_app_key(raw_key):
    """
    Normalize BROKER_API_KEY format.

    Some users store credentials as `client_id:::api_key`.
    XTS appKey should be only the API key part.
    """
    if not raw_key:
        return raw_key

    if ":::" in raw_key:
        parts = raw_key.split(":::")
        if len(parts) > 1 and parts[1]:
            return parts[1]

    return raw_key


def _extract_error_message(response):
    """Extract broker error message safely from JSON/text response."""
    try:
        error_detail = response.json()
        return (
            error_detail.get("description")
            or error_detail.get("message")
            or error_detail.get("error")
            or str(error_detail)
        )
    except Exception:
        return (response.text or "").strip() or "Authentication failed. Please try again."


def _clean_url(url: str) -> str:
    """Trim stray whitespace/backticks from URLs returned by hostlookup."""
    if not url:
        return url
    # Remove surrounding backticks and whitespace
    url = url.strip().strip("`").strip()
    return url


def _hostlookup_login(app_key: str, secret_key: str):
    """
    Fallback flow for clustered XTS deployments that require hostlookup uniqueKey login.
    1) POST BASE_URL/hostlookup with accesspassword/version to get uniqueKey + connectionString
    2) POST <connectionString>/user/session with appKey, secretKey, uniqueKey
    Returns: (auth_token, connection_string, error_message)
    """
    try:
        client = get_httpx_client()

        # Step 1: Hostlookup to get uniqueKey and connectionString
        lookup_url = f"{BASE_URL}/hostlookup"
        headers = {"Content-Type": "application/json"}

        # Try commonly accepted versions in order
        versions = ["interactive_1.0.1", "interactive_1.0.2", "interactiveapi_1.0.1", "interactive_2.0"]
        last_err = None
        unique_key = None
        connection_string = None

        for ver in versions:
            payload = {"accesspassword": "2021HostLookUpAccess", "version": ver}
            try:
                r = client.post(lookup_url, json=payload, headers=headers, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    # Accept both {"type": true} and {"type": "success"}
                    ok = data.get("type") in (True, "success") or data.get("code") == "hostlookup"
                    if ok and isinstance(data.get("result"), dict):
                        res = data["result"]
                        unique_key = res.get("uniqueKey") or res.get("UniqueKey")
                        connection_string = res.get("connectionString")
                        if unique_key and connection_string:
                            break
                last_err = _extract_error_message(r)
            except Exception as e:
                last_err = str(e)

        if not (unique_key and connection_string):
            return None, None, f"Hostlookup failed: {last_err or 'No uniqueKey/connectionString'}"

        # Step 2: Exchange uniqueKey for session token on cluster path
        login_url = _clean_url(connection_string).rstrip("/") + "/user/session"
        try:
            r2 = client.post(
                login_url,
                json={"appKey": app_key, "secretKey": secret_key, "uniqueKey": unique_key},
                headers=headers,
                timeout=15,
            )
            if r2.status_code == 200:
                j = r2.json()
                if j.get("type") in (True, "success") and j.get("result"):
                    token = j["result"].get("token")
                    if token:
                        logger.debug("Auth token received via hostlookup uniqueKey flow")
                        return token, connection_string, None
                return None, None, _extract_error_message(r2)
            else:
                return None, None, _extract_error_message(r2)
        except Exception as e:
            return None, None, f"Cluster session error: {str(e)}"
    except Exception as e:
        return None, None, f"Hostlookup exception: {str(e)}"


def authenticate_broker(request_token):
    try:
        # Get the shared httpx client
        client = get_httpx_client()
        if not request_token:
            # If no request token from redirect, try hostlookup fallback (cluster path)
            BROKER_API_KEY = _normalize_app_key(os.getenv("BROKER_API_KEY"))
            BROKER_API_SECRET = os.getenv("BROKER_API_SECRET")
            token, conn_str, err = _hostlookup_login(BROKER_API_KEY, BROKER_API_SECRET)
            if token:
                try:
                    if conn_str:
                        cs = _clean_url(conn_str)
                        cluster_base = re.sub(r"/([^/]+)hostlookup/?$", r"/\1interactive", cs)
                        session["JAINAMPROP_CLUSTER_BASE"] = cluster_base
                except Exception:
                    pass
                # Retrieve feed token and user_id after successful auth
                feed_token, user_id, feed_error = get_feed_token()
                if feed_error:
                    return token, None, None, f"Feed token error: {feed_error}"
                return token, feed_token, user_id, None
            return None, None, None, err or "Missing request token in callback."

        # Fetching the necessary credentials from environment variables
        BROKER_API_KEY = _normalize_app_key(os.getenv("BROKER_API_KEY"))
        BROKER_API_SECRET = os.getenv("BROKER_API_SECRET")

        headers = {"Content-Type": "application/json"}
        session_url = f"{INTERACTIVE_URL}/user/session"

        # Different XTS broker hosts accept different token key names.
        # Try both accessToken and requestToken for compatibility.
        payloads = [
            {"appKey": BROKER_API_KEY, "secretKey": BROKER_API_SECRET, "accessToken": request_token},
            {"appKey": BROKER_API_KEY, "secretKey": BROKER_API_SECRET, "requestToken": request_token},
        ]

        last_error_message = "Authentication failed. Please try again."
        for payload in payloads:
            response = client.post(session_url, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                if result.get("type") == "success":
                    token = result["result"]["token"]
                    logger.debug("Auth token received successfully")

                    # Call get_feed_token() after successful authentication
                    feed_token, user_id, feed_error = get_feed_token()
                    if feed_error:
                        return token, None, None, f"Feed token error: {feed_error}"

                    return token, feed_token, user_id, None
                last_error_message = _extract_error_message(response)
            else:
                last_error_message = _extract_error_message(response)

        # Fallback for clustered deployments:
        # Try cluster session exchange with the provided token at /5interactive/user/session
        try:
            # Try both param names on /5interactive as well
            cluster_session_url = re.sub(r"/interactive/?$", "/5interactive", INTERACTIVE_URL.rstrip("/")) + "/user/session"
            for p in [
                {"appKey": BROKER_API_KEY, "secretKey": BROKER_API_SECRET, "accessToken": request_token},
                {"appKey": BROKER_API_KEY, "secretKey": BROKER_API_SECRET, "requestToken": request_token},
            ]:
                r = client.post(cluster_session_url, json=p, headers=headers, timeout=15)
                if r.status_code == 200:
                    rj = r.json()
                    if rj.get("type") == "success" and rj.get("result"):
                        t = rj["result"].get("token")
                        if t:
                            feed_token, user_id, feed_error = get_feed_token()
                            if feed_error:
                                return t, None, None, f"Feed token error: {feed_error}"
                            return t, feed_token, user_id, None
        except Exception:
            pass

        # Last-chance fallback: hostlookup uniqueKey flow
        token, conn_str, err = _hostlookup_login(BROKER_API_KEY, BROKER_API_SECRET)
        if token:
            try:
                if conn_str:
                    cs = _clean_url(conn_str)
                    cluster_base = re.sub(r"/([^/]+)hostlookup/?$", r"/\1interactive", cs)
                    session["JAINAMPROP_CLUSTER_BASE"] = cluster_base
            except Exception:
                pass
            feed_token, user_id, feed_error = get_feed_token()
            if feed_error:
                return token, None, None, f"Feed token error: {feed_error}"
            return token, feed_token, user_id, None

        return None, None, None, f"API error: {last_error_message or err}"

    except Exception as e:
        return None, None, None, f"Error during authentication: {str(e)}"


def get_feed_token():
    try:
        # Fetch credentials for feed token
        BROKER_API_KEY_MARKET = os.getenv("BROKER_API_KEY_MARKET")
        BROKER_API_SECRET_MARKET = os.getenv("BROKER_API_SECRET_MARKET")

        # Construct payload for feed token request
        feed_payload = {
            "secretKey": BROKER_API_SECRET_MARKET,
            "appKey": BROKER_API_KEY_MARKET,
            "source": "WebAPI",
        }

        feed_headers = {"Content-Type": "application/json"}

        # Get feed token
        feed_url = f"{MARKET_DATA_URL}/auth/login"
        client = get_httpx_client()
        feed_response = client.post(feed_url, json=feed_payload, headers=feed_headers)

        feed_token = None
        user_id = None
        if feed_response.status_code == 200:
            feed_result = feed_response.json()
            if feed_result.get("type") == "success":
                feed_token = feed_result["result"].get("token")
                
                client_codes = feed_result["result"].get("clientCodes", [])
                if client_codes and isinstance(client_codes, list) and len(client_codes) > 0:
                    user_id = client_codes[0]
                else:
                    user_id = feed_result["result"].get("userID")
                    
                if user_id and isinstance(user_id, str):
                    user_id = user_id.split("_")[0]
                logger.debug("Feed token received successfully")
            else:
                return None, None, "Feed token request failed. Please check the response."
        else:
            feed_error_detail = feed_response.json()
            feed_error_message = feed_error_detail.get(
                "description", "Feed token request failed. Please try again."
            )
            return None, None, f"API Error (Feed): {feed_error_message}"

        return feed_token, user_id, None
    except Exception as e:
        return None, None, f"An exception occurred: {str(e)}"
