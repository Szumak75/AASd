# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 2026-03-22

  Purpose: Regression tests for lazy exports exposed by `libs.interfaces`.
"""

import importlib
import sys
import unittest


class TestLibsInterfacesInit(unittest.TestCase):
    """Test lazy exports from the `libs.interfaces` package."""

    def tearDown(self) -> None:
        """Reset imported package modules after each test."""
        sys.modules.pop("libs.interfaces", None)
        sys.modules.pop("libs.interfaces.modules", None)

    def test_01_lazy_export_loads_modules_on_demand(self) -> None:
        """Test nr 01."""
        sys.modules.pop("libs.interfaces", None)
        sys.modules.pop("libs.interfaces.modules", None)
        interfaces_module = importlib.import_module("libs.interfaces")

        self.assertNotIn("libs.interfaces.modules", sys.modules)

        lazy_export = getattr(interfaces_module, "IRunModule")

        self.assertIn("libs.interfaces.modules", sys.modules)
        direct_export = getattr(
            importlib.import_module("libs.interfaces.modules"), "IRunModule"
        )
        self.assertIs(lazy_export, direct_export)

    def test_02_package_dir_and_all_expose_lazy_symbols(self) -> None:
        """Test nr 02."""
        interfaces_module = importlib.import_module("libs.interfaces")

        self.assertIn("IRunModule", interfaces_module.__all__)
        self.assertIn("IRunModule", dir(interfaces_module))
        with self.assertRaises(AttributeError):
            getattr(interfaces_module, "NotExported")


# #[EOF]#######################################################################
