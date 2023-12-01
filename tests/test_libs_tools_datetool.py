# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 30.11.2023

  Purpose:
"""

import unittest

from datetime import datetime, timedelta, timezone, tzinfo
from time import time

from libs.tools.datetool import DateTime


class TestDateTime(unittest.TestCase):
    """DateTime tests."""

    def test_01_datetime_now(self):
        """Test nr 01."""
        self.assertIsInstance(DateTime.now(), datetime)

    def test_02_datetime_elapsed_from_seconds(self):
        """Test nr 02."""
        self.assertIsInstance(
            DateTime.elapsed_time_from_seconds(10), timedelta
        )

    def test_03_datetime_elapsed_from_timestamp(self):
        """Test nr 03."""
        self.assertIsInstance(
            DateTime.elapsed_time_from_timestamp(10), timedelta
        )

    def test_04_datetime_datetime_from_timestamp(self):
        """Test nr 04."""
        self.assertIsInstance(DateTime.datetime_from_timestamp(10), datetime)


# #[EOF]#######################################################################
