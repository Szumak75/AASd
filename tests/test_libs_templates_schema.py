# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 2026-03-23

  Purpose: Regression tests for plugin configuration schema helpers.
"""

import unittest

from libs.templates import (
    PluginConfigField,
    PluginConfigSchema,
    PluginConfigSchemaRenderer,
    TemplateConfigItem,
)


class TestLibsTemplatesSchema(unittest.TestCase):
    """Test plugin configuration schema helper classes."""

    def test_01_field_properties_store_declared_metadata(self) -> None:
        """Test nr 01."""
        field = PluginConfigField(
            name="message_channel",
            field_type=list[str],
            default=["1"],
            required=True,
            description="Dispatcher output channels.",
            example=["1", "2"],
            group="routing",
            restart_required=True,
        )

        self.assertEqual(field.name, "message_channel")
        self.assertEqual(field.default, ["1"])
        self.assertTrue(field.required)
        self.assertEqual(field.description, "Dispatcher output channels.")
        self.assertEqual(field.group, "routing")
        self.assertTrue(field.restart_required)
        self.assertEqual(field.type_name, "list")

    def test_02_schema_renderer_creates_template_rows(self) -> None:
        """Test nr 02."""
        field = PluginConfigField(
            name="stdout_prefix",
            field_type=str,
            default="[example2]",
            required=False,
            description="Prefix added to stdout output.",
            example="[worker]",
        )
        schema = PluginConfigSchema(
            title="Example communication plugin.",
            fields=[field],
            description="Consumes dispatcher messages and prints them.",
        )

        out = PluginConfigSchemaRenderer.render(schema)

        self.assertEqual(len(out), 5)
        self.assertTrue(all(isinstance(item, TemplateConfigItem) for item in out))
        self.assertEqual(out[0].desc, "Example communication plugin.")
        self.assertEqual(out[1].desc, "Consumes dispatcher messages and prints them.")
        self.assertIn("stdout_prefix [str]", out[2].desc or "")
        self.assertEqual(out[3].desc, "example: [worker]")
        self.assertEqual(out[4].varname, "stdout_prefix")
        self.assertEqual(out[4].value, "[example2]")


# #[EOF]#######################################################################
