# -*- coding: utf-8 -*-
"""
Plugin thread mixins.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-24

Purpose: Provide typed mixins shared by thread-based plugin runtimes.
"""

from typing import Any

from jsktoolbox.basetool import ThBaseObject


class ThPluginMixin(ThBaseObject):
    """Provide typed attributes shared by thread-based plugin runtimes."""

    # #[PROTECTED PROPERTIES]##########################################################
    _context: Any = None
    _health: Any = None
    _queue: Any = None
    _state: Any = None


# #[EOF]#######################################################################
