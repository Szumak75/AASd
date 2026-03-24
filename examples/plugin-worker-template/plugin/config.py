# -*- coding: UTF-8 -*-
"""
Worker template plugin configuration keys.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-24

Purpose: Provide plugin-specific config keys for the worker template plugin.
"""

from jsktoolbox.attribtool import ReadOnlyClass


class Keys(object, metaclass=ReadOnlyClass):
    """Define plugin-specific configuration keys."""

    # #[CONSTANTS]####################################################################
    MESSAGE_TEXT: str = "message_text"


# #[EOF]#######################################################################
