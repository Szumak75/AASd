# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Provide regression coverage for plugin startup ordering in the daemon.
"""

import unittest

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import PropertyMock, patch

from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.logstool import LoggerClient, LoggerQueue

from libs import AppConfig, AppName, Keys
from libs.plugins import (
    PluginConfigParser,
    PluginDefinition,
    PluginHealth,
    PluginHealthSnapshot,
    PluginKind,
    PluginSpec,
    PluginState,
    PluginStateSnapshot,
)
from libs.templates import PluginConfigField, PluginConfigSchema
from server.daemon import AASd


class _FakeRuntime(object):
    """Track plugin startup order without starting real threads."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self, bucket: list[str], name: str) -> None:
        """Initialize the fake runtime tracker.

        ### Arguments:
        * bucket: list[str] - Shared startup order collector.
        * name: str - Plugin instance name.
        """
        self._bucket = bucket
        self._name = name
        self._initialized = False
        self._stopped = False

    # #[PUBLIC METHODS]################################################################
    def health(self) -> PluginHealthSnapshot:
        """Return a healthy state for the fake runtime.

        ### Returns:
        PluginHealthSnapshot - Fake healthy snapshot.
        """
        return PluginHealthSnapshot(health=PluginHealth.HEALTHY)

    def initialize(self) -> None:
        """Record runtime initialization."""
        self._initialized = True

    def start(self) -> None:
        """Record the startup order."""
        if not self._initialized:
            raise RuntimeError("Runtime was not initialized.")
        self._bucket.append(self._name)
        self._stopped = False

    def state(self) -> PluginStateSnapshot:
        """Return the current fake lifecycle state.

        ### Returns:
        PluginStateSnapshot - Fake lifecycle state snapshot.
        """
        state = PluginState.STOPPED if self._stopped else PluginState.RUNNING
        return PluginStateSnapshot(state=state)

    def stop(self, timeout: float | None = None) -> None:
        """Mark the runtime as stopped."""
        self._stopped = True


class TestServerDaemonPlugins(unittest.TestCase):
    """Cover daemon startup ordering for communication and worker plugins."""

    def test_01_should_start_communication_plugins_before_workers(self) -> None:
        """Start communication plugins before worker plugins."""
        cfg = ConfigTool(str(Path("/tmp/aasd-daemon-test.conf")), "AASd", auto_create=True)
        cfg.set("aasd", varname="debug", value=True)
        cfg.set("aasd", varname="verbose", value=False)
        order: list[str] = []
        schema = PluginConfigSchema(
            title="Test plugin.",
            fields=[
                PluginConfigField(
                    name="channel",
                    field_type=int,
                    default=1,
                    required=True,
                    description="Test channel.",
                )
            ],
        )

        def _runtime_factory(name: str):
            def _factory(_context):
                return _FakeRuntime(order, name)

            return _factory

        comm_plugin = PluginDefinition(
            instance_name="comm_plugin",
            plugin_path=Path("/tmp/comm_plugin"),
            spec=PluginSpec(
                api_version=1,
                config_schema=schema,
                plugin_id="test.comm",
                plugin_kind=PluginKind.COMMUNICATION,
                plugin_name="comm_plugin",
                runtime_factory=_runtime_factory("comm_plugin"),
            ),
        )
        worker_plugin = PluginDefinition(
            instance_name="worker_plugin",
            plugin_path=Path("/tmp/worker_plugin"),
            spec=PluginSpec(
                api_version=1,
                config_schema=schema,
                plugin_id="test.worker",
                plugin_kind=PluginKind.WORKER,
                plugin_name="worker_plugin",
                runtime_factory=_runtime_factory("worker_plugin"),
            ),
        )

        obj = AASd.__new__(AASd)
        app_conf = AppConfig(qlog=LoggerQueue(), app_name="AASd")
        app_conf.config_file = str(Path("/tmp/aasd-daemon-test.conf"))
        app_conf.debug = True
        app_conf.verbose = False
        app_conf._cfh = cfg

        obj.logs = LoggerClient(queue=LoggerQueue(), name="AASd")
        obj._set_data(key=Keys.CONF, value=app_conf)
        obj.application = AppName(app_name="AASd", app_version="2.1.0-DEV")

        with patch.object(
            AppConfig,
            "get_plugins",
            new_callable=PropertyMock,
            return_value=[worker_plugin, comm_plugin],
        ), patch.object(
            PluginConfigParser,
            "parse",
            return_value={"channel": 1},
        ), patch.object(AASd, "_AASd__build_plugin_context", return_value=None):
            plugins, dispatcher = obj._AASd__start_subsystem()

        self.assertEqual(order, ["comm_plugin", "worker_plugin"])
        obj._AASd__stop_subsystem(plugins, dispatcher)


# #[EOF]#######################################################################
