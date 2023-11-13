# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 07.11.2023

  Purpose:
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, List


class IRunModule(ABC):
    """Run Module Interface class."""

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
    def stop(self) -> None:
        """Set stop event."""

    @property
    @abstractmethod
    def stopped(self) -> bool:
        """Return stop flag."""

    @classmethod
    @abstractmethod
    def template_module_name(cls) -> str:
        """Return module name for configuration builder."""

    @classmethod
    @abstractmethod
    def template_module_variables(cls) -> List:
        """Return configuration variables template."""

    @property
    @abstractmethod
    def verbose(self) -> bool:
        """Return verbose flag."""


class IComModule(ABC):
    """Communication Module Interface class."""

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
    def stop(self) -> None:
        """Set stop event."""

    @property
    @abstractmethod
    def stopped(self) -> bool:
        """Return stop flag."""

    @classmethod
    @abstractmethod
    def template_module_name(cls) -> str:
        """Return module name for configuration builder."""

    @classmethod
    @abstractmethod
    def template_module_variables(cls) -> List:
        """Return configuration variables template."""

    @property
    @abstractmethod
    def verbose(self) -> bool:
        """Return verbose flag."""


# #[EOF]#######################################################################
