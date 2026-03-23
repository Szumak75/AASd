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
        sys.modules.pop("libs.templates.schema", None)

    def test_01_lazy_export_loads_modules_on_demand(self) -> None:
        """Test nr 01."""
        sys.modules.pop("libs.templates", None)
        sys.modules.pop("libs.templates.schema", None)
        templates_module = importlib.import_module("libs.templates")

        self.assertNotIn("libs.templates.schema", sys.modules)

        lazy_field_export = getattr(templates_module, "PluginConfigField")
        lazy_schema_export = getattr(templates_module, "PluginConfigSchema")

        self.assertIn("libs.templates.schema", sys.modules)
        direct_field_export = getattr(
            importlib.import_module("libs.templates.schema"), "PluginConfigField"
        )
        direct_schema_export = getattr(
            importlib.import_module("libs.templates.schema"), "PluginConfigSchema"
        )
        self.assertIs(lazy_field_export, direct_field_export)
        self.assertIs(lazy_schema_export, direct_schema_export)

    def test_02_package_dir_and_all_expose_lazy_symbols(self) -> None:
        """Test nr 02."""
        templates_module = importlib.import_module("libs.templates")

        self.assertIn("PluginConfigField", templates_module.__all__)
        self.assertIn("PluginConfigSchema", templates_module.__all__)
        self.assertIn("PluginConfigSchemaRenderer", templates_module.__all__)
        self.assertIn("PluginConfigField", dir(templates_module))
        self.assertIn("PluginConfigSchema", dir(templates_module))
        self.assertIn("PluginConfigSchemaRenderer", dir(templates_module))
        with self.assertRaises(AttributeError):
            getattr(templates_module, "NotExported")


# #[EOF]#######################################################################
