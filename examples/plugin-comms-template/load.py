# -*- coding: UTF-8 -*-
"""
Communication template plugin entry point.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-24

Purpose: Provide a starter `load.py` for standalone AASd communication plugins.
"""

from libs.plugins import PluginCommonKeys, PluginKind, PluginSpec
from libs.templates import PluginConfigField, PluginConfigSchema

from plugin.config import Keys
from plugin.runtime import CommsTemplateRuntime


def get_plugin_spec() -> PluginSpec:
    """Return the plugin spec for the communication template plugin.

    ### Returns:
    PluginSpec - Plugin manifest.
    """
    schema = PluginConfigSchema(
        title="Communication template plugin.",
        description=(
            "Starter communication plugin template showing the recommended "
            "AASd plugin layout."
        ),
        fields=[
            PluginConfigField(
                name=PluginCommonKeys.CHANNEL,
                field_type=int,
                default=1,
                required=True,
                description="Dispatcher channel consumed by the plugin.",
            ),
            PluginConfigField(
                name=Keys.STDOUT_PREFIX,
                field_type=str,
                default="[plugin-comms-template]",
                required=True,
                description="Prefix added to stdout output.",
                example="[plugin-comms-template]",
            ),
        ],
    )
    return PluginSpec(
        api_version=1,
        config_schema=schema,
        plugin_id="template.communication",
        plugin_kind=PluginKind.COMMUNICATION,
        plugin_name="plugin_comms_template",
        runtime_factory=CommsTemplateRuntime,
        description="Starter AASd communication plugin template.",
    )


# #[EOF]#######################################################################
