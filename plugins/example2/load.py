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

from libs.com.message import Message
from libs.plugins import PluginContext, PluginKind, PluginSpec
from libs.templates import PluginConfigField, PluginConfigSchema


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
        self._context = context
        self._stop_event = Event()
        self._queue: Queue = context.dispatcher.register_consumer(
            int(context.config["channel"])
        )

    # #[PUBLIC METHODS]################################################################
    def run(self) -> None:
        """Consume messages from the configured dispatcher channel."""
        while not self._stop_event.is_set():
            try:
                message: Message = self._queue.get(block=True, timeout=0.1)
                prefix = str(self._context.config["stdout_prefix"])
                print(
                    f"{prefix} subject={message.subject} payload={message.messages}",
                    flush=True,
                )
                self._queue.task_done()
            except Empty:
                time.sleep(0.05)

    def is_stopped(self) -> bool:
        """Return whether plugin processing is stopped.

        ### Returns:
        bool - `True` when runtime is stopped.
        """
        return self._stop_event.is_set() and not self.is_alive()

    def stop(self) -> None:
        """Request plugin shutdown."""
        self._stop_event.set()


def get_plugin_spec() -> PluginSpec:
    """Return the plugin spec for `example2`.

    ### Returns:
    PluginSpec - Plugin manifest.
    """
    schema = PluginConfigSchema(
        title="Example communication plugin.",
        description="Consumes messages from a configured dispatcher channel and prints them to stdout.",
        fields=[
            PluginConfigField(
                name="channel",
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
