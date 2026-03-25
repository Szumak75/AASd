# -*- coding: UTF-8 -*-
"""
Plugin configuration parsing helpers.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Validate and parse plugin configuration values using schema metadata.
"""

from typing import Any, Dict, List, Optional, Union, get_args, get_origin

from inspect import currentframe

from jsktoolbox.basetool import BClasses
from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.raisetool import Raise

from libs.templates import PluginConfigField, PluginConfigSchema


class PluginConfigParser(BClasses):
    """Parse plugin config sections according to `PluginConfigSchema`."""

    # #[STATIC/CLASS METHODS]#########################################################
    @classmethod
    def parse(
        cls, config_handler: ConfigTool, section: str, schema: PluginConfigSchema
    ) -> Dict[str, Any]:
        """Parse one config section using the declared schema.

        ### Arguments:
        * config_handler: ConfigTool - Configuration handler bound to the config file.
        * section: str - Section name to parse.
        * schema: PluginConfigSchema - Declared plugin configuration schema.

        ### Returns:
        Dict[str, Any] - Parsed and validated config values.
        """
        out: Dict[str, Any] = {}
        for field in schema.fields:
            value: Any = cls.__read_value(config_handler, section, field)
            cls.__validate_value(field, value)
            out[field.name] = value
        return out

    # #[PRIVATE METHODS]##############################################################
    @classmethod
    def __read_value(
        cls, config_handler: ConfigTool, section: str, field: PluginConfigField
    ) -> Any:
        """Read one field value from the config section with alias fallback.

        ### Arguments:
        * config_handler: ConfigTool - Configuration handler bound to the config file.
        * section: str - Section name to parse.
        * field: PluginConfigField - Declared field descriptor.

        ### Returns:
        Any - Parsed raw value or field default.
        """
        names: List[str] = [field.name]
        if field.aliases:
            names.extend(field.aliases)

        for name in names:
            value = config_handler.get(section, name)
            if value is not None:
                return value
        return field.default

    @classmethod
    def __validate_value(cls, field: PluginConfigField, value: Any) -> None:
        """Validate one value against the declared field schema.

        ### Arguments:
        * field: PluginConfigField - Declared field descriptor.
        * value: Any - Parsed field value.

        ### Raises:
        * ValueError: If the value violates the schema definition.
        """
        if value is None:
            if field.nullable:
                return None
            if field.required:
                raise Raise.error(
                    f"Missing required config field: '{field.name}'.",
                    ValueError,
                    cls.__name__,
                    currentframe(),
                )
            return None

        if field.choices and value not in field.choices:
            raise Raise.error(
                f"Config field '{field.name}' does not match allowed choices.",
                ValueError,
                cls.__name__,
                currentframe(),
            )

        if not cls.__matches_declared_type(value, field.field_type):
            raise Raise.error(
                f"Config field '{field.name}' does not match declared type '{field.type_name}'.",
                ValueError,
                cls.__name__,
                currentframe(),
            )

    @classmethod
    def __matches_declared_type(cls, value: Any, declared_type: object) -> bool:
        """Return whether a value matches the declared field type.

        ### Arguments:
        * value: Any - Parsed field value.
        * declared_type: object - Declared schema field type.

        ### Returns:
        bool - `True` when the value matches the declared type.
        """
        origin: Optional[object] = get_origin(declared_type)
        args: Tuple[object, ...] = get_args(declared_type)

        if origin in (list, List):
            if not isinstance(value, list):
                return False
            if not args:
                return True
            subtype = args[0]
            return all(cls.__matches_declared_type(item, subtype) for item in value)

        if origin is Union:
            return any(cls.__matches_declared_type(value, arg) for arg in args)

        if isinstance(declared_type, type):
            return isinstance(value, declared_type)

        return True


# #[EOF]#######################################################################
