# -*- coding: utf-8 -*-
"""
  test_mzfssnapshot.py
  Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 25.10.2024, 16:30:34
  
  Purpose: 
"""


import unittest
import os
from typing import List, Optional

from modules.run.mzfssnapshot import ZfsData, ZfsProcessor


class TestZfsData(unittest.TestCase):
    """Tests for ZfsData class."""

    def test_01_zfs_data(self) -> None:
        """Test nr 01."""
        data = "tank/iocage/jails/logger/data/logs/2024/01	214411292672	5192832966656	214411292672	/logs/2024/01"
        try:
            zfs_data = ZfsData(data)
        except Exception as e:
            self.fail(e)

        self.assertFalse(zfs_data.error)
        self.assertEqual(zfs_data.volume, "tank/iocage/jails/logger/data/logs/2024/01")
        self.assertEqual(zfs_data.used, 214411292672)
        self.assertEqual(zfs_data.available, 5192832966656)
        self.assertEqual(zfs_data.mount_point, "/logs/2024/01")
        self.assertEqual(zfs_data.volume_root, "tank")
        self.assertIsNone(zfs_data.snapshot_root)
        self.assertIsNone(zfs_data.snapshot_name)

    def test_02_zfs_data(self) -> None:
        """Test nr 02."""
        data = "zroot/iocage/jails/mydb/root/mysql/mysql@20241024015108	17375232	-	5058170880	-"
        try:
            zfs_data = ZfsData(data)
        except Exception as e:
            self.fail(e)

        self.assertFalse(zfs_data.error)
        self.assertIsNotNone(zfs_data.snapshot_root)
        self.assertIsNotNone(zfs_data.snapshot_name)
        self.assertEqual(
            zfs_data.snapshot_root, "zroot/iocage/jails/mydb/root/mysql/mysql"
        )
        self.assertEqual(zfs_data.snapshot_name, "20241024015108")
        self.assertEqual(zfs_data.available, -1)
        self.assertEqual(zfs_data.mount_point, "-")
        self.assertEqual(zfs_data.volume_root, "zroot")


class TestZfsProcessor(unittest.TestCase):
    """Tests for ZfsProcessor class."""

    def test_01_zfs_processor(self) -> None:
        """Test nr 01."""
        sys = os.uname()
        if sys.sysname == "FreeBSD":

            vol1 = "/tmp"  # vol: zroot/tmp
            vol2 = "zroot/tmp2"
            try:
                zp1 = ZfsProcessor(vol1)
                zp2 = ZfsProcessor(vol2)
            except Exception as e:
                self.fail(e)

            self.assertTrue(zp1.check_volume())
            self.assertEqual(zp1.volume, "zroot/tmp")
            self.assertIsNotNone(zp1.messages)
            zp1.clear()

            self.assertFalse(zp2.check_volume())
            self.assertIsNotNone(zp2.messages)
            self.assertTrue(len(zp2.messages), 1)  # type: ignore
            zp2.clear()
            self.assertIsNone(zp2.messages)

    def test_02_get_volume(self) -> None:
        """Test nr 02."""
        sys = os.uname()
        if sys.sysname == "FreeBSD":
            vol1 = "/tmp"  # vol: zroot/tmp
            try:
                zp1 = ZfsProcessor(vol1)
            except Exception as e:
                self.fail(e)

            self.assertTrue(zp1.check_volume())
            self.assertEqual(zp1.volume, "zroot/tmp")
            self.assertIsNotNone(zp1.get_volume())
            try:
                data: Optional[ZfsData] = zp1.get_volume()
            except Exception as e:
                self.fail(e)
            if data:
                self.assertEqual(data.volume, "zroot/tmp")
                self.assertEqual(data.volume_root, "zroot")
            else:
                self.fail("get_volume() returned None")
            try:
                root_data: Optional[ZfsData] = zp1.get_volume(data.volume_root)
            except Exception as e:
                self.fail(e)
            if root_data:
                self.assertEqual(root_data.volume, "zroot")
                self.assertEqual(root_data.volume_root, "zroot")
            else:
                self.fail("get_volume() for 'zroot' returned None")


# #[EOF]#######################################################################
