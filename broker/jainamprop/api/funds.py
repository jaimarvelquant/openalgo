# api/funds.py

import base64
import json
import os
from typing import Any, Dict
from flask import session
import re
import httpx

from broker.jainamprop.baseurl import BASE_URL, INTERACTIVE_URL
from utils.httpx_client import get_httpx_client
from utils.logging import get_logger
from database.apilog_db import async_log_order, init_db

logger = get_logger(__name__)


def get_margin_data(auth_token):
    def _zeros():
        return {
            "availablecash": "0.00",
            "collateral": "0.00",
            "m2munrealized": "0.00",
            "m2mrealized": "0.00",
            "utiliseddebits": "0.00",
        }

    def _decode_jwt_payload(token: str) -> Dict[str, Any] | None:
        try:
            parts = token.split(".")
            if len(parts) < 2:
                return None
            payload = parts[1]
            rem = len(payload) % 4
            if rem:
                payload += "=" * (4 - rem)
            data = base64.urlsafe_b64decode(payload.encode())
            return json.loads(data.decode())
        except Exception:
            return None

    client = get_httpx_client()

    headers = {"authorization": auth_token, "Content-Type": "application/json"}

    user_id = os.getenv("JAINAMPROP_USER_ID")
    if not user_id:
        payload = _decode_jwt_payload(auth_token)
        if isinstance(payload, dict):
            raw_uid = payload.get("userID") or payload.get("userId") or payload.get("userid")
            if raw_uid and isinstance(raw_uid, str):
                user_id = raw_uid.split("_")[0]

        if not user_id:
            try:
                from database.auth_db import get_user_id as _get_uid
                # session['user'] is set; use stored user_id
                login_username = session.get("user")
                if login_username:
                    user_id = _get_uid(login_username)
                    if user_id and isinstance(user_id, str):
                        user_id = user_id.split("_")[0]
            except Exception:
                pass

    # Prefer cluster base derived at login if present
    cluster_base = None
    try:
        cb = session.get("JAINAMPROP_CLUSTER_BASE")
        if isinstance(cb, str) and cb:
            cluster_base = cb.rstrip("/")
    except Exception:
        pass

    # Helper to fetch URL with h2 then h1 fallback
    def fetch_json(url_to_get: str) -> dict:
        try:
            r = client.get(url_to_get, headers=headers)
            return r.json()
        except Exception as e:
            logger.error(f"h2 fetch failed: {e}")
            try:
                client_h1 = httpx.Client(http2=False, http1=True, timeout=30.0)
                r2 = client_h1.get(url_to_get, headers=headers)
                return r2.json()
            except Exception as e2:
                logger.error(f"h1 fetch failed: {e2}")
                return {}

    # Prefer cluster path first if available (matches working script behavior)
    margin_data = {}
    if cluster_base:
        cu = f"{cluster_base}/user/balance"
        if user_id:
            cu = f"{cu}?clientID={user_id}"
        logger.info(f"Funds request cluster URL: {cu}")
        margin_data = fetch_json(cu)

    # If cluster missing or returned empty, try static interactive
    if not (
        isinstance(margin_data, dict)
        and margin_data.get("result")
        and margin_data["result"].get("BalanceList")
        and margin_data["result"]["BalanceList"]
    ):
        url = f"{INTERACTIVE_URL}/user/balance"
        if user_id:
            url = f"{url}?clientID={user_id}"
        logger.info(f"Funds request interactive URL: {url}")
        margin_data = fetch_json(url)

    # Fallback to cluster path if interactive returns no result
    if not (
        isinstance(margin_data, dict)
        and margin_data.get("result")
        and margin_data["result"].get("BalanceList")
        and margin_data["result"]["BalanceList"]
    ):
        try:
            if not cluster_base:
                try:
                    lookup_url = f"{BASE_URL}/hostlookup"
                    versions = ["interactive_1.0.1", "interactive_1.0.2", "interactiveapi_1.0.1", "interactive_2.0"]
                    conn_str = None
                    for ver in versions:
                        r = client.post(lookup_url, json={"accesspassword": "2021HostLookUpAccess", "version": ver}, timeout=15)
                        if r.status_code == 200:
                            j = r.json()
                            t = j.get("type")
                            ok = t in (True, "success") or j.get("code") == "hostlookup"
                            if ok and isinstance(j.get("result"), dict):
                                res = j["result"]
                                cs = res.get("connectionString")
                                if cs:
                                    conn_str = cs.strip().strip("`").strip()
                                    break
                    if conn_str:
                        cluster_base = re.sub(r"/([^/]+)hostlookup/?$", r"/\1interactive", conn_str)
                except Exception:
                    pass
            cluster_url = f"{(cluster_base or BASE_URL + '/5interactive').rstrip('/')}/user/balance"
            if user_id:
                cluster_url = f"{cluster_url}?clientID={user_id}"
            logger.info(f"Funds request derived cluster URL: {cluster_url}")
            try:
                response2 = client.get(cluster_url, headers=headers)
                margin_data = response2.json()
            except Exception as e3:
                logger.error(f"Cluster interactive path error (h2): {e3}")
                # Retry on HTTP/1.1
                client_h1 = httpx.Client(http2=False, http1=True, timeout=30.0)
                response2 = client_h1.get(cluster_url, headers=headers)
                margin_data = response2.json()
        except Exception as e:
            logger.error(f"Error fetching funds on cluster path: {e}")
            margin_data = {}

    try:
        logger.info(f"Funds raw response: {json.dumps(margin_data)[:500]}")
    except Exception:
        pass
    if (
        isinstance(margin_data, dict)
        and margin_data.get("result")
        and margin_data["result"].get("BalanceList")
        and margin_data["result"]["BalanceList"]
    ):
        try:
            init_db()
            req_info = {
                "cluster_base": cluster_base or "",
                "base_url": BASE_URL,
                "interactive_url": INTERACTIVE_URL,
                "user_id": user_id or "",
            }
            resp_info = margin_data if isinstance(margin_data, dict) else {"raw": str(margin_data)}
            async_log_order("jainamprop_funds_snapshot", req_info, resp_info)
        except Exception:
            pass
            
        # Safely extract sublimits
        res = margin_data.get("result") or {}
        blist = res.get("BalanceList") or []
        sub = (((blist[0] or {}).get("limitObject") or {}).get("RMSSubLimits") or {})

        required_keys = [
            "netMarginAvailable",
            "collateral",
            "UnrealizedMTM",
            "RealizedMTM",
            "marginUtilized",
        ]

        filtered_data = {}
        for key in required_keys:
            value = sub.get(key, 0)
            try:
                formatted_value = f"{float(value):.2f}" if str(value).lower() != "nan" else "0.00"
            except (ValueError, TypeError):
                formatted_value = "0.00"

            filtered_data[key] = formatted_value

        processed_margin_data = {
            "availablecash": filtered_data.get("netMarginAvailable"),
            "collateral": filtered_data.get("collateral"),
            "m2munrealized": filtered_data.get("UnrealizedMTM"),
            "m2mrealized": filtered_data.get("RealizedMTM"),
            "utiliseddebits": filtered_data.get("marginUtilized"),
        }

        return processed_margin_data
    else:
        try:
            init_db()
            req_info = {
                "cluster_base": cluster_base or "",
                "base_url": BASE_URL,
                "interactive_url": INTERACTIVE_URL,
                "user_id": user_id or "",
            }
            resp_info = margin_data if isinstance(margin_data, dict) else {"raw": str(margin_data)}
            async_log_order("jainamprop_funds_unavailable", req_info, resp_info)
        except Exception:
            pass
        return _zeros()
