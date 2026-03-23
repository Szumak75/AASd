# -*- coding: UTF-8 -*-
"""
Runtime module interfaces.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-11-07

Purpose: Define abstract interfaces implemented by communication and task modules.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, List

from libs.templates import TemplateConfigItem


class __IModule(ABC):
    """Define the abstract runtime contract shared by all module types."""

    @property
    @abstractmethod
    def debug(self) -> bool:
        """Return the effective debug flag.

        ### Returns:
        bool - Debug flag value.
        """

    @property
    @abstractmethod
    def module_conf(self) -> Optional[Any]:
        """Return the typed module configuration object.

        ### Returns:
        Optional[Any] - Module configuration object or `None`.
        """

    @abstractmethod
    def _apply_config(self) -> bool:
        """Apply runtime configuration to the module instance.

        ### Returns:
        bool - `True` when configuration was applied successfully.
        """

    @abstractmethod
    def run(self) -> None:
        """Run the main module loop."""

    @abstractmethod
    def sleep(self) -> None:
        """Sleep until the next iteration of the main loop."""

    @abstractmethod
    def stop(self) -> None:
        """Request the module to stop."""

    @property
    @abstractmethod
    def _stopped(self) -> bool:
        """Return the stop-event state.

        ### Returns:
        bool - `True` when stop has been requested.
        """

    @property
    @abstractmethod
    def module_stopped(self) -> bool:
        """Return whether the underlying thread finished execution.

        ### Returns:
        bool - `True` when the module thread is stopped.
        """

    @classmethod
    @abstractmethod
    def template_module_name(cls) -> str:
        """Return the module name used by configuration generators.

        ### Returns:
        str - Configuration section name for the module.
        """

    @classmethod
    @abstractmethod
    def template_module_variables(cls) -> List[TemplateConfigItem]:
        """Return the configuration template exposed by the module.

        ### Returns:
        List[TemplateConfigItem] - Configuration template items.
        """

    @property
    @abstractmethod
    def verbose(self) -> bool:
        """Return the effective verbose flag.

        ### Returns:
        bool - Verbose flag value.
        """


class IRunModule(__IModule):
    """Mark the interface implemented by task modules."""


class IComModule(__IModule):
    """Mark the interface implemented by communication modules."""


# #[EOF]#######################################################################
