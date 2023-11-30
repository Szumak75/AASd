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


# #[EOF]#######################################################################
