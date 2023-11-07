# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 07.11.2023

  Purpose: module config interface
"""

from abc import ABC, abstractmethod
from typing import Any


class IModuleConfig(ABC):
    """Module Config Interface class."""

    @abstractmethod
    def _get(self, varname: str) -> Any:
        """Get variable from config."""


# #[EOF]#######################################################################
