# -*- coding: utf-8 -*-
"""
Application identity helpers.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2024-11-06

Purpose: Provide a small container for application identity metadata.
"""

from inspect import currentframe
import platform
import socket
from typing import Optional
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.basetool import BData
from jsktoolbox.raisetool import Raise


class AppName(BData):
    """Store application name and version metadata.

    The class also exposes a derived host name used by modules when building
    logs and outbound messages.
    """

    class __Keys(object, metaclass=ReadOnlyClass):
        """Define internal storage keys for the application identity container."""

        APP_NAME = "app_name"
        APP_VERSION = "app_version"

    def __init__(self, app_name: str, app_version: str) -> None:
        """Initialize the application identity container.

        ### Arguments:
        * app_name: str - Runtime application name.
        * app_version: str - Runtime application version string.
        """
        self._set_data(key=self.__Keys.APP_NAME, value=app_name, set_default_type=str)
        self._set_data(
            key=self.__Keys.APP_VERSION, value=app_version, set_default_type=str
        )

    @property
    def app_name(self) -> str:
        """Return the application name.

        ### Returns:
        str - Configured application name.
        """
        obj: Optional[str] = self._get_data(key=self.__Keys.APP_NAME)
        if obj is None:
            raise Raise.error(
                "Internal error: application name is not set.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        return obj

    @property
    def app_version(self) -> str:
        """Return the application version.

        ### Returns:
        str - Configured application version string.
        """
        obj: Optional[str] = self._get_data(key=self.__Keys.APP_VERSION)
        if obj is None:
            raise Raise.error(
                "Internal error: application version is not set.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        return obj

    @property
    def app_host_name(self) -> str:
        """Return the best available host name for the current machine.

        ### Returns:
        str - Host name resolved from the local platform APIs.
        """
        app = platform.node()
        if app:
            return app
        app = socket.gethostname()
        if app:
            return app
        return "unknown host"


# #[EOF]#######################################################################
