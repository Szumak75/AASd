# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 2026-03-22

  Purpose: Regression tests for lazy exports exposed by `libs.templates`.
"""

import importlib
import sys
import unittest


class TestLibsTemplatesInit(unittest.TestCase):
    """Test lazy exports from the `libs.templates` package."""

    def tearDown(self) -> None:
        """Reset imported package modules after each test."""
        sys.modules.pop("libs.templates", None)
        sys.modules.pop("libs.templates.modules", None)

    def test_01_lazy_export_loads_modules_on_demand(self) -> None:
        """Test nr 01."""
        sys.modules.pop("libs.templates", None)
        sys.modules.pop("libs.templates.modules", None)
        templates_module = importlib.import_module("libs.templates")

        self.assertNotIn("libs.templates.modules", sys.modules)

        lazy_export = getattr(templates_module, "TemplateConfigItem")

        self.assertIn("libs.templates.modules", sys.modules)
        direct_export = getattr(
            importlib.import_module("libs.templates.modules"), "TemplateConfigItem"
        )
        self.assertIs(lazy_export, direct_export)

    def test_02_package_dir_and_all_expose_lazy_symbols(self) -> None:
        """Test nr 02."""
        templates_module = importlib.import_module("libs.templates")

        self.assertIn("TemplateConfigItem", templates_module.__all__)
        self.assertIn("TemplateConfigItem", dir(templates_module))
        with self.assertRaises(AttributeError):
            getattr(templates_module, "NotExported")


# #[EOF]#######################################################################
