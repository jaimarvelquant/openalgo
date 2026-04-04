import argparse
import json
import os
import re
import httpx
def get_env_var(name: str, default: str = "") -> str:
    val = os.getenv(name, default)
    if val is None:
        return default
    # Strip spaces and quotes so .env variations don't break things
    return val.strip().strip('"').strip("'")

def load_env():
    try:
        from dotenv import load_dotenv  # type: ignore
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
    except Exception:
        pass

def clean(s: str) -> str:
    return s.strip().strip("`").strip() if s else s

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

def derive_cluster_base(cs: str) -> str:
    cs = clean(cs)
    return re.sub(r"/([^/]+)hostlookup/?$", r"/\1interactive", cs)

def main():
    load_env()
    p = argparse.ArgumentParser()
    p.add_argument("--app-key", default=os.getenv("BROKER_API_KEY", ""))
    p.add_argument("--secret-key", default=os.getenv("BROKER_API_SECRET", ""))
    p.add_argument("--base-url", default=os.getenv("JAINAMPROP_BASE_URL", "https://smpb.jainam.in:4143"))
    p.add_argument("--token", default="")
    args = p.parse_args()

    app_key = normalize_app_key(get_env_var("BROKER_API_KEY"))
    secret_key = get_env_var("BROKER_API_SECRET")
    base_url = clean(get_env_var("JAINAMPROP_BASE_URL", "https://smpb.jainam.in:4143")).rstrip("/")
    token = args.token.strip()

    uid = get_env_var("JAINAMPROP_USER_ID")


    # Bypass login loop and forcibly pull active DB token
    if not token:
        try:
            from database.auth_db import get_auth_token
            token = get_auth_token("jainamprop")
            if not token:
                print(json.dumps({"status": "error", "message": "No active Jainamprop token found in database. Please log in through the UI."}))
                return
        except Exception as e:
            print(json.dumps({"status": "error", "message": f"Could not retrieve token: {e}"}))
            return



    # Simulate typical Jainamprop loadbalancer path
    cluster_base = f"{base_url}/interactive"
    print(f"[INFO] Using clientID={uid}")
    print(f"[INFO] Using cluster_base={cluster_base}")

    headers = {"authorization": token, "Content-Type": "application/json", "Accept": "application/json"}

    order_url = f"{cluster_base}/orders?clientID={uid}"
    trade_url = f"{cluster_base}/orders/trades?clientID={uid}"

    client = httpx.Client(timeout=20.0)

    order_resp = client.get(order_url, headers=headers)
    trade_resp = client.get(trade_url, headers=headers)

    def safe_json(resp):
        try:
            return resp.json()
        except Exception:
            return resp.text

    print(json.dumps({
        "status": "success",
        "order_book": safe_json(order_resp),
        "order_book_url": order_url,
        "trade_book": safe_json(trade_resp),
        "trade_book_url": trade_url
    }, indent=2))

if __name__ == "__main__":
    main()
