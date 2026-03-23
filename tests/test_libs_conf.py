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
        cfg.set("aasd", varname="modules", value=[])
        if with_plugins_dir:
            cfg.set("aasd", varname="plugins_dir", value="./plugins")
        self.assertTrue(cfg.save())

    # #[PUBLIC METHODS]################################################################
    def test_01_should_update_existing_plugins_dir_only_in_update_mode(self) -> None:
        """Persist `plugins_dir` for an existing file only when update mode is enabled."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "aasd.conf"
            self.__prepare_existing_file(config_file, with_plugins_dir=True)

            obj = self.__build_config(config_file)
            obj.plugins_dir = "/tmp/plugins-new"

            with patch.object(AppConfig, "import_name_list", return_value=[]):
                self.assertTrue(obj.load())

            check_cfg = ConfigTool(str(config_file), "AASd")
            self.assertTrue(check_cfg.load())
            self.assertEqual(check_cfg.get("aasd", "plugins_dir"), "./plugins")

            obj = self.__build_config(config_file)
            obj.plugins_dir = "/tmp/plugins-new"
            obj.update = True

            with patch.object(AppConfig, "import_name_list", return_value=[]):
                self.assertTrue(obj.load())

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

            with patch.object(AppConfig, "import_name_list", return_value=[]):
                self.assertTrue(obj.load())

            check_cfg = ConfigTool(str(config_file), "AASd")
            self.assertTrue(check_cfg.load())
            self.assertEqual(check_cfg.get("aasd", "plugins_dir"), "./plugins")


# #[EOF]#######################################################################
