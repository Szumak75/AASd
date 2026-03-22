# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 2026-03-22

  Purpose: Regression tests for lazy exports exposed by `libs`.
"""

import importlib
import sys
import unittest


class TestLibsInit(unittest.TestCase):
    """Test lazy exports from the `libs` package."""

    def tearDown(self) -> None:
        """Reset imported package modules after each test."""
        sys.modules.pop("libs", None)
        sys.modules.pop("libs.app", None)
        sys.modules.pop("libs.conf", None)
        sys.modules.pop("libs.keys", None)

    def test_01_lazy_export_loads_app_module_on_demand(self) -> None:
        """Test nr 01."""
        sys.modules.pop("libs", None)
        sys.modules.pop("libs.app", None)
        libs_module = importlib.import_module("libs")

        self.assertNotIn("libs.app", sys.modules)

        lazy_export = getattr(libs_module, "AppName")

        self.assertIn("libs.app", sys.modules)
        direct_export = getattr(importlib.import_module("libs.app"), "AppName")
        self.assertIs(lazy_export, direct_export)

    def test_02_package_dir_and_all_expose_lazy_symbols(self) -> None:
        """Test nr 02."""
        libs_module = importlib.import_module("libs")

        self.assertIn("AppName", libs_module.__all__)
        self.assertIn("AppConfig", libs_module.__all__)
        self.assertIn("Keys", libs_module.__all__)
        self.assertIn("AppName", dir(libs_module))
        with self.assertRaises(AttributeError):
            getattr(libs_module, "NotExported")


# #[EOF]#######################################################################
