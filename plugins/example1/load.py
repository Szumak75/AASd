# -*- coding: UTF-8 -*-
"""
Example worker plugin.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Emit one startup message to configured dispatcher channels.
"""

from time import time
from threading import Event, Thread
from typing import Optional

from libs.com.message import Message
from libs.plugins import (
    NotificationScheduler,
    PluginCommonKeys,
    PluginContext,
    PluginHealth,
    PluginHealthSnapshot,
    PluginKind,
    PluginSpec,
    PluginState,
    PluginStateSnapshot,
    ThPluginMixin,
)
from libs.templates import PluginConfigField, PluginConfigSchema

from jsktoolbox.attribtool import ReadOnlyClass


class _Keys(object, metaclass=ReadOnlyClass):
    """Plugin configuration keys."""

    MESSAGE_TEXT: str = "message_text"


class _Runtime(Thread, ThPluginMixin):
    """Emit one example startup message and then stop."""

    _notifications: Optional[NotificationScheduler] = None

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
        self._notifications = NotificationScheduler.from_config(context.config)
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
        health: Optional[PluginHealthSnapshot] = self._health
        if health is None:
            return PluginHealthSnapshot(
                health=PluginHealth.UNKNOWN,
                message="Health snapshot is not initialized.",
            )
        return health

    def run(self) -> None:
        """Emit one configured startup message."""
        stop_event: Optional[Event] = self._stop_event
        if stop_event is None:
            self._health = PluginHealthSnapshot(
                health=PluginHealth.UNHEALTHY,
                last_error_at=int(time()),
                message="Stop event is not initialized.",
            )
            self._state = PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Stop event is not initialized.",
                stopped_at=int(time()),
            )
            return None

        if stop_event.is_set():
            self._state = PluginStateSnapshot(
                state=PluginState.STOPPED,
                stopped_at=int(time()),
            )
            return None
        context: Optional[PluginContext] = self._context
        if context is None:
            self._health = PluginHealthSnapshot(
                health=PluginHealth.UNHEALTHY,
                last_error_at=int(time()),
                message="Plugin context is not initialized.",
            )
            self._state = PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Plugin context is not initialized.",
                stopped_at=int(time()),
            )
            return None
        notifications: Optional[NotificationScheduler] = self._notifications
        if notifications is None:
            self._health = PluginHealthSnapshot(
                health=PluginHealth.UNHEALTHY,
                last_error_at=int(time()),
                message="Notification scheduler is not initialized.",
            )
            self._state = PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Notification scheduler is not initialized.",
                stopped_at=int(time()),
            )
            return None
        for channel in notifications.due_channels():
            message = Message()
            message.channel = int(channel)
            message.subject = (
                f"[{context.app_meta.app_name}:{context.instance_name}] "
                "example1 startup notification"
            )
            message.messages = [str(context.config[_Keys.MESSAGE_TEXT])]
            context.dispatcher.publish(message)
        context.logger.message_info = "startup message emitted"
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
        stop_event.set()

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
        state: Optional[PluginStateSnapshot] = self._state
        if state is None:
            return PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Lifecycle snapshot is not initialized.",
            )
        if self.is_alive() and state.state == PluginState.STARTING:
            state = PluginStateSnapshot(
                state=PluginState.RUNNING,
                started_at=state.started_at,
            )
            self._state = state
        return state

    def stop(self, timeout: float | None = None) -> None:
        """Request plugin shutdown."""
        stop_event: Optional[Event] = self._stop_event
        if stop_event is None:
            self._health = PluginHealthSnapshot(
                health=PluginHealth.UNHEALTHY,
                last_error_at=int(time()),
                message="Stop event is not initialized.",
            )
            self._state = PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Stop event is not initialized.",
                stopped_at=int(time()),
            )
            return None

        state: Optional[PluginStateSnapshot] = self._state
        if state is None:
            self._state = PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Lifecycle snapshot is not initialized.",
                stopped_at=int(time()),
            )
            return None
        if state.state not in (PluginState.STOPPED, PluginState.FAILED):
            self._state = PluginStateSnapshot(
                state=PluginState.STOPPING,
                started_at=state.started_at,
            )
        stop_event.set()
        if self.is_alive():
            self.join(timeout=timeout)
        state = self._state
        self._state = PluginStateSnapshot(
            state=PluginState.STOPPED,
            started_at=state.started_at if state is not None else None,
            stopped_at=int(time()),
        )


def get_plugin_spec() -> PluginSpec:
    """Return the plugin spec for `example1`.

    ### Returns:
    PluginSpec - Plugin manifest.
    """
    schema = PluginConfigSchema(
        title="Example worker plugin.",
        description="Emits one startup message to configured dispatcher channels.",
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
            # PluginConfigField(
            #     name=PluginCommonKeys.AT_CHANNEL,
            #     field_type=list,
            #     default=[],
            #     required=False,
            #     description=(
            #         "Cron-like notification targets, for example "
            #         "`['3:0;8|20;*;*;*']`."
            #     ),
            # ),
            PluginConfigField(
                name=_Keys.MESSAGE_TEXT,
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
