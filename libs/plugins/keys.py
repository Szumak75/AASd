# -*- coding: UTF-8 -*-
"""
Plugin configuration key constants.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Provide public constant classes for shared plugin configuration keys.
"""

from jsktoolbox.attribtool import ReadOnlyClass


class PluginCommonKeys(object, metaclass=ReadOnlyClass):
    """Expose shared plugin configuration keys used across plugin types."""

    # #[CONSTANTS]####################################################################
    CHANNEL: str = "channel"
    MESSAGE_CHANNEL: str = "message_channel"
    SLEEP_PERIOD: str = "sleep_period"


class PluginHostKeys(object, metaclass=ReadOnlyClass):
    """Expose daemon-reserved plugin configuration keys."""

    # #[CONSTANTS]####################################################################
    AUTOSTART: str = "autostart"
    RESTART_POLICY: str = "restart_policy"
    START_DELAY: str = "start_delay"


# #[EOF]#######################################################################
