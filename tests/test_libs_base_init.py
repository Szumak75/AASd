# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 2026-03-22

  Purpose: Regression tests for lazy exports exposed by `libs.base`.
"""

import importlib
import sys
import unittest


class TestLibsBaseInit(unittest.TestCase):
    """Test lazy exports from the `libs.base` package."""

    def tearDown(self) -> None:
        """Reset imported package modules after each test."""
        sys.modules.pop("libs.base", None)
        sys.modules.pop("libs.base.classes", None)

    def test_01_lazy_export_loads_classes_on_demand(self) -> None:
        """Test nr 01."""
        sys.modules.pop("libs.base", None)
        sys.modules.pop("libs.base.classes", None)
        base_module = importlib.import_module("libs.base")

        self.assertNotIn("libs.base.classes", sys.modules)

        lazy_export = getattr(base_module, "PluginRuntimeMixin")

        self.assertIn("libs.base.classes", sys.modules)
        direct_export = getattr(
            importlib.import_module("libs.base.classes"), "PluginRuntimeMixin"
        )
        self.assertIs(lazy_export, direct_export)

    def test_02_package_dir_and_all_expose_lazy_symbols(self) -> None:
        """Test nr 02."""
        base_module = importlib.import_module("libs.base")

        self.assertIn("PluginRuntimeMixin", base_module.__all__)
        self.assertIn("PluginRuntimeMixin", dir(base_module))
        with self.assertRaises(AttributeError):
            getattr(base_module, "NotExported")


# #[EOF]#######################################################################
