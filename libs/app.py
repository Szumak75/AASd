# -*- coding: utf-8 -*-
"""
  app.py
  Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 6.11.2024, 15:34:07
  
  Purpose: Application name container class.
"""

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.basetool.data import BData


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys for the class."""

    APP_NAME = "app_name"
    APP_VERSION = "app_version"


class AppName(BData):
    """Application name container class."""

    def __init__(self, app_name: str, app_version: str) -> None:
        """Initialize the class."""
        self._set_data(key=_Keys.APP_NAME, value=app_name, set_default_type=str)
        self._set_data(key=_Keys.APP_VERSION, value=app_version, set_default_type=str)

    @property
    def app_name(self) -> str:
        """Get the application name."""
        return self._get_data(key=_Keys.APP_NAME)  # type: ignore

    @property
    def app_version(self) -> str:
        """Get the application version."""
        return self._get_data(key=_Keys.APP_VERSION)  # type: ignore


# #[EOF]#######################################################################
