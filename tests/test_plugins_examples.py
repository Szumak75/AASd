# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-24

Purpose: Provide regression coverage for the reference plugin runtimes.
"""

import unittest

from queue import Queue
from types import SimpleNamespace
from unittest.mock import MagicMock

from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.logstool import LoggerClient, LoggerQueue

from libs import AppName
from libs.plugins import (
    DispatcherAdapter,
    PluginHealth,
    PluginState,
    ThPluginMixin,
)
from libs.com.message import ThDispatcher
from plugins.example1.load import get_plugin_spec as get_example1_plugin_spec
from plugins.example2.load import get_plugin_spec as get_example2_plugin_spec


class TestPluginExamples(unittest.TestCase):
    """Cover failure guards and exports of the reference plugin runtimes."""

    # #[PRIVATE METHODS]###############################################################
    def __build_context(self, instance_name: str) -> SimpleNamespace:
        """Build a minimal plugin context for reference runtime tests.

        ### Arguments:
        * instance_name: str - Runtime instance name.

        ### Returns:
        SimpleNamespace - Minimal context object accepted by the runtime factory.
        """
        qlog = LoggerQueue()
        qcom: Queue = Queue()
        dispatcher = ThDispatcher(
            qlog=qlog,
            qcom=qcom,
            debug=False,
            verbose=False,
        )
        adapter = DispatcherAdapter(qcom=qcom, dispatcher=dispatcher)
        return SimpleNamespace(
            app_meta=AppName(app_name="AASd", app_version="2.3.2-DEV"),
            config={},
            config_handler=ConfigTool("/tmp/unused.conf", "AASd", auto_create=True),
            debug=False,
            dispatcher=adapter,
            instance_name=instance_name,
            logger=LoggerClient(queue=qlog, name=instance_name),
            plugin_id=f"test.{instance_name}",
            plugin_kind="worker",
            qlog=qlog,
            verbose=False,
        )

    # #[PUBLIC METHODS]################################################################
    def test_01_public_plugins_package_should_export_thread_plugin_mixin(self) -> None:
        """Expose `ThPluginMixin` through the public plugin package."""
        self.assertTrue(issubclass(ThPluginMixin, object))

    def test_02_example1_runtime_should_fail_cleanly_without_stop_event(self) -> None:
        """Return a failed state instead of crashing when `_stop_event` is missing."""
        context = self.__build_context("example1_guard")
        context.config = {"channel": 1, "message_text": "hello"}
        runtime = get_example1_plugin_spec().runtime_factory(context)
        runtime._delete_data("_stop_event")
        context.dispatcher.publish = MagicMock()

        runtime.run()

        self.assertEqual(runtime.health().health, PluginHealth.UNHEALTHY)
        self.assertEqual(runtime.state().state, PluginState.FAILED)
        context.dispatcher.publish.assert_not_called()

    def test_03_example2_runtime_should_fail_cleanly_without_stop_event(self) -> None:
        """Return a failed state instead of crashing when `_stop_event` is missing."""
        context = self.__build_context("example2_guard")
        context.config = {"channel": 1, "stdout_prefix": "[example2]"}
        runtime = get_example2_plugin_spec().runtime_factory(context)
        runtime._delete_data("_stop_event")

        runtime.stop()

        self.assertEqual(runtime.health().health, PluginHealth.UNHEALTHY)
        self.assertEqual(runtime.state().state, PluginState.FAILED)


# #[EOF]#######################################################################
