# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 01.12.2023

  Purpose:
"""

import unittest
from typing import List

from libs.com.message import AtPriority


class TestAtPriority(unittest.TestCase):
    """Tests for AtPriority class."""

    def test_01_create_object(self):
        """Test nr 01."""
        try:
            AtPriority(["1:0;0;7|10|12|13;*;*", "1:0;8|12|16|21;14;*;*"])
        except Exception as ex:
            self.fail(
                f"Creating an AtPriority object resulted in en exception: {ex}"
            )

    def test_02_priorities_list(self):
        """Test nr 02."""
        obj = AtPriority(["1:0;0;7|10|12|13;*;*", "1:0;8|12|16|21;14;*;*"])
        self.assertIsInstance(obj.priorities, List)
        self.assertTrue(len(obj.priorities) == 1, msg=f"{obj.priorities}")

        # self.fail(f"{obj.dump}")


# #[EOF]#######################################################################
