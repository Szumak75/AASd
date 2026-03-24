# -*- coding: UTF-8 -*-
"""
Communication template plugin configuration keys.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-24

Purpose: Provide plugin-specific config keys for the communication template.
"""

from jsktoolbox.attribtool import ReadOnlyClass


class Keys(object, metaclass=ReadOnlyClass):
    """Define plugin-specific configuration keys."""

    # #[CONSTANTS]####################################################################
    STDOUT_PREFIX: str = "stdout_prefix"


# #[EOF]#######################################################################
