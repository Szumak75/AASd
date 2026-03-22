# -*- coding: UTF-8 -*-
"""
Date and interval helpers.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-11-13

Purpose: Provide date formatting helpers and interval conversion utilities.
"""


import re
from re import Pattern, Match

from datetime import date, datetime, timezone
from typing import Dict, Optional
from inspect import currentframe

from jsktoolbox.raisetool import Raise
from jsktoolbox.datetool import DateTime
from jsktoolbox.basetool import BData
from jsktoolbox.attribtool import ReadOnlyClass


class MDateTime(DateTime):
    """Provide project-specific date and time formatting helpers."""

    @classmethod
    def date_now(cls) -> str:
        """Return the current date in ISO format.

        ### Returns:
        str - Current date formatted as `YYYY-MM-DD`.
        """
        return f"{date.today().isoformat()}"

    @classmethod
    def datetime_now(cls) -> str:
        """Return the current local date and time as a compact string.

        ### Returns:
        str - Current date and time formatted as `YYYY-MM-DD HH:MM:SS`.
        """
        return f"{cls.date_now()} {cls.now().strftime('%H:%M:%S')}"

    @classmethod
    def email_date(cls) -> str:
        """Return the current UTC time formatted for email headers.

        ### Returns:
        str - RFC-like email date string.
        """
        return cls.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")

    @classmethod
    def mfi_date(cls) -> Dict:
        """Return a dictionary used by the MFI-oriented date presentation.

        ### Returns:
        Dict - Dictionary with `day` and `year` keys.
        """
        now: datetime = cls.now()
        return {
            "day": f"{now.strftime('%a %b')} {int(now.strftime('%d')): >2d}",
            "year": now.strftime("%Y"),
        }

    @classmethod
    def zfs_snapshot_date(cls) -> str:
        """Return the timestamp string used in ZFS snapshot names.

        ### Returns:
        str - Snapshot-friendly timestamp string.
        """
        return cls.now().strftime("%Y%m%d-%H%M%S")


class MIntervals(BData):
    """Convert human-readable interval definitions to seconds."""

    class __Keys(object, metaclass=ReadOnlyClass):
        """Define internal storage keys for date and interval helpers."""

        RE: str = "__re__"
        NAME: str = "__name__"

    def __init__(self, module_name: str) -> None:
        """Initialize the interval converter.

        ### Arguments:
        * module_name: str - Name of the caller used in error reporting.
        """
        self._set_data(key=self.__Keys.NAME, value=module_name, set_default_type=str)
        self._set_data(
            key=self.__Keys.RE,
            value=re.compile(r"(\d+)\s*([wdhms]*)", re.IGNORECASE),
            set_default_type=Pattern,
        )

    def convert(self, value: str) -> int:
        """Convert string value to seconds.

        ### Arguments:
        * value: str - Value to convert in `w`, `d`, `h`, `m`, or `s` notation.

        ### Returns:
        int - Converted interval in seconds.

        ### Raises:
        * ValueError: If the value cannot be parsed.
        """
        obj: Optional[Pattern[str]] = self._get_data(key=self.__Keys.RE)
        if obj is None:
            raise Raise.error(
                "Internal error: regular expression pattern is not set.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        _re: Pattern[str] = obj
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
