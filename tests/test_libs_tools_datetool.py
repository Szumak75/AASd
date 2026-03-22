# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 30.11.2023

  Purpose:
"""

import unittest

from datetime import datetime, timedelta
from unittest.mock import patch

from libs.tools import MDateTime, MIntervals


class TestDateTime(unittest.TestCase):
    """DateTime tests."""

    def test_01_datetime_now(self) -> None:
        """Test nr 01."""
        self.assertIsInstance(MDateTime.now(), datetime)

    def test_02_datetime_elapsed_from_seconds(self) -> None:
        """Test nr 02."""
        self.assertIsInstance(MDateTime.elapsed_time_from_seconds(10), timedelta)

    def test_03_datetime_elapsed_from_timestamp(self) -> None:
        """Test nr 03."""
        self.assertIsInstance(MDateTime.elapsed_time_from_timestamp(10), timedelta)

    def test_04_datetime_datetime_from_timestamp(self) -> None:
        """Test nr 04."""
        self.assertIsInstance(MDateTime.datetime_from_timestamp(10), datetime)

    def test_05_date_now(self) -> None:
        """Test nr 05."""
        self.assertRegex(MDateTime.date_now(), r"^\d{4}-\d{2}-\d{2}$")

    def test_06_datetime_now(self) -> None:
        """Test nr 06."""
        self.assertRegex(MDateTime.datetime_now(), r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

    def test_07_email_date(self) -> None:
        """Test nr 07."""
        self.assertRegex(
            MDateTime.email_date(),
            r"^[A-Z][a-z]{2}, \d{2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2}:\d{2} [+-]\d{4}$",
        )

    @patch("libs.tools.datetool.MDateTime.now")
    def test_08_mfi_date(self, mock_now) -> None:
        """Test nr 08."""
        mock_now.return_value = datetime(2026, 3, 22, 12, 34, 56)

        self.assertEqual(
            MDateTime.mfi_date(),
            {
                "day": "Sun Mar 22",
                "year": "2026",
            },
        )

    @patch("libs.tools.datetool.MDateTime.now")
    def test_09_zfs_snapshot_date(self, mock_now) -> None:
        """Test nr 09."""
        mock_now.return_value = datetime(2026, 3, 22, 12, 34, 56)

        self.assertEqual(MDateTime.zfs_snapshot_date(), "20260322-123456")


class TestIntervals(unittest.TestCase):
    """Intervals tests."""

    def setUp(self) -> None:
        self.mi = MIntervals("test")

    def test_01_interval_from_seconds(self) -> None:
        """Test nr 01."""
        self.assertEqual(self.mi.convert("10s"), 10)

    def test_02_interval_from_minutes(self) -> None:
        """Test nr 02."""
        self.assertEqual(self.mi.convert("10m"), 600)

    def test_03_interval_from_hours(self) -> None:
        """Test nr 03."""
        self.assertEqual(self.mi.convert("10h"), 36000)

    def test_04_interval_from_days(self) -> None:
        """Test nr 04."""
        self.assertEqual(self.mi.convert("10d"), 864000)

    def test_05_interval_from_weeks(self) -> None:
        """Test nr 05."""
        self.assertEqual(self.mi.convert("10w"), 6048000)

    def test_06_interval_from_seconds_as_integer(self) -> None:
        """Test nr 06."""
        self.assertEqual(self.mi.convert("30"), 30)

    def test_07_interval_error(self) -> None:
        """Test nr 07."""
        with self.assertRaises(ValueError):
            self.mi.convert("abc")

    def test_08_interval_with_space(self) -> None:
        """Test nr 08."""
        self.assertEqual(self.mi.convert("10 m"), 600)


# #[EOF]#######################################################################
