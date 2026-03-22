# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 2026-03-22

  Purpose: Regression tests for lazy exports exposed by `libs.tools`.
"""

import importlib
import sys
import unittest


class TestLibsToolsInit(unittest.TestCase):
    """Test lazy exports from the `libs.tools` package."""

    def tearDown(self) -> None:
        """Reset imported package modules after each test."""
        sys.modules.pop("libs.tools", None)
        sys.modules.pop("libs.tools.datetool", None)
        sys.modules.pop("libs.tools.icmp", None)

    def test_01_lazy_export_loads_datetool_on_demand(self) -> None:
        """Test nr 01."""
        sys.modules.pop("libs.tools", None)
        sys.modules.pop("libs.tools.datetool", None)
        tools_module = importlib.import_module("libs.tools")

        self.assertNotIn("libs.tools.datetool", sys.modules)

        lazy_export = getattr(tools_module, "MDateTime")

        self.assertIn("libs.tools.datetool", sys.modules)
        direct_export = getattr(
            importlib.import_module("libs.tools.datetool"), "MDateTime"
        )
        self.assertIs(lazy_export, direct_export)

    def test_02_package_dir_and_all_expose_lazy_symbols(self) -> None:
        """Test nr 02."""
        tools_module = importlib.import_module("libs.tools")

        self.assertIn("MDateTime", tools_module.__all__)
        self.assertIn("Pinger", tools_module.__all__)
        self.assertIn("MDateTime", dir(tools_module))
        with self.assertRaises(AttributeError):
            getattr(tools_module, "NotExported")


# #[EOF]#######################################################################
