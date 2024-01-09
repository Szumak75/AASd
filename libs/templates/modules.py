# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 08.11.2023

  Purpose: Template class for configuration elements.
"""

from inspect import currentframe
from typing import Dict, Union, List, Optional

from jsktoolbox.raisetool import Raise

from libs.base.classes import BClasses


class TemplateConfigItem(BClasses):
    """Template item for config generator."""

    __var: Optional[str] = None
    __val: Optional[Union[str, int, float, bool, List]] = None
    __desc: Optional[str] = None

    def __init__(
        self,
        varname: Optional[str] = None,
        value: Optional[Union[str, int, float, bool, List]] = None,
        desc: Optional[str] = None,
    ) -> None:
        """Constructor."""
        if varname:
            self.varname = varname
        if value is not None:
            self.value = value
        if desc:
            self.desc = desc

    def __repr__(self) -> str:
        """Returns object as string representation."""
        return f"{self._c_name}( varname='{self.varname if self.varname else ''}', value={self.value if self.value is  not None else ''}, desc='{self.desc if self.desc else ''}' )"

    @property
    def desc(self) -> Optional[str]:
        """Return description."""
        return self.__desc

    @desc.setter
    def desc(self, string: str) -> None:
        """Set description."""
        if not isinstance(string, str):
            raise Raise.error(
                f"Expected String type, received: '{type(string)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.__desc = string

    @property
    def value(self) -> Optional[Union[str, int, float, bool, List]]:
        """Return value."""
        return self.__val

    @value.setter
    def value(self, value: Union[str, int, float, bool, List]) -> None:
        """Set value."""
        if not isinstance(value, (str, int, float, bool, list)):
            raise Raise.error(
                f"Expected Union[str, int, float, bool, list] typs, received: '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.__val = value

    @property
    def varname(self) -> Optional[str]:
        """Return varname."""
        return self.__var

    @varname.setter
    def varname(self, name: str) -> None:
        """Set varname."""
        if not isinstance(name, str):
            raise Raise.error(
                f"Expected String type, received: '{type(name)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.__var = name


# #[EOF]#######################################################################
