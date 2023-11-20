# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 13.11.2023

  Purpose:
"""

import datetime
import time
import re

from typing import Optional, Dict
from inspect import currentframe

from jsktoolbox.attribtool import NoNewAttributes
from jsktoolbox.raisetool import Raise
from libs.base.classes import BClasses


class DateTime(NoNewAttributes):
    """DateTime class to generate datetime string in various format."""

    @classmethod
    def time_from_seconds(cls, seconds: int) -> str:
        """Generate date/time string with elapsed time, from seconds.

        Example return string:
        '578 days, 16:53:20'
        """
        return str(datetime.timedelta(seconds=seconds))

    @classmethod
    def now(
        cls, tz: Optional[datetime.timezone] = None
    ) -> datetime.datetime:
        """Return datetime.datetime.now() object.

        Argument:
        tz [datetime.timezone] - datetime.timezone.utc for UTC, default None for current set timezone.
        """
        return datetime.datetime.now(tz=tz)

    @classmethod
    @property
    def datetimenow(cls) -> str:
        """Return datetime string in isoformat."""
        return f"{datetime.date.today().isoformat()} {cls.now().strftime('%H:%M:%S')}"

    @classmethod
    @property
    def email_date(cls) -> str:
        """Return email date formatted string."""
        return cls.now(datetime.timezone.utc).strftime(
            "%a, %d %b %Y %H:%M:%S %z"
        )

    @classmethod
    @property
    def mfi_date(cls) -> Dict:
        """Return MFI date formatted dict."""
        now = cls.now()
        return {
            "day": f"{now.strftime('%a %b')} {int(now.strftime('%d')): >2d}",
            "year": now.strftime("%Y"),
        }

    @classmethod
    @property
    def zfs_snapshot_date(cls) -> str:
        """Return datetime string for zfs snapshot name."""
        return cls.now().strftime("%Y%m%d-%H%M%S")


class Timestamp(NoNewAttributes):
    """Timestamp class for geting current timestamp."""

    @classmethod
    @property
    def now(cls) -> int:
        """Return timestamp int."""
        return int(time.time())


class Intervals(BClasses):
    """Intervals converter class."""

    __name = None
    __re = None

    def __init__(self, module_name: str) -> None:
        """Constructor."""
        self.__name = module_name
        self.__re = re.compile(r"(\d+)\s*([wdhms])", re.IGNORECASE)

    def convert(self, value: str) -> int:
        """Convert string value to seconds.

        Arguments:
        value [str] - value to convert, format: (\d)w: weeks, (\d)d: days, (\d)h: hours, (\d)m: minutes, (\d)s: seconds
        """
        match = self.__re.match(value)

        if (match) is None:
            raise Raise.error(
                f"Converting error, given value: '{value}' is in an unknown format.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        var1 = int(match.group(1))
        var2 = 1

        if match.group(2).lower() == "w":
            var2 = 60 * 60 * 24 * 7
        elif match.group(2).lower() == "d":
            var2 = 60 * 60 * 24
        elif match.group(2).lower() == "h":
            var2 = 60 * 60
        elif match.group(2).lower() == "m":
            var2 = 60
        return var1 * var2


# #[EOF]#######################################################################
