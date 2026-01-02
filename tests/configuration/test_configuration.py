"""Tests for Configuration class integration with ConfigurationLoader."""

from __future__ import annotations

import warnings
from pathlib import Path
from unittest.mock import patch

import pytest

from buvis.pybase.configuration.configuration import Configuration


class TestExplicitPath:
    """Tests for explicit file_path argument."""

    def test_explicit_path_used(self, tmp_path: Path) -> None:
        """Configuration uses explicit path when provided."""
        config_file = tmp_path / "explicit.yaml"
        config_file.write_text("key: explicit_value\n")

        cfg = Configuration(config_file)

        assert cfg.get_configuration_item("key") == "explicit_value"
        assert cfg.path_config_file == config_file.absolute()

    def test_explicit_path_missing_raises(self, tmp_path: Path) -> None:
        """FileNotFoundError raised when explicit path doesn't exist."""
        missing = tmp_path / "missing.yaml"

        with pytest.raises(FileNotFoundError, match="was not found"):
            Configuration(missing)


class TestAutoDiscovery:
    """Tests for auto-discovery via ConfigurationLoader."""

    def test_discovery_used_when_no_explicit_path(self, tmp_path: Path) -> None:
        """Auto-discovery finds config when no explicit path provided."""
        config_file = tmp_path / "buvis.yaml"
        config_file.write_text("discovered: true\n")

        with patch(
            "buvis.pybase.configuration.configuration.ConfigurationLoader.find_config_files",
            return_value=[config_file.resolve()],
        ):
            cfg = Configuration()

        assert cfg.get_configuration_item("discovered") is True

    def test_discovery_returns_first_file(self, tmp_path: Path) -> None:
        """First discovered file (highest priority) is used."""
        first = tmp_path / "first.yaml"
        second = tmp_path / "second.yaml"
        first.write_text("source: first\n")
        second.write_text("source: second\n")

        with patch(
            "buvis.pybase.configuration.configuration.ConfigurationLoader.find_config_files",
            return_value=[first.resolve(), second.resolve()],
        ):
            cfg = Configuration()

        assert cfg.get_configuration_item("source") == "first"

    def test_discovery_empty_falls_through(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Empty discovery falls through to env/default."""
        fake_home = tmp_path / "empty_home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        with (
            patch(
                "buvis.pybase.configuration.configuration.ConfigurationLoader.find_config_files",
                return_value=[],
            ),
            patch.dict("os.environ", {}, clear=True),
        ):
            # No discovery, no env var, no default file = no config
            cfg = Configuration()

        assert not hasattr(cfg, "path_config_file")


class TestDeprecationWarning:
    """Tests for BUVIS_CONFIG_FILE deprecation warning."""

    def test_warns_when_env_var_used(self, tmp_path: Path) -> None:
        """DeprecationWarning emitted when BUVIS_CONFIG_FILE is used."""
        config_file = tmp_path / "env_config.yaml"
        config_file.write_text("from_env: true\n")

        with (
            patch(
                "buvis.pybase.configuration.configuration.ConfigurationLoader.find_config_files",
                return_value=[],
            ),
            patch.dict("os.environ", {"BUVIS_CONFIG_FILE": str(config_file)}),
            pytest.warns(DeprecationWarning, match="BUVIS_CONFIG_FILE is deprecated"),
        ):
            Configuration()

    def test_no_warning_when_env_var_not_set(self, tmp_path: Path) -> None:
        """No warning when BUVIS_CONFIG_FILE not set."""
        with (
            patch(
                "buvis.pybase.configuration.configuration.ConfigurationLoader.find_config_files",
                return_value=[],
            ),
            patch.dict("os.environ", {}, clear=True),
            warnings.catch_warnings(record=True) as w,
        ):
            warnings.simplefilter("always")
            Configuration()

        deprecation_warnings = [
            x for x in w if issubclass(x.category, DeprecationWarning)
        ]
        assert len(deprecation_warnings) == 0

    def test_no_warning_when_discovery_succeeds(self, tmp_path: Path) -> None:
        """No warning when auto-discovery finds config."""
        config_file = tmp_path / "discovered.yaml"
        config_file.write_text("key: value\n")

        with (
            patch(
                "buvis.pybase.configuration.configuration.ConfigurationLoader.find_config_files",
                return_value=[config_file.resolve()],
            ),
            patch.dict("os.environ", {"BUVIS_CONFIG_FILE": "/ignored/path.yaml"}),
            warnings.catch_warnings(record=True) as w,
        ):
            warnings.simplefilter("always")
            Configuration()

        deprecation_warnings = [
            x for x in w if issubclass(x.category, DeprecationWarning)
        ]
        assert len(deprecation_warnings) == 0


class TestDefaultPath:
    """Tests for default path fallback."""

    def test_default_path_used_when_exists(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Default ~/.config/buvis/config.yaml used when it exists."""
        fake_home = tmp_path / "home"
        config_dir = fake_home / ".config" / "buvis"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("default: true\n")

        monkeypatch.setattr(Path, "home", lambda: fake_home)

        with (
            patch(
                "buvis.pybase.configuration.configuration.ConfigurationLoader.find_config_files",
                return_value=[],
            ),
            patch.dict("os.environ", {}, clear=True),
        ):
            cfg = Configuration()

        assert cfg.get_configuration_item("default") is True

    def test_none_when_no_config_found(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Returns None when no config file found anywhere."""
        fake_home = tmp_path / "empty_home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        with (
            patch(
                "buvis.pybase.configuration.configuration.ConfigurationLoader.find_config_files",
                return_value=[],
            ),
            patch.dict("os.environ", {}, clear=True),
        ):
            cfg = Configuration()

        assert not hasattr(cfg, "path_config_file")


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing behavior."""

    def test_cfg_singleton_works(self) -> None:
        """Global cfg singleton remains functional."""
        from buvis.pybase.configuration import cfg

        # Should not raise - singleton is created at import
        assert cfg is not None

    def test_explicit_path_takes_precedence(self, tmp_path: Path) -> None:
        """Explicit path always takes precedence over discovery."""
        explicit = tmp_path / "explicit.yaml"
        discovered = tmp_path / "discovered.yaml"
        explicit.write_text("source: explicit\n")
        discovered.write_text("source: discovered\n")

        with patch(
            "buvis.pybase.configuration.configuration.ConfigurationLoader.find_config_files",
            return_value=[discovered.resolve()],
        ):
            cfg = Configuration(explicit)

        assert cfg.get_configuration_item("source") == "explicit"


class TestEnvSubstitution:
    """Tests for enable_env_substitution parameter."""

    def test_disabled_by_default(self, tmp_path: Path) -> None:
        """Env substitution is disabled by default (backward compat)."""
        config = tmp_path / "config.yaml"
        config.write_text("value: ${MY_VAR}\n")

        cfg = Configuration(config)

        # Should remain literal, not substituted
        assert cfg.get_configuration_item("value") == "${MY_VAR}"

    def test_enabled_substitutes_env_vars(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Env vars substituted when enabled."""
        monkeypatch.setenv("MY_VAR", "substituted_value")
        config = tmp_path / "config.yaml"
        config.write_text("value: ${MY_VAR}\n")

        cfg = Configuration(config, enable_env_substitution=True)

        assert cfg.get_configuration_item("value") == "substituted_value"

    def test_default_syntax_when_var_unset(self, tmp_path: Path) -> None:
        """${VAR:-default} uses default when var unset."""
        config = tmp_path / "config.yaml"
        config.write_text("value: ${UNSET_VAR:-fallback}\n")

        cfg = Configuration(config, enable_env_substitution=True)

        assert cfg.get_configuration_item("value") == "fallback"

    def test_hostname_preserved_after_load(self, tmp_path: Path) -> None:
        """Hostname is set after loading config."""
        import platform

        config = tmp_path / "config.yaml"
        config.write_text("key: value\n")

        cfg = Configuration(config)

        assert cfg.get_configuration_item("hostname") == platform.node()

    def test_hostname_not_overwritten_by_config(self, tmp_path: Path) -> None:
        """Config file hostname value doesn't override platform.node()."""
        import platform

        config = tmp_path / "config.yaml"
        config.write_text("hostname: fake_host\nkey: value\n")

        cfg = Configuration(config)

        # Platform hostname should win (set after load)
        assert cfg.get_configuration_item("hostname") == platform.node()
