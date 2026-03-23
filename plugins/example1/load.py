# -*- coding: UTF-8 -*-
"""
Example worker plugin.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Emit one startup message to a configured dispatcher channel.
"""

from queue import Empty
from threading import Event, Thread

from libs.com.message import Message
from libs.plugins import PluginContext, PluginKind, PluginSpec
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
        self._context = context
        self._stop_event = Event()

    # #[PUBLIC METHODS]################################################################
    def run(self) -> None:
        """Emit one configured startup message."""
        if self._stop_event.is_set():
            return None
        message = Message()
        message.channel = int(self._context.config["channel"])
        message.subject = (
            f"[{self._context.app_meta.app_name}:{self._context.instance_name}] "
            "example1 startup notification"
        )
        message.messages = [str(self._context.config["message_text"])]
        self._context.dispatcher.publish(message)
        self._context.logger.message_info = "startup message emitted"
        self._stop_event.set()

    def is_stopped(self) -> bool:
        """Return whether plugin processing is stopped.

        ### Returns:
        bool - `True` when runtime is stopped.
        """
        return self._stop_event.is_set()

    def stop(self) -> None:
        """Request plugin shutdown."""
        self._stop_event.set()


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
                name="channel",
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
