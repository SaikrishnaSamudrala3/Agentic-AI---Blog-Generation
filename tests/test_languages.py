import pytest

from src.config.languages import normalize_language


def test_normalize_language_treats_english_as_default():
    assert normalize_language("English") is None


def test_normalize_language_accepts_supported_language():
    assert normalize_language(" Spanish ") == "spanish"


def test_normalize_language_rejects_unsupported_language():
    with pytest.raises(ValueError, match="not supported"):
        normalize_language("Klingon")
