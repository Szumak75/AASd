# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 14.11.2023

  Purpose: communication subsystem classes.
"""

from inspect import currentframe
from typing import Optional, Union, Dict, List, Any
from threading import Thread, Event

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.libs.base_th import ThBaseObject

from libs.base.classes import BProjectClass, BCom, BClasses


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys definition class.

    For internal purpose only.
    """

    CMESS = "__message__"
    CLEVEL = "__level__"
    CTO = "__to__"


class Message(BClasses):
    """Communication message container class."""

    def __init__(self):
        """Constructor."""
        self._data[_Keys.CMESS] = []
        self._data[_Keys.CLEVEL] = None
        self._data[_Keys.CTO] = None

    @property
    def level(self) -> Optional[int]:
        """Return level int."""
        return self._data[_Keys.CLEVEL]

    @level.setter
    def level(self, value: int) -> None:
        """Set message communication level."""
        if isinstance(value, int):
            self._data[_Keys.CLEVEL] = value
        else:
            raise Raise.error(
                f"Expected integer type, received '{type(value)}'.",
                TypeError,
                self.c_name,
                currentframe(),
            )

    @property
    def messages(self) -> List:
        """Return messages list."""
        return self._data[_Keys.CMESS]

    @messages.setter
    def messages(self, message: str) -> None:
        """Append message to list."""
        self._data[_Keys.CMESS].append(str(message))

    @property
    def to(self) -> Optional[str]:
        """Return optional to string.

        For example: custom email address.
        """
        return self._data[_Keys.CTO]

    @to.setter
    def to(self, value: str) -> None:
        """Set optional to string."""
        if not isinstance(value, str):
            raise Raise.error(
                f"Expected string type, received '{type(value)}'.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        self._data[_Keys.CTO] = value


class Dispatcher(Thread, ThBaseObject, BCom, BProjectClass):
    """Dispatcher class for assigning messages to different queues."""

    def __init__(self):
        """Constructor."""


# #[EOF]#######################################################################
