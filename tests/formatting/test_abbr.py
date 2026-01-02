from __future__ import annotations

from pathlib import Path

from buvis.pybase.configuration import Configuration
from buvis.pybase.formatting.string_operator.abbr import Abbr


class TestAbbrWithConfig:
    """Tests for Abbr.replace_abbreviations with config parameter."""

    def test_config_loads_abbreviations(self, tmp_path: Path) -> None:
        """Config parameter loads abbreviations from Configuration."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "abbreviations:\n"
            "  - API: Application Programming Interface\n"
            "  - CLI: Command Line Interface\n"
        )
        config = Configuration(config_file)

        result = Abbr.replace_abbreviations("Use the API", config=config, level=1)

        assert result == "Use the Application Programming Interface"

    def test_config_ignored_when_abbreviations_provided(self, tmp_path: Path) -> None:
        """Explicit abbreviations take precedence over config."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("abbreviations:\n  - API: Wrong\n")
        config = Configuration(config_file)

        result = Abbr.replace_abbreviations(
            "Use the API",
            abbreviations=[{"API": "Correct"}],
            config=config,
            level=1,
        )

        assert result == "Use the Correct"

    def test_no_config_returns_empty_abbreviations(self) -> None:
        """Without config or abbreviations, text is unchanged."""
        result = Abbr.replace_abbreviations("Use the API", level=1)

        assert result == "Use the API"

    def test_config_without_abbreviations_key(self, tmp_path: Path) -> None:
        """Config without abbreviations key returns empty list."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("other_key: value\n")
        config = Configuration(config_file)

        result = Abbr.replace_abbreviations("Use the API", config=config, level=1)

        assert result == "Use the API"
