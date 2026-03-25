# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Provide regression coverage for plugin startup ordering in the daemon.
"""

import unittest

from pathlib import Path
from typing import List, Optional
from unittest.mock import PropertyMock, patch

from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.logstool import LoggerClient, LoggerQueue

from libs import AppConfig, AppName, Keys
from libs.plugins import (
    PluginConfigParser,
    PluginDefinition,
    PluginHealth,
    PluginHealthPolicy,
    PluginHealthSnapshot,
    PluginKind,
    PluginRegistryService,
    PluginRestartPolicy,
    PluginServiceReport,
    PluginSpec,
    PluginState,
    PluginStateSnapshot,
)
from libs.templates import PluginConfigField, PluginConfigSchema
from server.daemon import AASd


class _FakeRuntime(object):
    """Track plugin startup order without starting real threads."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self, bucket: List[str], name: str) -> None:
        """Initialize the fake runtime tracker.

        ### Arguments:
        * bucket: List[str] - Shared startup order collector.
        * name: str - Plugin instance name.
        """
        self._bucket = bucket
        self._health = PluginHealth.HEALTHY
        self._name = name
        self._initialized = False
        self._state = PluginState.CREATED
        self._stopped = False
        self.stop_calls = 0

    # #[PUBLIC METHODS]################################################################
    def health(self) -> PluginHealthSnapshot:
        """Return a healthy state for the fake runtime.

        ### Returns:
        PluginHealthSnapshot - Fake healthy snapshot.
        """
        return PluginHealthSnapshot(health=self._health)

    def initialize(self) -> None:
        """Record runtime initialization."""
        self._initialized = True
        self._state = PluginState.INITIALIZED

    def start(self) -> None:
        """Record the startup order."""
        if not self._initialized:
            raise RuntimeError("Runtime was not initialized.")
        self._bucket.append(self._name)
        self._state = PluginState.RUNNING
        self._stopped = False

    def state(self) -> PluginStateSnapshot:
        """Return the current fake lifecycle state.

        ### Returns:
        PluginStateSnapshot - Fake lifecycle state snapshot.
        """
        return PluginStateSnapshot(state=self._state)

    def stop(self, timeout: Optional[float] = None) -> None:
        """Mark the runtime as stopped."""
        del timeout
        self.stop_calls += 1
        self._state = PluginState.STOPPED
        self._stopped = True


class _BrokenInitializeRuntime(_FakeRuntime):
    """Raise during initialization to simulate startup isolation."""

    # #[PUBLIC METHODS]#############################################################
    def initialize(self) -> None:
        """Raise an initialization error."""
        self._state = PluginState.FAILED
        self._health = PluginHealth.UNHEALTHY
        raise RuntimeError("broken initialize")


class _BrokenStartRuntime(_FakeRuntime):
    """Raise during startup to simulate partial initialization."""

    # #[PUBLIC METHODS]#############################################################
    def start(self) -> None:
        """Raise a startup error after successful initialization."""
        if not self._initialized:
            raise RuntimeError("Runtime was not initialized.")
        self._state = PluginState.FAILED
        self._health = PluginHealth.UNHEALTHY
        raise RuntimeError("broken start")


class _CollectingLogger(object):
    """Collect supervision summary messages without real logger engines."""

    # #[CONSTRUCTOR]################################################################
    def __init__(self) -> None:
        """Initialize the collecting logger."""
        self.infos: List[str] = []
        self.warnings: List[str] = []
        self.logs_queue = LoggerQueue()

    # #[PUBLIC PROPERTIES]##########################################################
    @property
    def message_info(self) -> str:
        """Return the last info message.

        ### Returns:
        str - Last stored info message or an empty string.
        """
        if not self.infos:
            return ""
        return self.infos[-1]

    @message_info.setter
    def message_info(self, value: str) -> None:
        """Store an info message.

        ### Arguments:
        * value: str - Info message text.
        """
        self.infos.append(value)

    @property
    def message_warning(self) -> str:
        """Return the last warning message.

        ### Returns:
        str - Last stored warning message or an empty string.
        """
        if not self.warnings:
            return ""
        return self.warnings[-1]

    @message_warning.setter
    def message_warning(self, value: str) -> None:
        """Store a warning message.

        ### Arguments:
        * value: str - Warning message text.
        """
        self.warnings.append(value)

    @property
    def message_error(self) -> str:
        """Return the last warning as the error placeholder.

        ### Returns:
        str - Last stored warning message or an empty string.
        """
        return self.message_warning

    @message_error.setter
    def message_error(self, value: str) -> None:
        """Store an error message in the warning bucket.

        ### Arguments:
        * value: str - Error message text.
        """
        self.warnings.append(value)

    @property
    def message_debug(self) -> str:
        """Return the last info message as the debug placeholder.

        ### Returns:
        str - Last stored info message or an empty string.
        """
        return self.message_info

    @message_debug.setter
    def message_debug(self, value: str) -> None:
        """Store a debug message in the info bucket.

        ### Arguments:
        * value: str - Debug message text.
        """
        self.infos.append(value)


class TestServerDaemonPlugins(unittest.TestCase):
    """Cover daemon startup ordering for communication and worker plugins."""

    def test_01_registry_should_start_communication_plugins_before_workers(self) -> None:
        """Start communication plugins before worker plugins."""
        cfg = ConfigTool(str(Path("/tmp/aasd-daemon-test.conf")), "AASd", auto_create=True)
        cfg.set("aasd", varname="debug", value=True)
        cfg.set("aasd", varname="verbose", value=False)
        order: List[str] = []
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

        app_conf = AppConfig(qlog=LoggerQueue(), app_name="AASd")
        app_conf.config_file = str(Path("/tmp/aasd-daemon-test.conf"))
        app_conf.debug = True
        app_conf.verbose = False
        app_conf._cfh = cfg

        app_meta = AppName(app_name="AASd", app_version="2.1.0-DEV")
        logs = LoggerClient(queue=LoggerQueue(), name="AASd")

        with patch.object(
            AppConfig,
            "get_plugins",
            new_callable=PropertyMock,
            return_value=[worker_plugin, comm_plugin],
        ), patch.object(
            PluginConfigParser,
            "parse",
            return_value={"channel": 1},
        ):
            report = PluginRegistryService.start(
                conf=app_conf,
                app_meta=app_meta,
                logs=logs,
            )

        self.assertEqual(order, ["comm_plugin", "worker_plugin"])
        self.assertEqual(report.started, ["comm_plugin", "worker_plugin"])
        PluginRegistryService.stop(report=report, logs=logs)

    def test_02_daemon_should_delegate_lifecycle_to_registry_service(self) -> None:
        """Delegate subsystem start and stop to the plugin registry service."""
        obj = AASd.__new__(AASd)
        report = PluginServiceReport()
        logs = LoggerClient(queue=LoggerQueue(), name="AASd")
        obj.logs = logs
        obj.application = AppName(app_name="AASd", app_version="2.1.0-DEV")

        app_conf = AppConfig(qlog=LoggerQueue(), app_name="AASd")
        obj._set_data(key=Keys.CONF, value=app_conf)

        with patch.object(
            PluginRegistryService,
            "start",
            return_value=report,
        ) as start_mock, patch.object(
            PluginRegistryService,
            "stop",
            return_value=None,
        ) as stop_mock:
            start_report = obj._AASd__start_subsystem()
            obj._AASd__stop_subsystem(report)

        self.assertIs(start_report, report)
        start_mock.assert_called_once_with(
            conf=app_conf,
            app_meta=obj.application,
            logs=logs,
        )
        stop_mock.assert_called_once_with(report=report, logs=logs)

    def test_03_registry_should_report_failed_initialize_without_blocking_others(
        self,
    ) -> None:
        """Keep starting unrelated plugins when one plugin fails initialize."""
        cfg = ConfigTool(str(Path("/tmp/aasd-daemon-test.conf")), "AASd", auto_create=True)
        cfg.set("aasd", varname="debug", value=True)
        cfg.set("aasd", varname="verbose", value=False)
        order: List[str] = []
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

        healthy_plugin = PluginDefinition(
            instance_name="healthy_worker",
            plugin_path=Path("/tmp/healthy_worker"),
            spec=PluginSpec(
                api_version=1,
                config_schema=schema,
                plugin_id="test.healthy",
                plugin_kind=PluginKind.WORKER,
                plugin_name="healthy_worker",
                runtime_factory=lambda _context: _FakeRuntime(order, "healthy_worker"),
            ),
        )
        broken_plugin = PluginDefinition(
            instance_name="broken_worker",
            plugin_path=Path("/tmp/broken_worker"),
            spec=PluginSpec(
                api_version=1,
                config_schema=schema,
                plugin_id="test.broken",
                plugin_kind=PluginKind.WORKER,
                plugin_name="broken_worker",
                runtime_factory=lambda _context: _BrokenInitializeRuntime(
                    order, "broken_worker"
                ),
            ),
        )

        app_conf = AppConfig(qlog=LoggerQueue(), app_name="AASd")
        app_conf.config_file = str(Path("/tmp/aasd-daemon-test.conf"))
        app_conf.debug = True
        app_conf.verbose = False
        app_conf._cfh = cfg
        logs = _CollectingLogger()

        with patch.object(
            AppConfig,
            "get_plugins",
            new_callable=PropertyMock,
            return_value=[broken_plugin, healthy_plugin],
        ), patch.object(
            PluginConfigParser,
            "parse",
            return_value={"channel": 1},
        ):
            report = PluginRegistryService.start(
                conf=app_conf,
                app_meta=AppName(app_name="AASd", app_version="2.1.0-DEV"),
                logs=logs,  # type: ignore[arg-type]
            )

        self.assertEqual(report.started, ["healthy_worker"])
        self.assertEqual(order, ["healthy_worker"])
        self.assertEqual(len(report.failed), 1)
        self.assertEqual(report.failed[0].instance_name, "broken_worker")
        self.assertEqual(report.failed[0].stage, "initialize")
        self.assertEqual(report.skipped, [])
        self.assertTrue(
            any("plugin supervision summary" in message for message in logs.infos)
        )
        PluginRegistryService.stop(report=report, logs=logs)  # type: ignore[arg-type]

    def test_04_registry_should_mark_plugins_skipped_on_bootstrap_failure(self) -> None:
        """Mark discovered plugins as skipped when startup aborts before attempts."""
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
        skipped_plugin = PluginDefinition(
            instance_name="skipped_worker",
            plugin_path=Path("/tmp/skipped_worker"),
            spec=PluginSpec(
                api_version=1,
                config_schema=schema,
                plugin_id="test.skipped",
                plugin_kind=PluginKind.WORKER,
                plugin_name="skipped_worker",
                runtime_factory=lambda _context: _FakeRuntime([], "skipped_worker"),
            ),
        )
        app_conf = AppConfig(qlog=LoggerQueue(), app_name="AASd")
        app_conf.config_file = str(Path("/tmp/aasd-daemon-test.conf"))
        app_conf.debug = False
        app_conf.verbose = False
        app_conf._cfh = None
        logs = _CollectingLogger()

        with patch.object(
            AppConfig,
            "get_plugins",
            new_callable=PropertyMock,
            return_value=[skipped_plugin],
        ):
            report = PluginRegistryService.start(
                conf=app_conf,
                app_meta=AppName(app_name="AASd", app_version="2.1.0-DEV"),
                logs=logs,  # type: ignore[arg-type]
            )

        self.assertEqual(len(report.failed), 1)
        self.assertEqual(report.failed[0].stage, "bootstrap")
        self.assertEqual(len(report.skipped), 1)
        self.assertEqual(report.skipped[0].instance_name, "skipped_worker")
        self.assertEqual(report.skipped[0].stage, "bootstrap")
        self.assertTrue(
            any("skipped plugin instances" in message for message in logs.warnings)
        )
        PluginRegistryService.stop(report=report, logs=logs)  # type: ignore[arg-type]

    def test_05_registry_should_expose_default_supervision_policies(self) -> None:
        """Expose explicit defaults for restart and health supervision."""
        report = PluginServiceReport(
            health_policy=PluginHealthPolicy.TRANSITIONS_ONLY,
            restart_policy=PluginRestartPolicy.NONE,
        )

        self.assertEqual(report.health_policy, PluginHealthPolicy.TRANSITIONS_ONLY)
        self.assertEqual(report.restart_policy, PluginRestartPolicy.NONE)

    def test_06_stop_should_handle_initialized_runtime_that_never_started(self) -> None:
        """Stop initialized runtimes even when startup never completed."""
        runtime = _FakeRuntime([], "initialized_only")
        runtime.initialize()
        report = PluginServiceReport(managed_runtimes=[runtime])
        logs = _CollectingLogger()

        PluginRegistryService.stop(report=report, logs=logs)  # type: ignore[arg-type]

        self.assertEqual(runtime.stop_calls, 1)
        self.assertEqual(runtime.state().state, PluginState.STOPPED)

    def test_07_registry_should_keep_managed_runtime_after_start_failure(self) -> None:
        """Retain initialized runtimes for shutdown after a start failure."""
        cfg = ConfigTool(str(Path("/tmp/aasd-daemon-test.conf")), "AASd", auto_create=True)
        cfg.set("aasd", varname="debug", value=False)
        cfg.set("aasd", varname="verbose", value=False)
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
        runtime = _BrokenStartRuntime([], "broken_start")
        broken_plugin = PluginDefinition(
            instance_name="broken_start",
            plugin_path=Path("/tmp/broken_start"),
            spec=PluginSpec(
                api_version=1,
                config_schema=schema,
                plugin_id="test.broken_start",
                plugin_kind=PluginKind.WORKER,
                plugin_name="broken_start",
                runtime_factory=lambda _context: runtime,
            ),
        )
        app_conf = AppConfig(qlog=LoggerQueue(), app_name="AASd")
        app_conf.config_file = str(Path("/tmp/aasd-daemon-test.conf"))
        app_conf.debug = False
        app_conf.verbose = False
        app_conf._cfh = cfg
        logs = _CollectingLogger()

        with patch.object(
            AppConfig,
            "get_plugins",
            new_callable=PropertyMock,
            return_value=[broken_plugin],
        ), patch.object(
            PluginConfigParser,
            "parse",
            return_value={"channel": 1},
        ):
            report = PluginRegistryService.start(
                conf=app_conf,
                app_meta=AppName(app_name="AASd", app_version="2.1.0-DEV"),
                logs=logs,  # type: ignore[arg-type]
            )

        self.assertEqual(report.started, [])
        self.assertEqual(len(report.failed), 1)
        self.assertEqual(report.failed[0].stage, "start")
        self.assertEqual(len(report.managed_runtimes), 1)
        self.assertGreaterEqual(runtime.stop_calls, 1)

        PluginRegistryService.stop(report=report, logs=logs)  # type: ignore[arg-type]
        self.assertGreaterEqual(runtime.stop_calls, 2)


# #[EOF]#######################################################################
