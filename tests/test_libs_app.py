# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-24

Purpose: Provide regression coverage for the application identity helper.
"""

import unittest

from unittest.mock import patch

from libs.app import AppName


class TestLibsApp(unittest.TestCase):
    """Cover `AppName` accessors and fallback behavior."""

    # #[PUBLIC METHODS]################################################################
    def test_01_app_host_name_should_use_socket_hostname_fallback(self) -> None:
        """Use `socket.gethostname()` when `platform.node()` is empty."""
        obj = AppName(app_name="AASd", app_version="2.3.1-DEV")

        with patch("libs.app.platform.node", return_value=""), patch(
            "libs.app.socket.gethostname",
            return_value="fallback-host",
        ):
            self.assertEqual(obj.app_host_name, "fallback-host")

    def test_02_app_host_name_should_return_unknown_host_when_all_sources_fail(
        self,
    ) -> None:
        """Return the final host-name fallback when platform APIs are empty."""
        obj = AppName(app_name="AASd", app_version="2.3.1-DEV")

        with patch("libs.app.platform.node", return_value=""), patch(
            "libs.app.socket.gethostname",
            return_value="",
        ):
            self.assertEqual(obj.app_host_name, "unknown host")

    def test_03_app_name_should_raise_when_internal_value_is_missing(self) -> None:
        """Raise `ValueError` when the stored application name is missing."""
        obj = AppName(app_name="AASd", app_version="2.3.1-DEV")
        obj._delete_data("app_name")

        with self.assertRaises(ValueError):
            _ = obj.app_name

    def test_04_app_version_should_raise_when_internal_value_is_missing(self) -> None:
        """Raise `ValueError` when the stored application version is missing."""
        obj = AppName(app_name="AASd", app_version="2.3.1-DEV")
        obj._delete_data("app_version")

        with self.assertRaises(ValueError):
            _ = obj.app_version


# #[EOF]#######################################################################
