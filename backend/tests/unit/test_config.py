import pytest

from app.config import Config


@pytest.fixture(autouse=True)
def _isolated_data_dir(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATA_DIR", str(tmp_path))


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(None, True), ("", True), ("true", True), ("1", True), ("FALSE", False), ("off", False)],
)
def test_allow_registration_parsing(
    monkeypatch: pytest.MonkeyPatch, raw: str | None, expected: bool
) -> None:
    if raw is None:
        monkeypatch.delenv("ALLOW_REGISTRATION", raising=False)
    else:
        monkeypatch.setenv("ALLOW_REGISTRATION", raw)

    assert Config().allow_registration is expected


def test_allow_registration_rejects_invalid_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOW_REGISTRATION", "talvez")

    with pytest.raises(ValueError, match="ALLOW_REGISTRATION"):
        Config()


def test_is_demo_defaults_to_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IS_DEMO", raising=False)

    assert Config().is_demo is False


def test_is_demo_true_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IS_DEMO", "true")

    assert Config().is_demo is True
