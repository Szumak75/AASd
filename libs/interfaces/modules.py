# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 07.11.2023

Purpose: Interface classes for modules.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, List

from libs.templates.modules import TemplateConfigItem


class __IModule(ABC):
    """Module Interface class."""

    @property
    @abstractmethod
    def debug(self) -> bool:
        """Return debug flag."""

    @property
    @abstractmethod
    def module_conf(self) -> Optional[Any]:
        """Return module conf object."""

    @abstractmethod
    def _apply_config(self) -> bool:
        """Apply config from module_conf."""

    @abstractmethod
    def run(self) -> None:
        """Main loop."""

    @abstractmethod
    def sleep(self) -> None:
        """Sleep interval for main loop."""

    @abstractmethod
    def stop(self) -> None:
        """Set stop event."""

    @property
    @abstractmethod
    def _stopped(self) -> bool:
        """Return stop event flag."""

    @property
    @abstractmethod
    def module_stopped(self) -> bool:
        """Return stopped status for main process."""

    @classmethod
    @abstractmethod
    def template_module_name(cls) -> str:
        """Return module name for configuration builder."""

    @classmethod
    @abstractmethod
    def template_module_variables(cls) -> List[TemplateConfigItem]:
        """Return configuration variables template."""

    @property
    @abstractmethod
    def verbose(self) -> bool:
        """Return verbose flag."""


class IRunModule(__IModule):
    """Run Module Interface class."""


class IComModule(__IModule):
    """Communication Module Interface class."""


# #[EOF]#######################################################################
