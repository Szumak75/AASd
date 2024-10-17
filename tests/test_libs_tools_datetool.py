# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 30.11.2023

  Purpose:
"""

import unittest

from datetime import datetime, timedelta, timezone, tzinfo
from time import time

from libs.tools.datetool import MDateTime


class TestDateTime(unittest.TestCase):
    """DateTime tests."""

    def test_01_datetime_now(self) -> None:
        """Test nr 01."""
        self.assertIsInstance(MDateTime.now(), datetime)

    def test_02_datetime_elapsed_from_seconds(self) -> None:
        """Test nr 02."""
        self.assertIsInstance(
            MDateTime.elapsed_time_from_seconds(10), timedelta
        )

    def test_03_datetime_elapsed_from_timestamp(self) -> None:
        """Test nr 03."""
        self.assertIsInstance(
            MDateTime.elapsed_time_from_timestamp(10), timedelta
        )

    def test_04_datetime_datetime_from_timestamp(self) -> None:
        """Test nr 04."""
        self.assertIsInstance(
            MDateTime.datetime_from_timestamp(10), datetime
        )


# #[EOF]#######################################################################
