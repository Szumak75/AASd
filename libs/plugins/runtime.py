# -*- coding: UTF-8 -*-
"""
Plugin runtime contracts.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Provide runtime contracts, lifecycle state, and context objects for plugin API v1.
"""

from dataclasses import dataclass
from queue import Queue
from typing import Any, Callable, Dict, Optional, Protocol, runtime_checkable

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.basetool import BData
from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.logstool import LoggerClient, LoggerQueue

from libs.app import AppName
from libs.com.message import Message, ThDispatcher
from libs.templates import PluginConfigSchema


class PluginKind(object, metaclass=ReadOnlyClass):
    """Expose supported plugin kinds."""

    # #[CONSTANTS]##############################################################
    COMMUNICATION: str = "communication"
    WORKER: str = "worker"


class PluginState(object, metaclass=ReadOnlyClass):
    """Expose supported plugin lifecycle states."""

    # #[CONSTANTS]##############################################################
    CREATED: str = "created"
    FAILED: str = "failed"
    INITIALIZED: str = "initialized"
    RUNNING: str = "running"
    STARTING: str = "starting"
    STOPPED: str = "stopped"
    STOPPING: str = "stopping"


class PluginHealth(object, metaclass=ReadOnlyClass):
    """Expose supported plugin health states."""

    # #[CONSTANTS]##############################################################
    DEGRADED: str = "degraded"
    HEALTHY: str = "healthy"
    UNKNOWN: str = "unknown"
    UNHEALTHY: str = "unhealthy"


@dataclass(slots=True, frozen=True)
class PluginStateSnapshot:
    """Describe the current lifecycle state of one plugin instance."""

    state: str
    failure_count: int = 0
    message: Optional[str] = None
    started_at: Optional[int] = None
    stopped_at: Optional[int] = None


@dataclass(slots=True, frozen=True)
class PluginHealthSnapshot:
    """Describe the current operational health of one plugin instance."""

    health: str
    last_error_at: Optional[int] = None
    last_ok_at: Optional[int] = None
    message: Optional[str] = None


@runtime_checkable
class PluginRuntime(Protocol):
    """Define the minimal runtime contract implemented by daemon-hosted plugins."""

    def initialize(self) -> None:
        """Prepare plugin resources before startup."""

    def start(self) -> None:
        """Start plugin processing."""

    def stop(self, timeout: Optional[float] = None) -> None:
        """Request plugin shutdown."""

    def health(self) -> PluginHealthSnapshot:  # pyright: ignore[reportReturnType]
        """Return the current plugin health snapshot."""

    def state(self) -> PluginStateSnapshot:  # pyright: ignore[reportReturnType]
        """Return the current plugin lifecycle snapshot."""


class DispatcherAdapter(BData):
    """Expose a stable plugin-facing adapter for the dispatcher subsystem."""

    class __Keys(object, metaclass=ReadOnlyClass):
        """Define internal storage keys used by the plugin runtime helpers."""

        # #[CONSTANTS]##########################################################
        DISPATCHER: str = "__dispatcher__"
        QCOM: str = "__qcom__"

    # #[CONSTRUCTOR]############################################################
    def __init__(self, qcom: Queue, dispatcher: ThDispatcher) -> None:
        """Initialize the dispatcher adapter.

        ### Arguments:
        * qcom: Queue - Shared outbound dispatcher input queue.
        * dispatcher: ThDispatcher - Active dispatcher instance.
        """
        self._set_data(key=self.__Keys.QCOM, value=qcom, set_default_type=Queue)
        self._set_data(
            key=self.__Keys.DISPATCHER,
            value=dispatcher,
            set_default_type=ThDispatcher,
        )

    # #[PRIVATE PROPERTIES]#####################################################
    @property
    def __dispatcher(self) -> ThDispatcher:
        """Return the bound dispatcher instance.

        ### Returns:
        ThDispatcher - Bound dispatcher instance.
        """
        obj: Optional[ThDispatcher] = self._get_data(key=self.__Keys.DISPATCHER)
        if obj is None:
            raise ValueError("Dispatcher instance is not initialized.")
        return obj

    @property
    def __qcom(self) -> Queue:
        """Return the shared dispatcher input queue.

        ### Returns:
        Queue - Shared dispatcher input queue.
        """
        obj: Optional[Queue] = self._get_data(key=self.__Keys.QCOM)
        if obj is None:
            raise ValueError("Dispatcher queue is not initialized.")
        return obj

    # #[PUBLIC METHODS]#########################################################
    def publish(self, message: Message) -> None:
        """Publish a message to the dispatcher input queue.

        ### Arguments:
        * message: Message - Message routed by the dispatcher.
        """
        self.__qcom.put(message)

    def register_consumer(self, channel: int) -> Queue:
        """Register a communication consumer queue for the selected channel.

        ### Arguments:
        * channel: int - Communication channel identifier.

        ### Returns:
        Queue - Queue receiving messages for the selected channel.
        """
        return self.__dispatcher.register_queue(channel)


@dataclass(slots=True)
class PluginContext:
    """Store runtime context passed to plugin factories."""

    app_meta: AppName
    config: Dict[str, Any]
    config_handler: ConfigTool
    debug: bool
    dispatcher: DispatcherAdapter
    instance_name: str
    logger: LoggerClient
    plugin_id: str
    plugin_kind: str
    qlog: LoggerQueue
    verbose: bool


@dataclass(slots=True)
class PluginSpec:
    """Describe one plugin implementation exposed through `load.py`."""

    api_version: int
    config_schema: PluginConfigSchema
    plugin_id: str
    plugin_kind: str
    plugin_name: str
    runtime_factory: Callable[[PluginContext], PluginRuntime]
    author: Optional[str] = None
    description: Optional[str] = None
    homepage: Optional[str] = None
    plugin_version: Optional[str] = None


# #[EOF]#######################################################################
