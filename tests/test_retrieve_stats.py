import json
import re
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from retrieve_stats import fetch_user_by_uid, save_json, transform_profile, utc_stamp

_FIXTURES = json.loads(
    (Path(__file__).parent / "fixtures" / "transform_profile_cases.json").read_text()
)


def test_utc_stamp_format():
    assert re.fullmatch(r"\d{8}T\d{6}Z", utc_stamp())


@pytest.mark.parametrize("case", _FIXTURES, ids=[c["id"] for c in _FIXTURES])
def test_transform_profile(case):
    assert transform_profile(case["raw"], case["stamp"]) == case["expected"]


def test_save_json_creates_dirs_and_writes(tmp_path):
    data = {"players": 3, "active": True}
    dest = tmp_path / "subdir" / "out.json"
    save_json(dest, data)
    assert json.loads(dest.read_text()) == data


@pytest.fixture
def mock_ok_response():
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"global": {"name": "TestPlayer"}}
    return response


@patch("retrieve_stats.requests.get")
def test_fetch_user_by_uid_calls_correct_endpoint(mock_get, mock_ok_response):
    mock_get.return_value = mock_ok_response

    result = fetch_user_by_uid("my_api_key", "123456")

    mock_get.assert_called_once_with(
        "https://api.mozambiquehe.re/bridge",
        params={"auth": "my_api_key", "uid": "123456", "platform": "X1"},
        timeout=20,
    )
    assert result == {"global": {"name": "TestPlayer"}}


@patch("retrieve_stats.requests.get")
def test_fetch_user_by_uid_raises_on_http_error(mock_get):
    mock_get.return_value = Mock(status_code=403, text="Forbidden")

    with pytest.raises(RuntimeError, match="HTTP 403"):
        fetch_user_by_uid("bad_key", "123456")
