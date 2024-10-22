# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 13.11.2023

  Purpose: date and time operations classes.
"""


import re
from re import Pattern, Match

from datetime import date, datetime, timezone
from typing import Dict, Optional
from inspect import currentframe

from jsktoolbox.raisetool import Raise
from jsktoolbox.datetool import DateTime
from jsktoolbox.basetool.data import BData
from jsktoolbox.attribtool import ReadOnlyClass


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys for date and time operations classes."""

    RE: str = "__re__"
    NAME: str = "__name__"


class MDateTime(DateTime):
    """DateTime class to generate datetime string in various format."""

    @classmethod
    def date_now(cls) -> str:
        """Return current date as %Y-%m-%d format."""
        return f"{date.today().isoformat()}"

    @classmethod
    def datetime_now(cls) -> str:
        """Return datetime string in isoformat."""
        return f"{cls.date_now()} {cls.now().strftime('%H:%M:%S')}"

    @classmethod
    def email_date(cls) -> str:
        """Return email date formatted string."""
        return cls.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")

    @classmethod
    def mfi_date(cls) -> Dict:
        """Return MFI date formatted dict."""
        now: datetime = cls.now()
        return {
            "day": f"{now.strftime('%a %b')} {int(now.strftime('%d')): >2d}",
            "year": now.strftime("%Y"),
        }

    @classmethod
    def zfs_snapshot_date(cls) -> str:
        """Return datetime string for zfs snapshot name."""
        return cls.now().strftime("%Y%m%d-%H%M%S")


class MIntervals(BData):
    """Intervals converter class."""

    # __name: str = ""
    # __re: Optional[Pattern[str]] = None

    def __init__(self, module_name: str) -> None:
        """Constructor."""
        self._set_data(key=_Keys.NAME, value=module_name, set_default_type=str)
        self._set_data(
            key=_Keys.RE,
            value=re.compile(r"(\d+)\s*([wdhms])", re.IGNORECASE),
            set_default_type=Pattern[str],
        )

    def convert(self, value: str) -> int:
        """Convert string value to seconds.

        Arguments:
        value [str] - value to convert, format: (d)w: weeks, (d)d: days, (d)h: hours, (d)m: minutes, (d)s: seconds
        """
        _re:Pattern[str]=self._get_data(key=_Keys.RE) # type: ignore
        match: Optional[Match[str]] = _re.match(value)

        if match is None:
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
