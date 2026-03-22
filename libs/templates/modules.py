# -*- coding: UTF-8 -*-
"""
Configuration template helpers.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-11-08

Purpose: Provide helper classes for module configuration template definitions.
"""

from typing import Union, List, Optional

from jsktoolbox.basetool import BData
from jsktoolbox.attribtool import ReadOnlyClass


class _Keys(object, metaclass=ReadOnlyClass):
    """Define internal storage keys for configuration template items."""

    DESC: str = "__desc__"
    VALUE: str = "__val__"
    VARNAME: str = "__var__"


class TemplateConfigItem(BData):
    """Represent one configuration template entry exposed by a module."""

    def __init__(
        self,
        varname: Optional[str] = None,
        value: Optional[Union[str, int, float, bool, List]] = None,
        desc: Optional[str] = None,
    ) -> None:
        """Initialize a configuration template item.

        ### Arguments:
        * varname: Optional[str] - Variable name to generate in config output.
        * value: Optional[Union[str, int, float, bool, List]] - Default value.
        * desc: Optional[str] - Human-readable description line.
        """
        if varname:
            self.varname = varname
        if value is not None:
            self.value = value
        if desc:
            self.desc = desc

    def __repr__(self) -> str:
        """Return a debug representation of the template item.

        ### Returns:
        str - Debug-friendly string representation.
        """
        varname: str = self.varname if self.varname else ""
        value: Union[str, int, float, bool, List, str] = (
            self.value if self.value is not None else ""
        )
        desc: str = self.desc if self.desc else ""
        return (
            f"{self._c_name}("
            f" varname='{varname}',"
            f" value={value},"
            f" desc='{desc}'"
            " )"
        )

    @property
    def desc(self) -> Optional[str]:
        """Return the description line.

        ### Returns:
        Optional[str] - Description line or `None`.
        """
        return self._get_data(key=_Keys.DESC, default_value=None)

    @desc.setter
    def desc(self, string: str) -> None:
        """Store the description line.

        ### Arguments:
        * string: str - Description line.
        """
        self._set_data(key=_Keys.DESC, value=string, set_default_type=str)

    @property
    def value(self) -> Optional[Union[str, int, float, bool, List]]:
        """Return the default value stored in the template item.

        ### Returns:
        Optional[Union[str, int, float, bool, List]] - Default value or `None`.
        """
        return self._get_data(key=_Keys.VALUE, default_value=None)

    @value.setter
    def value(self, value: Union[str, int, float, bool, List]) -> None:
        """Store the default value for the template item.

        ### Arguments:
        * value: Union[str, int, float, bool, List] - Default configuration value.
        """
        self._set_data(
            key=_Keys.VALUE,
            value=value,
            set_default_type=Union[str, int, float, bool, List],
        )

    @property
    def varname(self) -> Optional[str]:
        """Return the configuration variable name.

        ### Returns:
        Optional[str] - Variable name or `None`.
        """
        return self._get_data(key=_Keys.VARNAME, default_value=None)

    @varname.setter
    def varname(self, name: str) -> None:
        """Store the configuration variable name.

        ### Arguments:
        * name: str - Configuration variable name.
        """
        self._set_data(
            key=_Keys.VARNAME,
            value=name,
            set_default_type=str,
        )


# #[EOF]#######################################################################
