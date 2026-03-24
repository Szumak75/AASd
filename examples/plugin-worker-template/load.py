# -*- coding: UTF-8 -*-
"""
Worker template plugin entry point.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-24

Purpose: Provide a starter `load.py` for standalone AASd worker plugins.
"""

from libs.plugins import PluginCommonKeys, PluginKind, PluginSpec
from libs.templates import PluginConfigField, PluginConfigSchema

from .plugin.config import Keys
from .plugin.runtime import WorkerTemplateRuntime


def get_plugin_spec() -> PluginSpec:
    """Return the plugin spec for the worker template plugin.

    ### Returns:
    PluginSpec - Plugin manifest.
    """
    schema = PluginConfigSchema(
        title="Worker template plugin.",
        description=(
            "Starter worker plugin template showing the recommended "
            "AASd plugin layout."
        ),
        fields=[
            PluginConfigField(
                name=PluginCommonKeys.MESSAGE_CHANNEL,
                field_type=list,
                default=[1],
                required=True,
                description=(
                    "Interval-based notification targets, for example " "`[1, '2:6h']`."
                ),
            ),
            PluginConfigField(
                name=PluginCommonKeys.AT_CHANNEL,
                field_type=list,
                default=[],
                required=False,
                description=(
                    "Cron-like notification targets, for example "
                    "`['3:0;8|20;*;*;*']`."
                ),
            ),
            PluginConfigField(
                name=Keys.MESSAGE_TEXT,
                field_type=str,
                default="Hello from worker template plugin.",
                required=True,
                description="Message emitted during startup by the worker plugin.",
            ),
        ],
    )
    return PluginSpec(
        api_version=1,
        config_schema=schema,
        plugin_id="template.worker",
        plugin_kind=PluginKind.WORKER,
        plugin_name="plugin_worker_template",
        runtime_factory=WorkerTemplateRuntime,
        description="Starter AASd worker plugin template.",
    )


# #[EOF]#######################################################################
