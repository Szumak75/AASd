# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 30.11.2023

  Purpose:
"""

import unittest

from datetime import datetime, timedelta, timezone, tzinfo
from time import time

from libs.tools.datetool import MDateTime, MIntervals


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


# #[EOF]#######################################################################
