# -*- coding: UTF-8 -*-
"""
Example communication plugin.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Consume dispatcher messages from a configured channel and print them.
"""

import time

from queue import Empty, Queue
from threading import Event, Thread
from typing import Optional

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
from libs.templates import PluginConfigField
from libs.templates import PluginConfigSchema


class _Runtime(Thread):
    """Read messages from one configured dispatcher channel and print them."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self, context: PluginContext) -> None:
        """Initialize the example communication runtime.

        ### Arguments:
        * context: PluginContext - Plugin runtime context.
        """
        Thread.__init__(self, name=context.instance_name)
        self.daemon = True
        self._context: PluginContext = context
        self._health = PluginHealthSnapshot(health=PluginHealth.UNKNOWN)
        self._stop_event = Event()
        self._queue: Optional[Queue] = None
        self._state = PluginStateSnapshot(state=PluginState.CREATED)

    def initialize(self) -> None:
        """Prepare the runtime before startup."""
        self._queue = self._context.dispatcher.register_consumer(
            int(self._context.config[PluginCommonKeys.CHANNEL])
        )
        self._state = PluginStateSnapshot(state=PluginState.INITIALIZED)

    # #[PUBLIC METHODS]################################################################
    def health(self) -> PluginHealthSnapshot:
        """Return the current health snapshot.

        ### Returns:
        PluginHealthSnapshot - Current plugin health snapshot.
        """
        return self._health

    def run(self) -> None:
        """Consume messages from the configured dispatcher channel."""
        if self._queue is None:
            self._health = PluginHealthSnapshot(
                health=PluginHealth.UNHEALTHY,
                last_error_at=int(time.time()),
                message="Consumer queue is not initialized.",
            )
            self._state = PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Consumer queue is not initialized.",
                stopped_at=int(time.time()),
            )
            return None
        while not self._stop_event.is_set():
            try:
                message: Message = self._queue.get(block=True, timeout=0.1)
                prefix = str(self._context.config["stdout_prefix"])
                print(
                    (
                        f"{prefix} subject={message.subject} "
                        f"payload={message.messages}"
                    ),
                    flush=True,
                )
                now = int(time.time())
                self._health = PluginHealthSnapshot(
                    health=PluginHealth.HEALTHY,
                    last_ok_at=now,
                    message="Message consumed successfully.",
                )
                self._queue.task_done()
            except Empty:
                time.sleep(0.05)
        self._state = PluginStateSnapshot(
            state=PluginState.STOPPED,
            started_at=self._state.started_at,
            stopped_at=int(time.time()),
        )

    def start(self) -> None:
        """Start the runtime thread."""
        self._state = PluginStateSnapshot(
            state=PluginState.STARTING,
            started_at=int(time.time()),
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

    def stop(self, timeout: Optional[float] = None) -> None:
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
            stopped_at=int(time.time()),
        )


def get_plugin_spec() -> PluginSpec:
    """Return the plugin spec for `example2`.

    ### Returns:
    PluginSpec - Plugin manifest.
    """
    schema = PluginConfigSchema(
        title="Example communication plugin.",
        description=(
            "Consumes messages from a configured dispatcher channel "
            "and prints them to stdout."
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
                name="stdout_prefix",
                field_type=str,
                default="[example2]",
                required=True,
                description="Prefix added to stdout output.",
                example="[example2]",
            ),
        ],
    )
    return PluginSpec(
        api_version=1,
        config_schema=schema,
        plugin_id="example.stdout_consumer",
        plugin_kind=PluginKind.COMMUNICATION,
        plugin_name="example2",
        runtime_factory=_Runtime,
        description="Example communication plugin printing routed messages.",
    )


# #[EOF]#######################################################################
