# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 01.12.2023

  Purpose:
"""

import unittest
from typing import List

from libs.com.message import AtChannel


class TestAtChannel(unittest.TestCase):
    """Tests for AtChannel class."""

    def test_01_create_object(self) -> None:
        """Test nr 01."""
        try:
            AtChannel(["1:0;0;7|10|12|13;*;*", "1:0;8|12|16|21;14;*;*"])
        except Exception as ex:
            self.fail(
                f"Creating an AtChannel object resulted in en exception: {ex}"
            )

    def test_02_channels_list(self) -> None:
        """Test nr 02."""
        obj = AtChannel(["1:0;0;7|10|12|13;*;*", "1:0;8|12|16|21;14;*;*"])
        self.assertIsInstance(obj.channels, List)
        self.assertTrue(len(obj.channels) == 1, msg=f"{obj.channels}")

        # self.fail(f"{obj.dump}")


# #[EOF]#######################################################################
