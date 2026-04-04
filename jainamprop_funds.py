import argparse
import base64
import json
import os

import httpx

# Attempt to load .env so BROKER_API_KEY / BROKER_API_SECRET are available for defaults
try:
    from dotenv import load_dotenv  # type: ignore

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
except Exception:
    pass


def clean_url(url: str) -> str:
    if not url:
        return url
    return url.strip().strip("`").strip()


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
                t = j.get("type")
                ok = t in (True, "success") or j.get("code") == "hostlookup"
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


def exchange_unique_for_session(app_key: str, secret_key: str, connection_string: str) -> tuple[str | None, str | None]:
    client = httpx.Client(timeout=15.0)
    url = clean_url(connection_string).rstrip("/") + "/user/session"
    try:
        r = client.post(url, json={"appKey": app_key, "secretKey": secret_key, "uniqueKey": ""})
        return None, "missing uniqueKey"
    except Exception:
        pass
    return None, "unexpected"


def session_with_unique(app_key: str, secret_key: str, unique_key: str, connection_string: str) -> tuple[str | None, dict | None, str | None]:
    client = httpx.Client(timeout=15.0)
    url = clean_url(connection_string).rstrip("/") + "/user/session"
    try:
        r = client.post(url, json={"appKey": app_key, "secretKey": secret_key, "uniqueKey": unique_key})
        if r.status_code == 200:
            j = r.json()
            if j.get("type") in (True, "success") and j.get("result"):
                return j["result"].get("token"), j["result"], None
        return None, None, r.text
    except Exception as e:
        return None, None, str(e)


def decode_user_id(token: str) -> str | None:
    try:
        p = token.split(".")[1]
        rem = len(p) % 4
        if rem:
            p += "=" * (4 - rem)
        data = base64.urlsafe_b64decode(p.encode())
        j = json.loads(data.decode())
        return j.get("userID") or j.get("userId") or j.get("userid")
    except Exception:
        return None


def fetch_balance(base_url: str, token: str, user_id: str | None) -> tuple[dict | None, str | None]:
    client = httpx.Client(timeout=15.0)
    h = {"authorization": token, "Content-Type": "application/json"}
    url1 = base_url.rstrip("/") + "/interactive/user/balance"
    if user_id:
        url1 = url1 + f"?clientID={user_id}"
    try:
        r = client.get(url1, headers=h)
        if r.status_code == 200:
            return r.json(), None
    except Exception as e:
        pass
    url2 = base_url.rstrip("/") + "/5interactive/user/balance"
    if user_id:
        url2 = url2 + f"?clientID={user_id}"
    try:
        r2 = client.get(url2, headers=h)
        if r2.status_code == 200:
            return r2.json(), None
        return None, r2.text
    except Exception as e:
        return None, str(e)


def format_funds(j: dict) -> dict:
    if not isinstance(j, dict):
        return {}
    res = j.get("result") or {}
    blist = res.get("BalanceList") or []
    if not blist:
        return {}
    sub = (((blist[0] or {}).get("limitObject") or {}).get("RMSSubLimits") or {})
    def f(x):
        try:
            if str(x).lower() == "nan":
                return "0.00"
            return f"{float(x):.2f}"
        except Exception:
            return "0.00"
    return {
        "availablecash": f(sub.get("netMarginAvailable", 0)),
        "collateral": f(sub.get("collateral", 0)),
        "m2munrealized": f(sub.get("UnrealizedMTM", 0)),
        "m2mrealized": f(sub.get("RealizedMTM", 0)),
        "utiliseddebits": f(sub.get("marginUtilized", 0)),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--app-key", default=os.getenv("BROKER_API_KEY", ""))
    p.add_argument("--secret-key", default=os.getenv("BROKER_API_SECRET", ""))
    p.add_argument("--base-url", default=os.getenv("JAINAMPROP_BASE_URL", "https://smpb.jainam.in:4143"))
    p.add_argument("--token", default="")
    args = p.parse_args()

    base_url = args.base_url.strip().rstrip("/")
    # Normalize possible client_id:::api_key format
    app_key = (args.app_key or os.getenv("BROKER_API_KEY", "")).strip()
    if ":::" in app_key:
        parts = app_key.split(":::")
        if len(parts) > 1 and parts[1]:
            app_key = parts[1]
    secret_key = (args.secret_key or os.getenv("BROKER_API_SECRET", "")).strip()
    token = args.token.strip()
    user_id = None

    if not app_key or not secret_key:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "Missing appKey/secretKey. Pass --app-key/--secret-key or set BROKER_API_KEY/BROKER_API_SECRET in .env",
                }
            )
        )
        return

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
        user_id = (res or {}).get("userID")
    if not user_id:
        user_id = decode_user_id(token)

    data, ferr = fetch_balance(base_url, token, user_id)
    if not data:
        print(json.dumps({"status": "error", "message": ferr or "fetch failed"}))
        return
    funds = format_funds(data)
    print(json.dumps({"status": "success", "funds": funds, "raw": data}))


if __name__ == "__main__":
    main()
