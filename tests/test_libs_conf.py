# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Provide regression coverage for selected AppConfig update paths.
"""

import tempfile
import unittest

from pathlib import Path
from typing import List
from unittest.mock import PropertyMock, patch

from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.logstool import LoggerQueue

from libs.conf import AppConfig


class _CollectingLogger(object):
    """Collect logger messages for config-load validation tests."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self) -> None:
        """Initialize the collector."""
        self.warnings: List[str] = []

    # #[PUBLIC PROPERTIES]#############################################################
    @property
    def message_critical(self) -> str:
        """Return the last critical message or an empty string.

        ### Returns:
        str - Last critical message.
        """
        return ""

    @message_critical.setter
    def message_critical(self, value: str) -> None:
        """Ignore critical messages in this collector.

        ### Arguments:
        * value: str - Critical message.
        """
        del value

    @property
    def message_debug(self) -> str:
        """Return the last debug message or an empty string.

        ### Returns:
        str - Last debug message.
        """
        return ""

    @message_debug.setter
    def message_debug(self, value: str) -> None:
        """Ignore debug messages in this collector.

        ### Arguments:
        * value: str - Debug message.
        """
        del value

    @property
    def message_error(self) -> str:
        """Return the last error message or an empty string.

        ### Returns:
        str - Last error message.
        """
        return ""

    @message_error.setter
    def message_error(self, value: str) -> None:
        """Ignore error messages in this collector.

        ### Arguments:
        * value: str - Error message.
        """
        del value

    @property
    def message_info(self) -> str:
        """Return the last info message or an empty string.

        ### Returns:
        str - Last info message.
        """
        return ""

    @message_info.setter
    def message_info(self, value: str) -> None:
        """Ignore info messages in this collector.

        ### Arguments:
        * value: str - Info message.
        """
        del value

    @property
    def message_warning(self) -> str:
        """Return the last warning message or an empty string.

        ### Returns:
        str - Last warning message.
        """
        if not self.warnings:
            return ""
        return self.warnings[-1]

    @message_warning.setter
    def message_warning(self, value: str) -> None:
        """Store a warning message.

        ### Arguments:
        * value: str - Warning message.
        """
        self.warnings.append(value)


class TestAppConfig(unittest.TestCase):
    """Cover selected configuration update scenarios."""

    # #[PRIVATE METHODS]###############################################################
    def __build_config(self, config_file: Path) -> AppConfig:
        """Create an `AppConfig` instance bound to the temporary config file.

        ### Arguments:
        * config_file: Path - Path to the temporary config file.

        ### Returns:
        AppConfig - Config service prepared for tests.
        """
        obj = AppConfig(qlog=LoggerQueue(), app_name="AASd")
        obj.config_file = str(config_file)
        return obj

    def __prepare_existing_file(
        self, config_file: Path, with_plugins_dir: bool
    ) -> None:
        """Write a minimal existing main-section configuration.

        ### Arguments:
        * config_file: Path - Path to the temporary config file.
        * with_plugins_dir: bool - Whether to include `plugins_dir`.
        """
        cfg = ConfigTool(str(config_file), "AASd", auto_create=True)
        cfg.set("aasd", desc="AASd configuration file")
        cfg.set("aasd", varname="debug", value=False)
        cfg.set("aasd", varname="verbose", value=False)
        cfg.set("aasd", varname="salt", value=123456)
        if with_plugins_dir:
            cfg.set("aasd", varname="plugins_dir", value="./plugins")
        self.assertTrue(cfg.save())

    def __write_test_plugin(self, plugin_dir: Path) -> None:
        """Write a simple plugin manifest for config-render tests.

        ### Arguments:
        * plugin_dir: Path - Target plugin directory path.
        """
        plugin_dir.mkdir()
        (plugin_dir / "load.py").write_text(
            "\n".join(
                [
                    "from libs.plugins import PluginKind, PluginSpec",
                    "from libs.templates import PluginConfigField, PluginConfigSchema",
                    "",
                    "def _runtime(_context):",
                    "    class Runtime(object):",
                    "        def start(self):",
                    "            return None",
                    "        def stop(self):",
                    "            return None",
                    "        def is_stopped(self):",
                    "            return True",
                    "    return Runtime()",
                    "",
                    "def get_plugin_spec():",
                    "    return PluginSpec(",
                    "        api_version=1,",
                    "        config_schema=PluginConfigSchema(",
                    "            title='Sample plugin.',",
                    "            fields=[",
                    "                PluginConfigField(",
                    "                    name='channel',",
                    "                    field_type=int,",
                    "                    default=3,",
                    "                    required=True,",
                    "                    description='Sample channel.',",
                    "                )",
                    "            ],",
                    "        ),",
                    "        plugin_id='sample.plugin',",
                    "        plugin_kind=PluginKind.WORKER,",
                    "        plugin_name='sample_plugin',",
                    "        runtime_factory=_runtime,",
                    "    )",
                ]
            ),
            encoding="utf-8",
        )

    def __write_validation_test_plugin(self, plugin_dir: Path) -> None:
        """Write a plugin manifest with scheduling fields for validation tests.

        ### Arguments:
        * plugin_dir: Path - Target plugin directory path.
        """
        plugin_dir.mkdir()
        (plugin_dir / "load.py").write_text(
            "\n".join(
                [
                    "from libs.plugins import PluginKind, PluginSpec",
                    "from libs.templates import PluginConfigField, PluginConfigSchema",
                    "",
                    "def _runtime(_context):",
                    "    class Runtime(object):",
                    "        def start(self):",
                    "            return None",
                    "        def stop(self):",
                    "            return None",
                    "        def is_stopped(self):",
                    "            return True",
                    "    return Runtime()",
                    "",
                    "def get_plugin_spec():",
                    "    return PluginSpec(",
                    "        api_version=1,",
                    "        config_schema=PluginConfigSchema(",
                    "            title='Validation plugin.',",
                    "            fields=[",
                    "                PluginConfigField(",
                    "                    name='message_channel',",
                    "                    field_type=list,",
                    "                    default=[1],",
                    "                    required=False,",
                    "                    description='Dispatcher targets.',",
                    "                ),",
                    "                PluginConfigField(",
                    "                    name='at_channel',",
                    "                    field_type=list,",
                    "                    default=[],",
                    "                    required=False,",
                    "                    description='Cron-like dispatcher targets.',",
                    "                )",
                    "            ],",
                    "        ),",
                    "        plugin_id='validation.plugin',",
                    "        plugin_kind=PluginKind.WORKER,",
                    "        plugin_name='validation_plugin',",
                    "        runtime_factory=_runtime,",
                    "    )",
                ]
            ),
            encoding="utf-8",
        )

    # #[PUBLIC METHODS]################################################################
    def test_01_should_update_existing_plugins_dir_only_in_update_mode(self) -> None:
        """Persist `plugins_dir` for an existing file only when update mode is enabled."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "aasd.conf"
            self.__prepare_existing_file(config_file, with_plugins_dir=True)

            obj = self.__build_config(config_file)
            obj.plugins_dir = "/tmp/plugins-new"
            self.assertTrue(obj.load())
            self.assertFalse(obj.config_review_required)
            self.assertIsNone(obj.config_review_message)

            check_cfg = ConfigTool(str(config_file), "AASd")
            self.assertTrue(check_cfg.load())
            self.assertIn(
                check_cfg.get("aasd", "plugins_dir"), ("./plugins", ".plugins")
            )

            obj = self.__build_config(config_file)
            obj.plugins_dir = "/tmp/plugins-new"
            obj.update = True
            self.assertTrue(obj.load())
            self.assertFalse(obj.config_review_required)
            self.assertIsNone(obj.config_review_message)

            check_cfg = ConfigTool(str(config_file), "AASd")
            self.assertTrue(check_cfg.load())
            self.assertEqual(check_cfg.get("aasd", "plugins_dir"), "/tmp/plugins-new")

    def test_02_should_add_default_plugins_dir_to_existing_file_in_update_mode(
        self,
    ) -> None:
        """Add missing `plugins_dir` to an old config when update mode is enabled."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "aasd.conf"
            self.__prepare_existing_file(config_file, with_plugins_dir=False)

            obj = self.__build_config(config_file)
            obj.update = True
            self.assertTrue(obj.load())
            self.assertTrue(obj.config_review_required)
            self.assertIsNotNone(obj.config_review_message)
            self.assertIn("[aasd].plugins_dir", obj.config_review_message or "")

            check_cfg = ConfigTool(str(config_file), "AASd")
            self.assertTrue(check_cfg.load())
            self.assertEqual(
                check_cfg.get("aasd", "plugins_dir"),
                f"{Path(__file__).resolve().parent.parent}/plugins",
            )

    def test_03_should_return_directory_containing_aasd_py(self) -> None:
        """Return the absolute project directory that contains `aasd.py`."""
        obj = self.__build_config(Path("/tmp/unused.conf"))

        app_dir = Path(obj.get_app_dir)

        self.assertTrue(app_dir.is_absolute())
        self.assertEqual(app_dir, Path(__file__).resolve().parent.parent)
        self.assertTrue((app_dir / "aasd.py").is_file())

    def test_04_should_create_plugin_sections_for_discovered_instances(self) -> None:
        """Create default plugin sections for discovered plugin instances."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "aasd.conf"
            plugins_dir = Path(tmp_dir) / "plugins"
            plugins_dir.mkdir()
            self.__write_test_plugin(plugins_dir / "sample_plugin")

            obj = self.__build_config(config_file)
            obj.plugins_dir = str(plugins_dir)

            self.assertTrue(obj.load())
            self.assertTrue(obj.config_review_required)
            self.assertIsNotNone(obj.config_review_message)
            self.assertIn("new configuration file", obj.config_review_message or "")

            check_cfg = ConfigTool(str(config_file), "AASd")
            self.assertTrue(check_cfg.load())
            self.assertTrue(check_cfg.has_section("sample_plugin"))
            self.assertEqual(check_cfg.get("sample_plugin", "channel"), 3)

    def test_05_should_flag_review_when_missing_plugin_section_is_added(self) -> None:
        """Request operator review after adding a new plugin section."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "aasd.conf"
            plugins_dir = Path(tmp_dir) / "plugins"
            plugins_dir.mkdir()
            self.__prepare_existing_file(config_file, with_plugins_dir=True)
            self.__write_test_plugin(plugins_dir / "sample_plugin")

            obj = self.__build_config(config_file)
            obj.plugins_dir = str(plugins_dir)

            self.assertTrue(obj.load())
            self.assertTrue(obj.config_review_required)
            self.assertIsNotNone(obj.config_review_message)
            self.assertIn("[sample_plugin]", obj.config_review_message or "")

            check_cfg = ConfigTool(str(config_file), "AASd")
            self.assertTrue(check_cfg.load())
            self.assertTrue(check_cfg.has_section("sample_plugin"))
            self.assertEqual(check_cfg.get("sample_plugin", "channel"), 3)

    def test_06_should_flag_review_when_missing_plugin_option_is_added(self) -> None:
        """Request operator review after adding a new plugin option."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "aasd.conf"
            plugins_dir = Path(tmp_dir) / "plugins"
            plugins_dir.mkdir()
            self.__prepare_existing_file(config_file, with_plugins_dir=True)
            self.__write_test_plugin(plugins_dir / "sample_plugin")

            cfg = ConfigTool(str(config_file), "AASd", auto_create=True)
            cfg.set("sample_plugin", desc="Sample plugin.")
            self.assertTrue(cfg.save())

            obj = self.__build_config(config_file)
            obj.plugins_dir = str(plugins_dir)

            self.assertTrue(obj.load())
            self.assertTrue(obj.config_review_required)
            self.assertIsNotNone(obj.config_review_message)
            self.assertIn("[sample_plugin].channel", obj.config_review_message or "")

            check_cfg = ConfigTool(str(config_file), "AASd")
            self.assertTrue(check_cfg.load())
            self.assertEqual(check_cfg.get("sample_plugin", "channel"), 3)

    def test_07_should_return_empty_plugin_list_when_plugins_dir_is_not_set(
        self,
    ) -> None:
        """Return an empty list when no plugins directory is configured."""
        obj = self.__build_config(Path("/tmp/unused.conf"))

        self.assertEqual(obj.get_plugins, [])

    def test_08_should_return_empty_plugin_list_when_discovery_raises(self) -> None:
        """Return an empty list when plugin discovery fails."""
        obj = self.__build_config(Path("/tmp/unused.conf"))
        obj.plugins_dir = "/tmp/nonexistent"

        with patch("libs.conf.PluginLoader.discover", side_effect=RuntimeError("boom")):
            self.assertEqual(obj.get_plugins, [])

    def test_09_should_read_debug_and_verbose_from_loaded_main_section(self) -> None:
        """Read effective debug and verbose flags from the main config section."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "aasd.conf"
            cfg = ConfigTool(str(config_file), "AASd", auto_create=True)
            cfg.set("aasd", varname="debug", value=True)
            cfg.set("aasd", varname="verbose", value=True)
            self.assertTrue(cfg.save())
            self.assertTrue(cfg.load())

            obj = self.__build_config(config_file)
            obj._cfh = cfg

            self.assertTrue(obj.debug)
            self.assertTrue(obj.verbose)

    def test_10_should_log_plugin_config_warnings_during_load(self) -> None:
        """Emit semantic plugin-config warnings during `load()`."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "aasd.conf"
            plugins_dir = Path(tmp_dir) / "plugins"
            plugins_dir.mkdir()
            self.__prepare_existing_file(config_file, with_plugins_dir=True)
            self.__write_validation_test_plugin(plugins_dir / "sample_plugin")

            cfg = ConfigTool(str(config_file), "AASd", auto_create=True)
            cfg.set("sample_plugin", varname="message_channel", value=["mail", "2:bad"])
            cfg.set("sample_plugin", varname="at_channel", value=["1:0;*/6;*;*;*"])
            self.assertTrue(cfg.save())

            obj = self.__build_config(config_file)
            obj.plugins_dir = str(plugins_dir)
            logs = _CollectingLogger()

            with patch.object(AppConfig, "logs", new_callable=PropertyMock) as logs_mock:
                logs_mock.return_value = logs
                self.assertTrue(obj.load())

            self.assertGreaterEqual(len(logs.warnings), 3)
            self.assertTrue(
                any(
                    "message_channel" in item and "non-integer" in item
                    for item in logs.warnings
                )
            )
            self.assertTrue(
                any(
                    "message_channel" in item and "invalid interval" in item
                    for item in logs.warnings
                )
            )
            self.assertTrue(
                any("at_channel" in item and "full wildcard" in item for item in logs.warnings)
            )


# #[EOF]#######################################################################
