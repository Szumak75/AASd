# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Provide regression coverage for plugin discovery and config parsing.
"""

import os
import tempfile
import unittest
import io

from pathlib import Path
from queue import Queue
from unittest.mock import patch

from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.logstool import LoggerClient, LoggerQueue

from libs import AppName
from libs.com.message import Message, ThDispatcher
from libs.plugins import (
    DispatcherAdapter,
    PluginCommonKeys,
    PluginConfigParser,
    PluginContext,
    PluginHealth,
    PluginHostKeys,
    PluginState,
    PluginLoader,
)
from libs.templates import PluginConfigField, PluginConfigSchema


class TestLibsPlugins(unittest.TestCase):
    """Cover plugin loader and parser helpers."""

    # #[PRIVATE METHODS]###############################################################
    def __write_test_plugin(self, target: Path, plugin_id: str) -> None:
        """Write a minimal plugin implementation to the target directory.

        ### Arguments:
        * target: Path - Plugin instance directory.
        * plugin_id: str - Plugin implementation identifier.
        """
        target.mkdir()
        (target / "load.py").write_text(
            "\n".join(
                [
                    "from libs.plugins import PluginKind, PluginSpec",
                    "from libs.templates import PluginConfigField, PluginConfigSchema",
                    "",
                    "def _runtime(_context):",
                    "    class Runtime(object):",
                    "        def initialize(self):",
                    "            return None",
                    "        def start(self):",
                    "            return None",
                    "        def stop(self, timeout=None):",
                    "            return None",
                    "        def state(self):",
                    "            from libs.plugins import PluginState, PluginStateSnapshot",
                    "            return PluginStateSnapshot(state=PluginState.STOPPED)",
                    "        def health(self):",
                    "            from libs.plugins import PluginHealth, PluginHealthSnapshot",
                    "            return PluginHealthSnapshot(health=PluginHealth.HEALTHY)",
                    "    return Runtime()",
                    "",
                    "def get_plugin_spec():",
                    "    return PluginSpec(",
                    "        api_version=1,",
                    "        config_schema=PluginConfigSchema(",
                    "            title='Loader test plugin.',",
                    "            fields=[",
                    "                PluginConfigField(",
                    "                    name='channel',",
                    "                    field_type=int,",
                    "                    default=7,",
                    "                    required=True,",
                    "                    description='Test channel.',",
                    "                )",
                    "            ],",
                    "        ),",
                    f"        plugin_id='{plugin_id}',",
                    "        plugin_kind=PluginKind.COMMUNICATION,",
                    "        plugin_name='loader_test',",
                    "        runtime_factory=_runtime,",
                    "    )",
                ]
            ),
            encoding="utf-8",
        )

    # #[PUBLIC METHODS]################################################################
    def test_01_loader_discovers_directories_and_symlink_instances(self) -> None:
        """Discover plugin instances from directories and symlinks."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            plugins_dir = Path(tmp_dir) / "plugins"
            plugins_dir.mkdir()
            self.__write_test_plugin(plugins_dir / "plugin_a", "plugin.test")

            symlink_path = plugins_dir / "plugin_b"
            os.symlink(plugins_dir / "plugin_a", symlink_path)

            discovered = PluginLoader.discover(plugins_dir)

            self.assertEqual([item.instance_name for item in discovered], ["plugin_a", "plugin_b"])
            self.assertEqual(discovered[0].spec.plugin_id, "plugin.test")
            self.assertEqual(discovered[1].spec.plugin_id, "plugin.test")

    def test_01a_public_plugin_key_classes_expose_shared_constants(self) -> None:
        """Expose shared plugin keys through the public package API."""
        self.assertEqual(PluginCommonKeys.CHANNEL, "channel")
        self.assertEqual(PluginCommonKeys.MESSAGE_CHANNEL, "message_channel")
        self.assertEqual(PluginCommonKeys.SLEEP_PERIOD, "sleep_period")
        self.assertEqual(PluginHostKeys.AUTOSTART, "autostart")
        self.assertEqual(PluginHostKeys.START_DELAY, "start_delay")
        self.assertEqual(PluginHostKeys.RESTART_POLICY, "restart_policy")

    def test_01b_dispatcher_adapter_uses_typed_storage_for_queue_access(self) -> None:
        """Publish and register through `DispatcherAdapter` backed by `BData`."""
        qcom: Queue = Queue()
        dispatcher = ThDispatcher(
            qlog=LoggerQueue(),
            qcom=qcom,
            debug=False,
            verbose=False,
        )
        adapter = DispatcherAdapter(qcom=qcom, dispatcher=dispatcher)
        message = object.__new__(Message)

        adapter.publish(message)  # type: ignore[arg-type]
        consumer_queue = adapter.register_consumer(7)

        self.assertIs(qcom.get_nowait(), message)
        self.assertIsInstance(consumer_queue, Queue)

    def test_02_parser_validates_and_returns_schema_values(self) -> None:
        """Parse config values according to the declared schema."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "plugin.conf"
            cfg = ConfigTool(str(config_file), "plugin", auto_create=True)
            cfg.set("plugin", varname="channel", value=9)
            cfg.set("plugin", varname="stdout_prefix", value="[test]")
            self.assertTrue(cfg.save())
            self.assertTrue(cfg.load())

            schema = PluginConfigSchema(
                title="Parser test.",
                fields=[
                    PluginConfigField(
                        name="channel",
                        field_type=int,
                        default=1,
                        required=True,
                        description="Channel number.",
                    ),
                    PluginConfigField(
                        name="stdout_prefix",
                        field_type=str,
                        default="[default]",
                        required=True,
                        description="Stdout prefix.",
                    ),
                ],
            )

            parsed = PluginConfigParser.parse(cfg, "plugin", schema)

            self.assertEqual(parsed["channel"], 9)
            self.assertEqual(parsed["stdout_prefix"], "[test]")

    def test_03_loader_should_reject_plugin_without_entry_point(self) -> None:
        """Reject plugin directories that do not expose `get_plugin_spec()`."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            plugins_dir = Path(tmp_dir) / "plugins"
            plugins_dir.mkdir()
            broken = plugins_dir / "broken_plugin"
            broken.mkdir()
            (broken / "load.py").write_text("VALUE = 1\n", encoding="utf-8")

            with self.assertRaises(RuntimeError):
                PluginLoader.discover(plugins_dir)

    def test_04_loader_should_reject_invalid_plugin_spec(self) -> None:
        """Reject plugins that return objects other than `PluginSpec`."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            plugins_dir = Path(tmp_dir) / "plugins"
            plugins_dir.mkdir()
            broken = plugins_dir / "broken_spec"
            broken.mkdir()
            (broken / "load.py").write_text(
                "def get_plugin_spec():\n    return 'bad'\n",
                encoding="utf-8",
            )

            with self.assertRaises(TypeError):
                PluginLoader.discover(plugins_dir)

    def test_05_parser_should_reject_missing_required_value(self) -> None:
        """Reject config sections that miss a required non-nullable field."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "plugin.conf"
            cfg = ConfigTool(str(config_file), "plugin", auto_create=True)
            cfg.set("plugin", varname="channel", value=None)
            self.assertTrue(cfg.save())
            self.assertTrue(cfg.load())

            schema = PluginConfigSchema(
                title="Parser test.",
                fields=[
                    PluginConfigField(
                        name="channel",
                        field_type=int,
                        default=None,
                        required=True,
                        description="Channel number.",
                    )
                ],
            )

            with self.assertRaises(ValueError):
                PluginConfigParser.parse(cfg, "plugin", schema)

    def test_06_example_plugins_should_exchange_message_via_dispatcher(self) -> None:
        """Start `example1` and `example2` and verify channel-based dispatching."""
        project_dir = Path(__file__).resolve().parent.parent
        plugins_dir = project_dir / "plugins"
        discovered = PluginLoader.discover(plugins_dir)
        plugin_map = {item.instance_name: item for item in discovered}

        self.assertIn("example1", plugin_map)
        self.assertIn("example2", plugin_map)

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "plugin.conf"
            cfg = ConfigTool(str(config_file), "AASd", auto_create=True)
            cfg.set("example1", varname="channel", value=11)
            cfg.set("example1", varname="message_text", value="Hello plugin.")
            cfg.set("example2", varname="channel", value=11)
            cfg.set("example2", varname="stdout_prefix", value="[consumer]")
            self.assertTrue(cfg.save())
            self.assertTrue(cfg.load())

            qcom: Queue = Queue()
            dispatcher = ThDispatcher(
                qlog=LoggerQueue(),
                qcom=qcom,
                debug=True,
                verbose=False,
            )
            dispatcher_adapter = DispatcherAdapter(qcom=qcom, dispatcher=dispatcher)
            app_meta = AppName(app_name="AASd", app_version="2.1.0-DEV")
            logger_queue = LoggerQueue()

            example2_config = PluginConfigParser.parse(
                cfg, "example2", plugin_map["example2"].spec.config_schema
            )
            example1_config = PluginConfigParser.parse(
                cfg, "example1", plugin_map["example1"].spec.config_schema
            )

            context_2 = PluginContext(
                app_meta=app_meta,
                config=example2_config,
                config_handler=cfg,
                debug=True,
                dispatcher=dispatcher_adapter,
                instance_name="example2",
                logger=LoggerClient(queue=logger_queue, name="example2"),
                plugin_id=plugin_map["example2"].spec.plugin_id,
                plugin_kind=plugin_map["example2"].spec.plugin_kind,
                qlog=logger_queue,
                verbose=False,
            )
            context_1 = PluginContext(
                app_meta=app_meta,
                config=example1_config,
                config_handler=cfg,
                debug=True,
                dispatcher=dispatcher_adapter,
                instance_name="example1",
                logger=LoggerClient(queue=logger_queue, name="example1"),
                plugin_id=plugin_map["example1"].spec.plugin_id,
                plugin_kind=plugin_map["example1"].spec.plugin_kind,
                qlog=logger_queue,
                verbose=False,
            )

            consumer = plugin_map["example2"].spec.runtime_factory(context_2)
            producer = plugin_map["example1"].spec.runtime_factory(context_1)

            with patch("sys.stdout", new_callable=io.StringIO) as stdout_buffer:
                dispatcher.start()
                consumer.initialize()
                producer.initialize()
                consumer.start()
                producer.start()
                producer.join(timeout=1.0)  # type: ignore[attr-defined]
                consumer.stop(timeout=1.0)
                consumer.join(timeout=1.0)  # type: ignore[attr-defined]
                dispatcher.stop()
                dispatcher.join(timeout=1.0)

                self.assertIn("[consumer]", stdout_buffer.getvalue())
                self.assertIn("Hello plugin.", stdout_buffer.getvalue())
                self.assertEqual(producer.state().state, PluginState.STOPPED)
                self.assertEqual(consumer.health().health, PluginHealth.HEALTHY)


# #[EOF]#######################################################################
