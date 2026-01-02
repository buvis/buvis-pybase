"""Tests for the configuration model validators."""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from buvis.pybase.configuration import (
    MAX_NESTING_DEPTH,
    get_model_depth,
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
