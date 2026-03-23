# -*- coding: UTF-8 -*-
"""
Example worker plugin.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Emit one startup message to a configured dispatcher channel.
"""

from threading import Event, Thread
from time import time

from libs.com.message import Message
from libs.plugins import (
    PluginCommonKeys,
    PluginContext,
    PluginHealth,
    PluginHealthSnapshot,
    PluginKind,
    PluginSpec,
    PluginState,
    PluginStateSnapshot,
)
from libs.templates import PluginConfigField, PluginConfigSchema


class _Runtime(Thread):
    """Emit one example startup message and then stop."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self, context: PluginContext) -> None:
        """Initialize the example worker runtime.

        ### Arguments:
        * context: PluginContext - Plugin runtime context.
        """
        Thread.__init__(self, name=context.instance_name)
        self.daemon = True
        self._context: PluginContext = context
        self._health = PluginHealthSnapshot(health=PluginHealth.UNKNOWN)
        self._stop_event = Event()
        self._state = PluginStateSnapshot(state=PluginState.CREATED)

    def initialize(self) -> None:
        """Prepare the runtime before startup."""
        self._state = PluginStateSnapshot(state=PluginState.INITIALIZED)

    # #[PUBLIC METHODS]################################################################
    def health(self) -> PluginHealthSnapshot:
        """Return the current health snapshot.

        ### Returns:
        PluginHealthSnapshot - Current plugin health snapshot.
        """
        return self._health

    def run(self) -> None:
        """Emit one configured startup message."""
        if self._stop_event.is_set():
            self._state = PluginStateSnapshot(
                state=PluginState.STOPPED,
                stopped_at=int(time()),
            )
            return None
        message = Message()
        message.channel = int(self._context.config[PluginCommonKeys.CHANNEL])
        message.subject = (
            f"[{self._context.app_meta.app_name}:{self._context.instance_name}] "
            "example1 startup notification"
        )
        message.messages = [str(self._context.config["message_text"])]
        self._context.dispatcher.publish(message)
        self._context.logger.message_info = "startup message emitted"
        now = int(time())
        self._health = PluginHealthSnapshot(
            health=PluginHealth.HEALTHY,
            last_ok_at=now,
            message="Startup message emitted successfully.",
        )
        self._state = PluginStateSnapshot(
            state=PluginState.STOPPED,
            started_at=now,
            stopped_at=now,
        )
        self._stop_event.set()

    def start(self) -> None:
        """Start the runtime thread."""
        self._state = PluginStateSnapshot(
            state=PluginState.STARTING,
            started_at=int(time()),
        )
        Thread.start(self)

    def state(self) -> PluginStateSnapshot:
        """Return the current lifecycle snapshot.

        ### Returns:
        PluginStateSnapshot - Current plugin lifecycle snapshot.
        """
        if self.is_alive() and self._state.state == PluginState.STARTING:
            self._state = PluginStateSnapshot(
                state=PluginState.RUNNING,
                started_at=self._state.started_at,
            )
        return self._state

    def stop(self, timeout: float | None = None) -> None:
        """Request plugin shutdown."""
        if self._state.state not in (PluginState.STOPPED, PluginState.FAILED):
            self._state = PluginStateSnapshot(
                state=PluginState.STOPPING,
                started_at=self._state.started_at,
            )
        self._stop_event.set()
        if self.is_alive():
            self.join(timeout=timeout)
        self._state = PluginStateSnapshot(
            state=PluginState.STOPPED,
            started_at=self._state.started_at,
            stopped_at=int(time()),
        )


def get_plugin_spec() -> PluginSpec:
    """Return the plugin spec for `example1`.

    ### Returns:
    PluginSpec - Plugin manifest.
    """
    schema = PluginConfigSchema(
        title="Example worker plugin.",
        description="Emits one startup message to the configured dispatcher channel.",
        fields=[
            PluginConfigField(
                name=PluginCommonKeys.CHANNEL,
                field_type=int,
                default=1,
                required=True,
                description="Dispatcher channel used for the startup message.",
            ),
            PluginConfigField(
                name="message_text",
                field_type=str,
                default="Hello from example1.",
                required=True,
                description="Text payload sent during daemon startup.",
            ),
        ],
    )
    return PluginSpec(
        api_version=1,
        config_schema=schema,
        plugin_id="example.startup_message",
        plugin_kind=PluginKind.WORKER,
        plugin_name="example1",
        runtime_factory=_Runtime,
        description="Example worker plugin emitting a startup message.",
    )


# #[EOF]#######################################################################
