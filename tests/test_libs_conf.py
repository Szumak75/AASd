# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Provide regression coverage for selected AppConfig update paths.
"""

import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.logstool import LoggerQueue

from libs.conf import AppConfig


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


# #[EOF]#######################################################################
