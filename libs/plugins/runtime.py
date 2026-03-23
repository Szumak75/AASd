# -*- coding: UTF-8 -*-
"""
Plugin runtime contracts.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Provide runtime contracts and context objects for plugin API v1.
"""

from dataclasses import dataclass
from queue import Queue
from typing import Any, Callable, Dict, Optional, Protocol, runtime_checkable

from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.logstool import LoggerClient, LoggerQueue

from libs.app import AppName
from libs.com.message import Message, ThDispatcher
from libs.templates import PluginConfigSchema


class PluginKind(object):
    """Expose supported plugin kinds."""

    # #[CONSTANTS]####################################################################
    COMMUNICATION: str = "communication"
    WORKER: str = "worker"


@runtime_checkable
class PluginRuntime(Protocol):
    """Define the minimal runtime contract implemented by daemon-hosted plugins."""

    def start(self) -> None:
        """Start plugin processing."""

    def stop(self) -> None:
        """Request plugin shutdown."""

    def is_stopped(self) -> bool:
        """Return whether plugin processing is stopped."""


class DispatcherAdapter(object):
    """Expose a stable plugin-facing adapter for the dispatcher subsystem."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self, qcom: Queue, dispatcher: ThDispatcher) -> None:
        """Initialize the dispatcher adapter.

        ### Arguments:
        * qcom: Queue - Shared outbound dispatcher input queue.
        * dispatcher: ThDispatcher - Active dispatcher instance.
        """
        self._qcom = qcom
        self._dispatcher = dispatcher

    # #[PUBLIC METHODS]################################################################
    def publish(self, message: Message) -> None:
        """Publish a message to the dispatcher input queue.

        ### Arguments:
        * message: Message - Message routed by the dispatcher.
        """
        self._qcom.put(message)

    def register_consumer(self, channel: int) -> Queue:
        """Register a communication consumer queue for the selected channel.

        ### Arguments:
        * channel: int - Communication channel identifier.

        ### Returns:
        Queue - Queue receiving messages for the selected channel.
        """
        return self._dispatcher.register_queue(channel)


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
