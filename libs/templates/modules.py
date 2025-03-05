# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 08.11.2023

Purpose: Template class for configuration elements.
"""

from typing import Union, List, Optional

from jsktoolbox.basetool.data import BData
from jsktoolbox.attribtool import ReadOnlyClass


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys for configuration elements."""

    DESC: str = "__desc__"
    VALUE: str = "__val__"
    VARNAME: str = "__var__"


class TemplateConfigItem(BData):
    """Template item for config generator."""

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
        return self._get_data(key=_Keys.DESC, default_value=None)

    @desc.setter
    def desc(self, string: str) -> None:
        """Set description."""
        self._set_data(key=_Keys.DESC, value=string, set_default_type=str)

    @property
    def value(self) -> Optional[Union[str, int, float, bool, List]]:
        """Return value."""
        return self._get_data(key=_Keys.VALUE, default_value=None)

    @value.setter
    def value(self, value: Union[str, int, float, bool, List]) -> None:
        """Set value."""
        self._set_data(
            key=_Keys.VALUE,
            value=value,
            set_default_type=Union[str, int, float, bool, List],
        )

    @property
    def varname(self) -> Optional[str]:
        """Return varname."""
        return self._get_data(key=_Keys.VARNAME, default_value=None)

    @varname.setter
    def varname(self, name: str) -> None:
        """Set varname."""
        self._set_data(
            key=_Keys.VARNAME,
            value=name,
            set_default_type=str,
        )


# #[EOF]#######################################################################
