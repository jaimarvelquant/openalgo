import os
import sys
from contextlib import contextmanager

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from broker.jainam_prop.api.config import get_jainam_base_url, get_jainam_credentials


@contextmanager
def env(**overrides):
    original = {name: os.environ.get(name) for name in overrides}
    try:
        for key, value in overrides.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _install_default_credentials():
    os.environ.setdefault("JAINAM_ACTIVE_SYMPHONY_SERVER", "B")
    os.environ.setdefault("JAINAM_ACTIVE_ACCOUNT_TYPE", "PRO")
    os.environ.setdefault("JAINAM_SYMPHONY_B_PRO_INTERACTIVE_API_KEY", "ik")
    os.environ.setdefault("JAINAM_SYMPHONY_B_PRO_INTERACTIVE_API_SECRET", "is")
    os.environ.setdefault("JAINAM_SYMPHONY_B_PRO_MARKET_API_KEY", "mk")
    os.environ.setdefault("JAINAM_SYMPHONY_B_PRO_MARKET_API_SECRET", "ms")
    os.environ.setdefault("JAINAM_SYMPHONY_B_PRO_CLIENT_ID", "ZZJ13048")


@pytest.mark.parametrize(
    "server,expected",
    [
        ("A", "https://smpa.jainam.in:6543"),
        ("B", "https://smpb.jainam.in:4143"),
        ("C", "https://smpc.jainam.in:14543"),
    ],
)
def test_get_jainam_base_url(server, expected):
    _install_default_credentials()
    with env(JAINAM_ACTIVE_SYMPHONY_SERVER=server):
        assert get_jainam_base_url() == expected


def test_get_jainam_base_url_invalid_server():
    _install_default_credentials()
    with env(JAINAM_ACTIVE_SYMPHONY_SERVER="Z"):
        with pytest.raises(ValueError):
            get_jainam_base_url()


def test_get_jainam_credentials_returns_expected_tuple():
    _install_default_credentials()
    creds = get_jainam_credentials()
    assert creds == ("ik", "is", "mk", "ms", "B", "PRO", "ZZJ13048")


def test_get_jainam_credentials_requires_all_fields():
    _install_default_credentials()
    with env(JAINAM_SYMPHONY_B_PRO_MARKET_API_KEY=None):
        with pytest.raises(ValueError) as exc:
            get_jainam_credentials()
        assert "MARKET_API_KEY" in str(exc.value)


def test_get_jainam_credentials_warns_on_client_id_mismatch(caplog):
    _install_default_credentials()
    with env(JAINAM_SYMPHONY_B_PRO_CLIENT_ID="WRONG"):
        caplog.clear()
        with caplog.at_level("WARNING"):
            creds = get_jainam_credentials()
        assert creds[-1] == "WRONG"
        assert "clientid" in caplog.text.lower()


def test_get_jainam_credentials_switch_account_type():
    _install_default_credentials()

    os.environ["JAINAM_SYMPHONY_B_NORMAL_INTERACTIVE_API_KEY"] = "nik"
    os.environ["JAINAM_SYMPHONY_B_NORMAL_INTERACTIVE_API_SECRET"] = "nis"
    os.environ["JAINAM_SYMPHONY_B_NORMAL_MARKET_API_KEY"] = "nmk"
    os.environ["JAINAM_SYMPHONY_B_NORMAL_MARKET_API_SECRET"] = "nms"
    os.environ["JAINAM_SYMPHONY_B_NORMAL_CLIENT_ID"] = "DLL7182"

    with env(JAINAM_ACTIVE_ACCOUNT_TYPE="NORMAL"):
        creds = get_jainam_credentials()
        assert creds == ("nik", "nis", "nmk", "nms", "B", "NORMAL", "DLL7182")
