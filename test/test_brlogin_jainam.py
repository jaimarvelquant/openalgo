import pytest
from flask import Flask, Response

from blueprints.brlogin import brlogin_bp
from limiter import limiter


@pytest.fixture
def flask_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"

    limiter.init_app(app)
    app.register_blueprint(brlogin_bp)

    return app


def test_jainam_prop_direct_login_flow(monkeypatch, flask_app):
    captured = {}

    flask_app.broker_auth_functions = {
        "jainam_prop_auth": lambda: ("auth-token", "feed-token", "user-123", None)
    }

    def fake_success(auth_token, user_session_key, broker, feed_token=None, user_id=None):
        captured["success"] = (
            auth_token,
            user_session_key,
            broker,
            feed_token,
            user_id,
        )
        return Response("redirect", status=302)

    def fake_failure(*_args, **_kwargs):
        raise AssertionError("handle_auth_failure should not be called for success path")

    monkeypatch.setattr("blueprints.brlogin.handle_auth_success", fake_success)
    monkeypatch.setattr("blueprints.brlogin.handle_auth_failure", fake_failure)

    with flask_app.test_client() as client:
        with client.session_transaction() as session:
            session["user"] = "demo-user"

        response = client.get("/jainam_prop/callback")

    assert response.status_code == 302
    assert captured["success"] == (
        "auth-token",
        "demo-user",
        "jainam_prop",
        "feed-token",
        "user-123",
    )
