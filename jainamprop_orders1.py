import argparse
import json
import os
import re

import httpx


def load_env():
    try:
        from dotenv import load_dotenv  # type: ignore
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
    except Exception:
        pass


def clean(s: str) -> str:
    if not s:
        return s
    return s.strip().strip("`").strip()


def hostlookup(base_url: str) -> tuple[str | None, str | None, str | None]:
    client = httpx.Client(timeout=15.0)
    url = base_url.rstrip("/") + "/hostlookup"
    versions = ["interactive_1.0.1", "interactive_1.0.2", "interactiveapi_1.0.1", "interactive_2.0"]
    last_err = None
    for ver in versions:
        try:
            r = client.post(url, json={"accesspassword": "2021HostLookUpAccess", "version": ver})
            if r.status_code == 200:
                j = r.json()
                ok = j.get("type") in (True, "success") or j.get("code") == "hostlookup"
                if ok and isinstance(j.get("result"), dict):
                    res = j["result"]
                    uk = res.get("uniqueKey") or res.get("UniqueKey")
                    cs = res.get("connectionString")
                    if uk and cs:
                        return uk, cs, None
            last_err = r.text
        except Exception as e:
            last_err = str(e)
    return None, None, last_err


def session_with_unique(app_key: str, secret_key: str, unique_key: str, connection_string: str) -> tuple[str | None, dict | None, str | None]:
    client = httpx.Client(timeout=15.0)
    url = clean(connection_string).rstrip("/") + "/user/session"
    try:
        r = client.post(url, json={"appKey": app_key, "secretKey": secret_key, "uniqueKey": unique_key})
        if r.status_code == 200:
            j = r.json()
            if j.get("type") in (True, "success") and j.get("result"):
                return j["result"].get("token"), j["result"], None
        return None, None, r.text
    except Exception as e:
        return None, None, str(e)


def normalize_app_key(raw_key: str) -> str:
    if ":::" in raw_key:
        parts = raw_key.split(":::")
        if len(parts) > 1 and parts[1]:
            return parts[1]
    return raw_key


def decode_user_id(tok: str) -> str | None:
    try:
        parts = tok.split(".")
        if len(parts) >= 2:
            import base64
            p = parts[1]
            p += "=" * ((4 - len(p) % 4) % 4)
            j = json.loads(base64.urlsafe_b64decode(p.encode()).decode())
            uid = j.get("userID") or j.get("userId") or j.get("userid")
            if uid and isinstance(uid, str):
                return uid.split("_")[0]
    except Exception:
        return None
    return None


def derive_cluster_base(cs: str) -> str:
    cs = clean(cs)
    return re.sub(r"/([^/]+)hostlookup/?$", r"/\1interactive", cs)


def get_json_any(client: httpx.Client, headers: dict, urls: list[str]) -> tuple[dict | None, str | None]:
    for u in urls:
        url = clean(u)
        try:
            r = client.get(url, headers=headers)
            if r.status_code == 200:
                return r.json(), url
        except Exception:
            pass
        try:
            c1 = httpx.Client(http2=False, http1=True, timeout=20.0)
            r2 = c1.get(url, headers=headers)
            if r2.status_code == 200:
                return r2.json(), url
        except Exception:
            pass
    return None, None


def main():
    load_env()
    p = argparse.ArgumentParser()
    p.add_argument("--app-key", default=os.getenv("BROKER_API_KEY", ""))
    p.add_argument("--secret-key", default=os.getenv("BROKER_API_SECRET", ""))
    p.add_argument("--base-url", default=os.getenv("JAINAMPROP_BASE_URL", "https://smpb.jainam.in:4143"))
    p.add_argument("--token", default="")
    args = p.parse_args()

    app_key = normalize_app_key((args.app_key or os.getenv("BROKER_API_KEY", "")).strip())
    secret_key = (args.secret_key or os.getenv("BROKER_API_SECRET", "")).strip()
    base_url = clean(args.base_url).rstrip("/")
    token = args.token.strip()

    if not token:
        uk, cs, err = hostlookup(base_url)
        if not (uk and cs):
            print(json.dumps({"status": "error", "message": f"hostlookup failed: {err}"}))
            return
        t, res, err2 = session_with_unique(app_key, secret_key, uk, cs)
        if not t:
            print(json.dumps({"status": "error", "message": f"session failed: {err2}"}))
            return
        token = t

    uid = (os.getenv("JAINAMPROP_USER_ID") or "").strip()
    if not uid:
        uid = decode_user_id(token) or ""


    client = httpx.Client(timeout=20.0)
    cluster_base = ""
    uk2, cs2, _ = hostlookup(base_url)
    if cs2:
        cluster_base = derive_cluster_base(cs2).rstrip("/")

    headers = {"authorization": token, "Content-Type": "application/json", "Accept": "application/json"}

    cluster_base = ""
    uk, cs, err = hostlookup(base_url)
    if not (uk and cs):
        print(json.dumps({"status": "error", "message": f"hostlookup failed: {err}"}))
        return

    cluster_base = derive_cluster_base(cs).rstrip("/")

    # Correct interactive endpoints
    base_int = f"{cluster_base}"
    base_5int = cluster_base.replace("interactive", "5interactive")


    endpoints = [
        ("order_book", "/orders"),
        ("trade_book", "/orders/trades"),
    ]

    results = {}
    for key, ep in endpoints:
        urls = []
        if cluster_base:
            urls.append(f"{clean(cluster_base)}{ep}")
        urls.append(f"{clean(base_int)}{ep}")
        urls.append(f"{clean(base_5int)}{ep}")
        urls = [f"{u}{'&' if '?' in u else '?'}clientID={uid}" if uid else u for u in urls]
        attempt_logs = []
        data, used = None, None
        for u in urls:
            url = clean(u)
            status = None
            body = None
            try:
                r = client.get(url, headers=headers)
                status = r.status_code
                body = (r.text or "")[:500]
                # Log every attempt (including non-200)
                try_body = None
                try:
                    try_body = r.json()
                except Exception:
                    try_body = body
                attempt_logs.append(
                    {
                        "url": url,
                        "status": status,
                        "body": (json.dumps(try_body)[:300] if isinstance(try_body, dict) else str(try_body)[:300]),
                        "proto": "h2",
                    }
                )
                if r.status_code == 200:
                    try:
                        data = r.json()
                        used = url
                        break
                    except Exception:
                        pass
            except Exception as e:
                attempt_logs.append({"url": url, "error": str(e)})
            if not used:
                try:
                    c1 = httpx.Client(http2=False, http1=True, timeout=20.0)
                    r2 = c1.get(url, headers=headers)
                    status = r2.status_code
                    body = (r2.text or "")[:500]
                    # Log h1 attempt as well
                    try_body = None
                    try:
                        try_body = r2.json()
                    except Exception:
                        try_body = body
                    attempt_logs.append(
                        {
                            "url": url,
                            "status": status,
                            "body": (json.dumps(try_body)[:300] if isinstance(try_body, dict) else str(try_body)[:300]),
                            "proto": "h1",
                        }
                    )
                    if r2.status_code == 200:
                        try:
                            data = r2.json()
                            used = url
                            break
                        except Exception:
                            pass
                except Exception as e2:
                    attempt_logs.append({"url": url, "error": str(e2), "proto": "h1"})
        if data is None:
            data, used = {}, ""
        results[key] = data or {}
        results[f"{key}_url"] = used or ""
        results[f"{key}_attempts"] = attempt_logs

    def compact(obj):
        try:
            s = json.dumps(obj)
            return s[:1200]
        except Exception:
            return str(obj)[:1200]

    summary = {
        "order_book_type": (results.get("order_book") or {}).get("type"),
        "trade_book_type": (results.get("trade_book") or {}).get("type"),
    }

    print(json.dumps({"status": "success", "summary": summary, "raw": {
        "order_book": compact(results.get("order_book")),
        "order_book_url": results.get("order_book_url"),
        "order_book_attempts": results.get("order_book_attempts"),
        "trade_book": compact(results.get("trade_book")),
        "trade_book_url": results.get("trade_book_url"),
        "trade_book_attempts": results.get("trade_book_attempts"),
    }}, indent=2))


if __name__ == "__main__":
    main()
