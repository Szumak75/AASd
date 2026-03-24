# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Provide regression coverage for the messaging subsystem primitives.
"""

import unittest

from datetime import datetime
from queue import Empty, Full, Queue
from typing import Any
from unittest.mock import patch

from jsktoolbox.logstool import LoggerQueue

from libs.com.message import (
    _Keys,
    AtChannel,
    Channel,
    Message,
    Multipart,
    NotificationScheduler,
    ThDispatcher,
)


class _FullQueue(Queue):
    """Simulate a permanently full target queue."""

    # #[PUBLIC METHODS]################################################################
    def put(self, item: Any, block: bool = True, timeout: float | None = None) -> None:
        """Always raise `Full` to exercise dispatcher fallback.

        ### Arguments:
        * item: Any - Ignored queued object.
        * block: bool - Unused compatibility argument.
        * timeout: float | None - Unused compatibility argument.

        ### Raises:
        * Full: Always raised.
        """
        del item
        del block
        del timeout
        raise Full


class _StopOnEmptyQueue(Queue):
    """Stop the dispatcher once an `Empty` exception is raised."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self, dispatcher: ThDispatcher) -> None:
        """Store the dispatcher used by the fake queue.

        ### Arguments:
        * dispatcher: ThDispatcher - Dispatcher instance under test.
        """
        self._dispatcher = dispatcher

    # #[PUBLIC METHODS]################################################################
    def get(self, block: bool = True, timeout: float = 0.0) -> Any:
        """Raise `Empty` once and request dispatcher shutdown.

        ### Arguments:
        * block: bool - Unused compatibility argument.
        * timeout: float - Unused compatibility argument.

        ### Raises:
        * Empty: Always raised to exercise dispatcher handling.
        """
        del block
        del timeout
        self._dispatcher.stop()
        raise Empty


class _StopOnRuntimeErrorQueue(Queue):
    """Stop the dispatcher after raising a generic queue error."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self, dispatcher: ThDispatcher) -> None:
        """Store the dispatcher used by the fake queue.

        ### Arguments:
        * dispatcher: ThDispatcher - Dispatcher instance under test.
        """
        self._dispatcher = dispatcher

    # #[PUBLIC METHODS]################################################################
    def get(self, block: bool = True, timeout: float = 0.0) -> Any:
        """Raise `RuntimeError` once and request dispatcher shutdown.

        ### Arguments:
        * block: bool - Unused compatibility argument.
        * timeout: float - Unused compatibility argument.

        ### Raises:
        * RuntimeError: Always raised to exercise dispatcher handling.
        """
        del block
        del timeout
        self._dispatcher.stop()
        raise RuntimeError("boom")


class TestAtChannel(unittest.TestCase):
    """Cover cron-like channel scheduling."""

    def test_01_should_build_all_supported_cron_value_forms(self) -> None:
        """Verify wildcard, list, range, and mixed cron fragments."""
        obj = AtChannel(
            [
                "cron:*;1|3;10-12;1-2|5;0|2-3|7",
                "cron:15;6;20;4;1",
            ]
        )

        cron = obj.get_channels["cron"][0]

        self.assertEqual(cron[_Keys.AT_MINUTE][0], 0)
        self.assertEqual(cron[_Keys.AT_MINUTE][-1], 59)
        self.assertEqual(cron[_Keys.AT_HOUR], [1, 3])
        self.assertEqual(cron[_Keys.AT_DAY], [10, 11, 12])
        self.assertEqual(cron[_Keys.AT_MONTH], [1, 2, 5])
        self.assertEqual(cron[_Keys.AT_DAY_WEEK], [0, 2, 3, 7])

    def test_02_should_report_due_channels_for_weekday_and_deduplicate(self) -> None:
        """Return one channel even when multiple rules match the same time."""
        now = datetime(2026, 3, 23, 12, 15, 0)
        obj = AtChannel(
            [
                "mail:15;12;23;3;1",
                "mail:15;12;23;3;1",
                "other:0;0;1;1;1",
            ]
        )

        with patch("libs.com.message.MDateTime.now", return_value=now):
            self.assertTrue(obj.check)
            self.assertEqual(obj.get, ["mail"])

    def test_03_should_support_sunday_as_zero_or_seven(self) -> None:
        """Treat Sunday as both `0` and `7`."""
        now = datetime(2026, 3, 22, 9, 30, 0)
        obj = AtChannel(
            [
                "sms:30;9;22;3;0",
                "email:30;9;22;3;7",
            ]
        )

        with patch("libs.com.message.MDateTime.now", return_value=now):
            self.assertTrue(obj.check)
            self.assertEqual(obj.get, ["sms", "email"])

    def test_04_should_reject_invalid_configuration_inputs(self) -> None:
        """Raise the documented exceptions for malformed cron config."""
        with self.assertRaises(TypeError):
            AtChannel(("mail:0;0;1;1;1",))  # type: ignore[arg-type]

        with self.assertRaises(ValueError):
            AtChannel(["mail-0;0;1;1;1"])

        with self.assertRaises(ValueError):
            AtChannel(["mail:0;0;1;1"])

        with self.assertRaises(ValueError):
            AtChannel(["mail:abc;0;1;1;1"])

        with self.assertRaises(ValueError):
            AtChannel(["mail:1|abc;0;1;1;1"])

        with self.assertRaises(ValueError):
            AtChannel(["mail:1-bad;0;1;1;1"])

        with self.assertRaises(ValueError):
            AtChannel(["mail:1|2-bad;0;1;1;1"])

    def test_05_should_return_false_when_no_schedule_matches(self) -> None:
        """Return a negative result when nothing is due."""
        now = datetime(2026, 3, 23, 12, 14, 0)
        obj = AtChannel(["mail:15;12;23;3;1"])

        with patch("libs.com.message.MDateTime.now", return_value=now):
            self.assertFalse(obj.check)
            self.assertEqual(obj.get, [])


class TestChannel(unittest.TestCase):
    """Cover interval-based channel scheduling."""

    def test_01_should_build_interval_channels_and_return_due_entries(self) -> None:
        """Convert intervals to seconds and reschedule due channels."""
        with patch("libs.com.message.Timestamp.now", side_effect=[100, 100, 100, 150]):
            obj = Channel(["one", "two:5m", "three:2h"])

        self.assertEqual(obj.channels, ["one", "two", "three"])
        self.assertEqual(obj.get_channels["one"][_Keys.CHECK_INTERVAL], 0)
        self.assertEqual(obj.get_channels["two"][_Keys.CHECK_INTERVAL], 300)
        self.assertEqual(obj.get_channels["three"][_Keys.CHECK_INTERVAL], 7200)

        obj.get_channels["one"][_Keys.CHECK_NEXT] = 149
        obj.get_channels["two"][_Keys.CHECK_NEXT] = 200
        obj.get_channels["three"][_Keys.CHECK_NEXT] = 120

        with patch("libs.com.message.Timestamp.now", return_value=150):
            self.assertTrue(obj.check)
            self.assertEqual(obj.get, ["one", "three"])

        self.assertEqual(obj.get_channels["one"][_Keys.CHECK_NEXT], 150)
        self.assertEqual(obj.get_channels["three"][_Keys.CHECK_NEXT], 7350)

    def test_02_should_reject_invalid_channel_configuration(self) -> None:
        """Raise on invalid config type, duplicate channels, and bad intervals."""
        with self.assertRaises(TypeError):
            Channel(("one",))  # type: ignore[arg-type]

        with self.assertRaises(KeyError):
            Channel(["dup", "dup:10s"])

        with self.assertRaises(ValueError):
            Channel(["bad:xxx"])

    def test_03_should_raise_when_internal_channel_mapping_is_missing(self) -> None:
        """Protect getters against missing internal storage."""
        obj = Channel(["one"])
        obj._delete_data(key=_Keys.CHANNELS)

        with self.assertRaises(ValueError):
            _ = obj.get_channels

    def test_04_should_return_false_when_no_interval_is_due(self) -> None:
        """Return a negative result when all next timestamps are in the future."""
        with patch("libs.com.message.Timestamp.now", side_effect=[100, 100]):
            obj = Channel(["one", "two:5m"])

        obj.get_channels["one"][_Keys.CHECK_NEXT] = 101
        obj.get_channels["two"][_Keys.CHECK_NEXT] = 200

        with patch("libs.com.message.Timestamp.now", return_value=100):
            self.assertFalse(obj.check)
            self.assertEqual(obj.get, [])


class TestNotificationScheduler(unittest.TestCase):
    """Cover the combined notification scheduler helper."""

    def test_01_should_merge_due_interval_and_cron_channels(self) -> None:
        """Return unique due channels from both schedule sources."""
        with patch("libs.com.message.Timestamp.now", return_value=100):
            obj = NotificationScheduler(
                message_channel=[1, "2:5m"],
                at_channel=["2:15;12;23;3;1", "3:15;12;23;3;1"],
            )

        obj._interval_scheduler.get_channels["2"][_Keys.CHECK_NEXT] = 200  # type: ignore[union-attr]
        now = datetime(2026, 3, 23, 12, 15, 0)
        with patch("libs.com.message.Timestamp.now", return_value=100):
            with patch("libs.com.message.MDateTime.now", return_value=now):
                self.assertEqual(obj.due_channels(), [1, 2, 3])

    def test_02_should_build_from_config_and_validate_types(self) -> None:
        """Read worker notification settings from parsed plugin config."""
        obj = NotificationScheduler.from_config(
            {
                "message_channel": [1, "2:6h"],
                "at_channel": ["3:0;8;*;*;*"],
            }
        )

        self.assertTrue(obj.has_schedule)

        with self.assertRaises(TypeError):
            NotificationScheduler.from_config({"message_channel": "1"})  # type: ignore[arg-type]

        with self.assertRaises(TypeError):
            NotificationScheduler.from_config({"at_channel": "1:0;0;*;*;*"})  # type: ignore[arg-type]

    def test_03_should_raise_when_due_channel_cannot_be_converted_to_int(self) -> None:
        """Reject non-integer channel identifiers at dispatch-decision time."""
        now = datetime(2026, 3, 23, 12, 15, 0)
        obj = NotificationScheduler(at_channel=["mail:15;12;23;3;1"])

        with patch("libs.com.message.MDateTime.now", return_value=now):
            with self.assertRaises(ValueError):
                obj.due_channels()


class TestMessage(unittest.TestCase):
    """Cover message container accessors and validation."""

    def test_01_should_store_and_return_message_data(self) -> None:
        """Exercise all supported accessors on the message container."""
        obj = Message()

        self.assertIsNone(obj.channel)
        self.assertIsNone(obj.footer)
        self.assertIsNone(obj.mmessages)
        self.assertEqual(obj.messages, [])
        self.assertEqual(obj.counter, 1)
        self.assertEqual(obj.counter, 2)

        obj.channel = 7
        obj.footer = "footer"
        obj.reply_to = "reply@example.com"
        obj.sender = "sender@example.com"
        obj.subject = "subject"
        obj.messages = "body"
        obj.messages = ["line-1", "line-2"]
        obj.messages = 123  # type: ignore[assignment]
        obj.mmessages = {Multipart.PLAIN: "plain"}
        obj.mmessages = {Multipart.HTML: "<b>html</b>"}
        obj.to = "one@example.com"
        obj.to = ["", "two@example.com", "three@example.com"]

        self.assertEqual(obj.channel, 7)
        self.assertEqual(obj.footer, "footer")
        self.assertEqual(obj.reply_to, "reply@example.com")
        self.assertEqual(obj.sender, "sender@example.com")
        self.assertEqual(obj.subject, "subject")
        self.assertEqual(obj.messages, ["body", "line-1", "line-2", "123"])
        self.assertEqual(
            obj.mmessages,
            {
                Multipart.PLAIN: "plain",
                Multipart.HTML: "<b>html</b>",
            },
        )
        self.assertEqual(
            obj.to,
            ["one@example.com", "two@example.com", "three@example.com"],
        )

    def test_02_should_raise_on_invalid_message_inputs(self) -> None:
        """Validate type checking and internal-state protection."""
        obj = Message()

        with self.assertRaises(TypeError):
            obj.mmessages = "bad"  # type: ignore[assignment]

        with self.assertRaises(TypeError):
            obj.to = 10  # type: ignore[assignment]

        obj._delete_data(key=_Keys.MSG_COUNTER)
        with self.assertRaises(ValueError):
            _ = obj.counter

        obj = Message()
        obj._delete_data(key=_Keys.MSG_MESS)
        with self.assertRaises(ValueError):
            _ = obj.messages


class TestThDispatcher(unittest.TestCase):
    """Cover queue registration and dispatch behaviour."""

    # #[PRIVATE METHODS]###############################################################
    def __build_dispatcher(
        self, qcom: Any | None = None, debug: bool = False
    ) -> ThDispatcher:
        """Create a dispatcher with a valid logger queue.

        ### Arguments:
        * qcom: Any | None - Communication queue used by the dispatcher.
        * debug: bool - Debug mode flag.

        ### Returns:
        ThDispatcher - Dispatcher configured for tests.
        """
        if qcom is None:
            qcom = Queue()
        return ThDispatcher(qlog=LoggerQueue(), qcom=qcom, debug=debug)

    def test_01_should_register_queues_and_dispatch_message(self) -> None:
        """Send one message to all queues registered for a channel."""
        dispatcher = self.__build_dispatcher(debug=True)
        queue_one = dispatcher.register_queue(1)
        queue_two = dispatcher.register_queue("1")

        message = Message()
        message.channel = 1

        dispatcher._ThDispatcher__dispatch_message(message)

        self.assertIs(queue_one.get_nowait(), message)
        self.assertIs(queue_two.get_nowait(), message)

    def test_02_should_reject_invalid_registration_and_dispatch_inputs(self) -> None:
        """Validate registration and dispatch input types."""
        dispatcher = self.__build_dispatcher()

        with self.assertRaises(TypeError):
            dispatcher.register_queue(1.5)  # type: ignore[arg-type]

        with self.assertRaises(TypeError):
            dispatcher._ThDispatcher__dispatch_message("bad")  # type: ignore[arg-type]

        with self.assertRaises(ValueError):
            dispatcher._ThDispatcher__dispatch_message(Message())

    def test_03_should_ignore_full_target_queue(self) -> None:
        """Swallow `Full` and continue dispatching as implemented."""
        dispatcher = self.__build_dispatcher()
        queue_obj = _FullQueue(maxsize=1)
        dispatcher._ThDispatcher__get_comm_queues["5"] = [queue_obj]

        message = Message()
        message.channel = 5

        dispatcher._ThDispatcher__dispatch_message(message)

        self.assertEqual(queue_obj.qsize(), 0)

    def test_04_should_process_messages_in_run_loop(self) -> None:
        """Start the dispatcher thread and deliver one queued message."""
        qcom: Queue = Queue()
        dispatcher = self.__build_dispatcher(qcom=qcom)
        target_queue = dispatcher.register_queue(2)

        message = Message()
        message.channel = 2
        qcom.put(message)

        dispatcher.start()
        delivered = target_queue.get(timeout=1.0)
        dispatcher.stop()
        dispatcher.join(timeout=1.0)

        self.assertIs(delivered, message)

    def test_05_should_handle_empty_and_generic_queue_errors(self) -> None:
        """Exercise both non-fatal queue exception branches in `run()`."""
        dispatcher = self.__build_dispatcher(debug=True)
        dispatcher.qcom = _StopOnEmptyQueue(dispatcher)  # type: ignore[assignment]
        dispatcher.run()
        self.assertTrue(dispatcher.stopped)

        dispatcher = self.__build_dispatcher(debug=True)
        dispatcher.qcom = _StopOnRuntimeErrorQueue(dispatcher)  # type: ignore[assignment]
        dispatcher.run()
        self.assertTrue(dispatcher.stopped)


# #[EOF]#######################################################################
