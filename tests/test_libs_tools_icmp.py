# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 2026-03-22

  Purpose: Regression tests for ICMP and traceroute helpers.
"""

import unittest

from unittest.mock import MagicMock, patch

from libs.tools import Pinger, Tracert


class TestPinger(unittest.TestCase):
    """Test ICMP reachability helper."""

    @patch("libs.tools.icmp.find_executable")
    @patch("libs.tools.icmp.os.system")
    def test_01_detects_working_command(self, mock_system, mock_find_executable) -> None:
        """Test nr 01."""
        mock_find_executable.side_effect = lambda cmd: "/usr/bin/fping" if cmd == "fping" else None
        mock_system.return_value = 0

        pinger = Pinger(timeout=2)

        self.assertTrue(pinger.is_alive("127.0.0.1"))
        self.assertEqual(mock_system.call_count, 2)

    @patch("libs.tools.icmp.find_executable", return_value="/usr/bin/ping")
    @patch("libs.tools.icmp.os.system", side_effect=[0, 1])
    def test_02_returns_false_when_host_is_unreachable(
        self, mock_system, mock_find_executable
    ) -> None:
        """Test nr 02."""
        pinger = Pinger(timeout=2)

        self.assertFalse(pinger.is_alive("127.0.0.1"))
        self.assertEqual(mock_system.call_count, 2)

    @patch("libs.tools.icmp.find_executable", return_value=None)
    def test_03_raises_when_no_command_is_available(
        self, mock_find_executable
    ) -> None:
        """Test nr 03."""
        pinger = Pinger()

        with self.assertRaises(ChildProcessError):
            pinger.is_alive("127.0.0.1")


class TestTracert(unittest.TestCase):
    """Test traceroute helper."""

    @patch("libs.tools.icmp.find_executable", return_value="/usr/bin/traceroute")
    @patch("libs.tools.icmp.os.system", return_value=0)
    @patch("libs.tools.icmp.subprocess.Popen")
    def test_01_execute_returns_decoded_lines(
        self, mock_popen, mock_system, mock_find_executable
    ) -> None:
        """Test nr 01."""
        process = MagicMock()
        process.stdout = [b"hop-1\n", b"hop-2\n"]
        mock_popen.return_value.__enter__.return_value = process

        tracer = Tracert()
        tracer._set_data(
            key="__command_found__",
            value={
                "cmd": "traceroute",
                "opts": "-I -q2 -S -e -w1 -n -m 10",
            },
        )

        self.assertEqual(tracer.execute("127.0.0.1"), ["hop-1\n", "hop-2\n"])

    @patch("libs.tools.icmp.find_executable", return_value=None)
    def test_02_raises_when_no_command_is_available(
        self, mock_find_executable
    ) -> None:
        """Test nr 02."""
        tracer = Tracert()

        with self.assertRaises(ChildProcessError):
            tracer.execute("127.0.0.1")


# #[EOF]#######################################################################
