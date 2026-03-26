# -*- coding: UTF-8 -*-
"""
Plugin registry and supervision service.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Provide discovery, initialization, startup, and shutdown control for plugins.
"""

import time

from dataclasses import dataclass, field
from inspect import currentframe
from queue import Queue
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.basetool import BClasses
from jsktoolbox.logstool import LoggerClient
from jsktoolbox.raisetool import Raise

from libs.app import AppName
from libs.com.message import ThDispatcher
from libs.plugins.config import PluginConfigParser
from libs.plugins.loader import PluginDefinition
from libs.plugins.runtime import (
    DispatcherAdapter,
    PluginContext,
    PluginKind,
    PluginRuntime,
    PluginState,
)

if TYPE_CHECKING:
    from libs.conf import AppConfig


@dataclass(slots=True)
class PluginFailure:
    """Describe one plugin failure recorded by the supervision service."""

    error: str
    instance_name: str
    stage: str


@dataclass(slots=True)
class PluginSkip:
    """Describe one plugin skipped by the supervision service."""

    instance_name: str
    reason: str
    stage: str


@dataclass(slots=True)
class PluginServiceReport:
    """Store the result of one plugin supervision start cycle."""

    dispatch: Optional[ThDispatcher] = None
    failed: List[PluginFailure] = field(default_factory=list)
    health_policy: str = "transitions_only"
    initialized: List[str] = field(default_factory=list)
    managed_runtimes: List[PluginRuntime] = field(default_factory=list)
    restart_policy: str = "none"
    started: List[str] = field(default_factory=list)
    skipped: List[PluginSkip] = field(default_factory=list)


class PluginHealthPolicy(object, metaclass=ReadOnlyClass):
    """Expose supported supervision health polling policies."""

    # #[CONSTANTS]##############################################################
    TRANSITIONS_ONLY: str = "transitions_only"


class PluginRestartPolicy(object, metaclass=ReadOnlyClass):
    """Expose supported supervision restart policies."""

    # #[CONSTANTS]##############################################################
    NONE: str = "none"


class PluginRegistryService(BClasses):
    """Supervise plugin discovery, initialization, startup, and shutdown."""

    # #[PUBLIC METHODS]#############################################################
    @classmethod
    def start(
        cls,
        conf: "AppConfig",
        app_meta: AppName,
        logs: LoggerClient,
    ) -> PluginServiceReport:
        """Start the dispatcher and all discovered plugin instances.

        ### Arguments:
        * conf: AppConfig - Loaded application configuration service.
        * app_meta: AppName - Application identity metadata.
        * logs: LoggerClient - Daemon logger used for supervision messages.

        ### Returns:
        PluginServiceReport - Supervision result for this startup cycle.
        """
        report = PluginServiceReport(
            health_policy=PluginHealthPolicy.TRANSITIONS_ONLY,
            restart_policy=PluginRestartPolicy.NONE,
        )
        logs.message_info = "starting..."
        discovered_plugins: List[PluginDefinition] = list(conf.get_plugins)

        if logs.logs_queue is None:
            report.failed.append(
                PluginFailure(
                    error="logger queue is not initialized",
                    instance_name="__daemon__",
                    stage="bootstrap",
                )
            )
            cls.__mark_skipped(
                report=report,
                plugins=discovered_plugins,
                reason="logger queue is not initialized",
                stage="bootstrap",
            )
            cls.__log_summary(report=report, logs=logs)
            return report

        qcom: Queue = Queue()
        dispatch = ThDispatcher(
            qlog=logs.logs_queue,
            qcom=qcom,
            verbose=conf.verbose,
            debug=conf.debug,
        )
        dispatch.start()
        time.sleep(1.0)
        report.dispatch = dispatch
        dispatcher_adapter = DispatcherAdapter(qcom=qcom, dispatcher=dispatch)

        if conf.cf is None:
            report.failed.append(
                PluginFailure(
                    error="configuration handler is not initialized",
                    instance_name="__daemon__",
                    stage="bootstrap",
                )
            )
            cls.__mark_skipped(
                report=report,
                plugins=discovered_plugins,
                reason="configuration handler is not initialized",
                stage="bootstrap",
            )
            cls.__log_summary(report=report, logs=logs)
            return report

        comm_plugins: List[PluginDefinition] = []
        worker_plugins: List[PluginDefinition] = []
        for plugin in discovered_plugins:
            if plugin.spec.plugin_kind == PluginKind.COMMUNICATION:
                comm_plugins.append(plugin)
            else:
                worker_plugins.append(plugin)

        initialized_plugins: List[Tuple[PluginDefinition, PluginRuntime]] = []
        ordered_plugins: List[PluginDefinition] = comm_plugins + worker_plugins
        for plugin in ordered_plugins:
            try:
                parsed_config = PluginConfigParser.parse(
                    conf.cf, plugin.instance_name, plugin.spec.config_schema
                )
                runtime = plugin.spec.runtime_factory(
                    cls.__build_plugin_context(
                        app_meta=app_meta,
                        conf=conf,
                        config=parsed_config,
                        dispatcher=dispatcher_adapter,
                        logs=logs,
                        plugin=plugin,
                    )
                )
                runtime.initialize()
                report.managed_runtimes.append(runtime)
                initialized_plugins.append((plugin, runtime))
                report.initialized.append(plugin.instance_name)
                if conf.debug:
                    logs.message_debug = (
                        f"initialized plugin instance: '{plugin.instance_name}'"
                    )
            except Exception as ex:
                report.failed.append(
                    PluginFailure(
                        error=str(ex),
                        instance_name=plugin.instance_name,
                        stage="initialize",
                    )
                )
                logs.message_error = (
                    f"cannot initialize plugin instance "
                    f"'{plugin.instance_name}': {ex}"
                )

        for plugin, runtime in initialized_plugins:
            try:
                runtime.start()
                report.started.append(plugin.instance_name)
                if conf.debug:
                    logs.message_debug = (
                        f"started plugin instance: '{plugin.instance_name}'"
                    )
            except Exception as ex:
                report.failed.append(
                    PluginFailure(
                        error=str(ex),
                        instance_name=plugin.instance_name,
                        stage="start",
                    )
                )
                logs.message_error = (
                    f"cannot start plugin instance '{plugin.instance_name}': {ex}"
                )
                try:
                    runtime.stop(timeout=2.0)
                except Exception:
                    pass
        cls.__log_summary(report=report, logs=logs)
        return report

    @classmethod
    def stop(cls, report: PluginServiceReport, logs: LoggerClient) -> None:
        """Stop all started plugin runtimes and the dispatcher.

        ### Arguments:
        * report: PluginServiceReport - Supervision report holding active runtimes.
        * logs: LoggerClient - Daemon logger used for supervision messages.
        """
        for runtime in reversed(report.managed_runtimes):
            try:
                runtime.stop(timeout=2.0)
            except TypeError:
                runtime.stop()
            except Exception as ex:
                logs.message_error = f"cannot stop plugin runtime: {ex}"
            cls.__wait_for_runtime_shutdown(runtime=runtime, logs=logs)

        if report.dispatch is None:
            return None

        report.dispatch.stop()
        while report.dispatch._is_stopped != True:
            report.dispatch.join()
            time.sleep(0.1)
        report.dispatch.join()

    # #[PRIVATE METHODS]############################################################
    @classmethod
    def __build_plugin_context(
        cls,
        app_meta: AppName,
        conf: "AppConfig",
        config: Dict[str, Any],
        dispatcher: DispatcherAdapter,
        logs: LoggerClient,
        plugin: PluginDefinition,
    ) -> PluginContext:
        """Build runtime context for one plugin instance.

        ### Arguments:
        * app_meta: AppName - Application identity metadata.
        * conf: AppConfig - Loaded application configuration service.
        * config: Dict[str, Any] - Parsed plugin config values.
        * dispatcher: DispatcherAdapter - Plugin-facing dispatcher adapter.
        * logs: LoggerClient - Daemon logger used by the supervision service.
        * plugin: PluginDefinition - Discovered plugin instance definition.

        ### Returns:
        PluginContext - Runtime context passed to the plugin factory.

        ### Raises:
        * RuntimeError: If the daemon context is incomplete.
        """
        if conf.cf is None or logs.logs_queue is None:
            raise Raise.error(
                "Daemon configuration context is incomplete.",
                RuntimeError,
                cls.__name__,
                currentframe(),
            )
        return PluginContext(
            app_meta=app_meta,
            config=config,
            config_handler=conf.cf,
            debug=conf.debug,
            dispatcher=dispatcher,
            instance_name=plugin.instance_name,
            logger=LoggerClient(queue=logs.logs_queue, name=plugin.instance_name),
            plugin_id=plugin.spec.plugin_id,
            plugin_kind=plugin.spec.plugin_kind,
            qlog=logs.logs_queue,
            verbose=conf.verbose,
        )

    @classmethod
    def __log_summary(cls, report: PluginServiceReport, logs: LoggerClient) -> None:
        """Log a short summary for one plugin supervision cycle.

        ### Arguments:
        * report: PluginServiceReport - Supervision cycle result.
        * logs: LoggerClient - Daemon logger used for summary messages.
        """
        logs.message_info = (
            "plugin supervision summary: "
            f"initialized={len(report.initialized)}, "
            f"started={len(report.started)}, "
            f"failed={len(report.failed)}, "
            f"skipped={len(report.skipped)}"
        )
        if report.failed:
            failed_summary: str = ", ".join(
                f"{item.instance_name}:{item.stage}" for item in report.failed
            )
            logs.message_warning = f"failed plugin instances: {failed_summary}"
        if report.skipped:
            skipped_summary: str = ", ".join(
                f"{item.instance_name}:{item.stage}" for item in report.skipped
            )
            logs.message_warning = f"skipped plugin instances: {skipped_summary}"

    @classmethod
    def __mark_skipped(
        cls,
        report: PluginServiceReport,
        plugins: List[PluginDefinition],
        reason: str,
        stage: str,
    ) -> None:
        """Mark plugins as skipped when the service cannot attempt startup.

        ### Arguments:
        * report: PluginServiceReport - Supervision report being updated.
        * plugins: List[PluginDefinition] - Plugins skipped by the service.
        * reason: str - Skip reason.
        * stage: str - Lifecycle stage where skip occurred.
        """
        for plugin in plugins:
            report.skipped.append(
                PluginSkip(
                    instance_name=plugin.instance_name,
                    reason=reason,
                    stage=stage,
                )
            )

    @classmethod
    def __wait_for_runtime_shutdown(
        cls,
        runtime: PluginRuntime,
        logs: LoggerClient,
    ) -> None:
        """Wait for one runtime to reach a terminal shutdown state.

        ### Arguments:
        * runtime: PluginRuntime - Managed runtime being stopped.
        * logs: LoggerClient - Daemon logger used for shutdown warnings.
        """
        for _ in range(50):
            if runtime.state().state in (
                PluginState.STOPPED,
                PluginState.FAILED,
            ):
                return None
            if hasattr(runtime, "join"):
                runtime.join(timeout=0.1)  # type: ignore[misc]
            time.sleep(0.1)

        logs.message_warning = (
            "plugin runtime did not reach a terminal shutdown state within "
            "the supervision timeout"
        )


# #[EOF]#######################################################################
