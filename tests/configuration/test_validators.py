"""Tests for the configuration model validators."""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from buvis.pybase.configuration import (
    MAX_JSON_ENV_SIZE,
    MAX_NESTING_DEPTH,
    get_model_depth,
    validate_json_env_size,
    validate_nesting_depth,
)


class Level0Valid(BaseModel):
    value: str = "leaf"


class Level1(BaseModel):
    child: Level0Valid


class Level2(BaseModel):
    child: Level1


class Level3(BaseModel):
    child: Level2


class Level4(BaseModel):
    child: Level3


class Level5(BaseModel):
    child: Level4


class Level6Invalid(BaseModel):
    child: Level5


class TestGetModelDepth:
    def test_flat_model_depth_zero(self) -> None:
        assert get_model_depth(Level0Valid) == 0

    def test_nested_model_depth_five(self) -> None:
        assert get_model_depth(Level5) == MAX_NESTING_DEPTH

    def test_nested_model_depth_six(self) -> None:
        assert get_model_depth(Level6Invalid) == MAX_NESTING_DEPTH + 1


class TestValidateNestingDepth:
    def test_valid_depth_passes(self) -> None:
        validate_nesting_depth(Level5)

    def test_invalid_depth_raises_valueerror(self) -> None:
        with pytest.raises(ValueError):
            validate_nesting_depth(Level6Invalid)


class TestMaxJsonEnvSizeConstant:
    def test_max_json_env_size_equals_expected_value(self) -> None:
        assert MAX_JSON_ENV_SIZE == 64 * 1024


class TestValidateJsonEnvSize:
    def test_passes_for_empty_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        env_var = "TEST_JSON_ENV"
        monkeypatch.delenv(env_var, raising=False)

        validate_json_env_size(env_var)

    def test_passes_at_exact_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        env_var = "TEST_JSON_ENV"
        payload = "a" * MAX_JSON_ENV_SIZE
        monkeypatch.setenv(env_var, payload)

        validate_json_env_size(env_var)

    def test_raises_over_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        env_var = "TEST_JSON_ENV"
        payload = "a" * (MAX_JSON_ENV_SIZE + 1)
        monkeypatch.setenv(env_var, payload)

        with pytest.raises(ValueError):
            validate_json_env_size(env_var)

    def test_utf8_multibyte_chars_counted_correctly(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        env_var = "TEST_JSON_ENV"
        multibyte_char = "é"
        payload = multibyte_char * (
            MAX_JSON_ENV_SIZE // len(multibyte_char.encode("utf-8"))
        )
        monkeypatch.setenv(env_var, payload)

        validate_json_env_size(env_var)

        payload_over = payload + multibyte_char
        monkeypatch.setenv(env_var, payload_over)

        with pytest.raises(ValueError):
            validate_json_env_size(env_var)
