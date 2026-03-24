# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-24

Purpose: Provide regression coverage for plugin thread mixins.
"""

import unittest

from queue import Queue

from libs import AppName
from libs.plugins import (
    DispatcherAdapter,
    PluginContext,
    PluginHealth,
    PluginHealthSnapshot,
    PluginKind,
    PluginState,
    PluginStateSnapshot,
    ThPluginMixin,
)
from libs.com.message import ThDispatcher
from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.logstool import LoggerClient, LoggerQueue


class _MixinProbe(ThPluginMixin):
    """Minimal probe object exposing `ThPluginMixin` storage."""


class TestLibsPluginsMixins(unittest.TestCase):
    """Cover typed storage provided by `ThPluginMixin`."""

    # #[PUBLIC METHODS]################################################################
    def test_01_plugin_mixin_should_store_typed_runtime_attributes(self) -> None:
        """Store and return typed context, queue, state, and health values."""
        obj = _MixinProbe()
        qlog = LoggerQueue()
        qcom: Queue = Queue()
        dispatcher = ThDispatcher(
            qlog=qlog,
            qcom=qcom,
            debug=False,
            verbose=False,
        )
        adapter = DispatcherAdapter(qcom=qcom, dispatcher=dispatcher)
        context = PluginContext(
            app_meta=AppName(app_name="AASd", app_version="2.3.4-DEV"),
            config={},
            config_handler=ConfigTool("/tmp/unused.conf", "AASd", auto_create=True),
            debug=False,
            dispatcher=adapter,
            instance_name="probe",
            logger=LoggerClient(queue=qlog, name="probe"),
            plugin_id="test.probe",
            plugin_kind=PluginKind.WORKER,
            qlog=qlog,
            verbose=False,
        )
        health = PluginHealthSnapshot(health=PluginHealth.HEALTHY)
        state = PluginStateSnapshot(state=PluginState.CREATED)
        queue: Queue = Queue()

        obj._context = context
        obj._health = health
        obj._queue = queue
        obj._state = state

        self.assertIs(obj._context, context)
        self.assertIs(obj._health, health)
        self.assertIs(obj._queue, queue)
        self.assertIs(obj._state, state)


# #[EOF]#######################################################################
