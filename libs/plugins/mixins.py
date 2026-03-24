# -*- coding: utf-8 -*-
"""
Plugin thread mixins.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-24

Purpose: Provide typed mixins shared by thread-based plugin runtimes.
"""

from queue import Queue
from typing import Optional, TYPE_CHECKING

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.basetool import ThBaseObject

if TYPE_CHECKING:
    from libs.plugins.runtime import (
        PluginContext,
        PluginHealthSnapshot,
        PluginStateSnapshot,
    )


class _Keys(object, metaclass=ReadOnlyClass):
    """Define internal storage keys for thread-based plugin mixins."""

    # #[CONSTANTS]####################################################################
    CONTEXT: str = "__context__"
    HEALTH: str = "__health__"
    QUEUE: str = "__queue__"
    STATE: str = "__state__"


class ThPluginMixin(ThBaseObject):
    """Provide typed attributes shared by thread-based plugin runtimes."""

    # #[PROTECTED PROPERTIES]##########################################################
    @property
    def _context(self) -> Optional["PluginContext"]:
        """Return the plugin runtime context.

        ### Returns:
        Optional[PluginContext] - Runtime context or `None`.
        """
        return self._get_data(key=_Keys.CONTEXT, default_value=None)

    @_context.setter
    def _context(self, value: Optional["PluginContext"]) -> None:
        """Store the plugin runtime context.

        ### Arguments:
        * value: Optional[PluginContext] - Runtime context object or `None`.
        """
        from libs.plugins.runtime import PluginContext

        self._set_data(
            key=_Keys.CONTEXT,
            value=value,
            set_default_type=Optional[PluginContext],
        )

    @property
    def _health(self) -> Optional["PluginHealthSnapshot"]:
        """Return the current health snapshot.

        ### Returns:
        Optional[PluginHealthSnapshot] - Health snapshot or `None`.
        """
        return self._get_data(key=_Keys.HEALTH, default_value=None)

    @_health.setter
    def _health(self, value: Optional["PluginHealthSnapshot"]) -> None:
        """Store the current health snapshot.

        ### Arguments:
        * value: Optional[PluginHealthSnapshot] - Health snapshot object or `None`.
        """
        from libs.plugins.runtime import PluginHealthSnapshot

        self._set_data(
            key=_Keys.HEALTH,
            value=value,
            set_default_type=Optional[PluginHealthSnapshot],
        )

    @property
    def _queue(self) -> Optional[Queue]:
        """Return the plugin-owned communication queue.

        ### Returns:
        Optional[Queue] - Communication queue or `None`.
        """
        return self._get_data(key=_Keys.QUEUE, default_value=None)

    @_queue.setter
    def _queue(self, value: Optional[Queue]) -> None:
        """Store the plugin-owned communication queue.

        ### Arguments:
        * value: Optional[Queue] - Communication queue object or `None`.
        """
        self._set_data(key=_Keys.QUEUE, value=value, set_default_type=Optional[Queue])

    @property
    def _state(self) -> Optional["PluginStateSnapshot"]:
        """Return the current lifecycle snapshot.

        ### Returns:
        Optional[PluginStateSnapshot] - Lifecycle snapshot or `None`.
        """
        return self._get_data(key=_Keys.STATE, default_value=None)

    @_state.setter
    def _state(self, value: Optional["PluginStateSnapshot"]) -> None:
        """Store the current lifecycle snapshot.

        ### Arguments:
        * value: Optional[PluginStateSnapshot] - Lifecycle snapshot object or `None`.
        """
        from libs.plugins.runtime import PluginStateSnapshot

        self._set_data(
            key=_Keys.STATE,
            value=value,
            set_default_type=Optional[PluginStateSnapshot],
        )


# #[EOF]#######################################################################
