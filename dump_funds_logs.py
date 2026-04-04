import json
import os

# Load .env so DATABASE_URL is available for SQLAlchemy
try:
    from dotenv import load_dotenv  # type: ignore

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
except Exception:
    pass

# Provide fallback for DATABASE_URL if not set
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///db/openalgo.db"

from database.apilog_db import OrderLog, db_session


def main():
    types = ["jainamprop_funds_snapshot", "jainamprop_funds_unavailable"]
    rows = (
        db_session.query(OrderLog)
        .filter(OrderLog.api_type.in_(types))
        .order_by(OrderLog.created_at.desc())
        .limit(20)
        .all()
    )
    out = []
    for r in rows:
        try:
            req = json.loads(r.request_data or "{}")
        except Exception:
            req = {"raw": r.request_data}
        try:
            resp = json.loads(r.response_data or "{}")
        except Exception:
            resp = {"raw": r.response_data}
        out.append(
            {
                "created_at": str(r.created_at),
                "request": req,
                "response": resp,
            }
        )
    print(json.dumps({"count": len(out), "logs": out}, indent=2))


if __name__ == "__main__":
    main()
