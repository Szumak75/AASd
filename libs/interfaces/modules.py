# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 07.11.2023

  Purpose:
"""

from abc import ABC, abstractmethod
from typing import Any


class IRunModule(ABC):
    """Run Module Interface class."""

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


class IComModule(ABC):
    """Communication Module Interface class."""

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


# #[EOF]#######################################################################
