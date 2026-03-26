# -*- coding: UTF-8 -*-
"""
Plugin configuration parsing helpers.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Validate and parse plugin configuration values using schema metadata.
"""

from typing import Any, Dict, List, Optional, Union, Tuple, get_args, get_origin

from inspect import currentframe

from jsktoolbox.basetool import BClasses
from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.logstool import LoggerClient
from jsktoolbox.raisetool import Raise

from libs.templates import PluginConfigField, PluginConfigSchema
from libs.tools import MIntervals


class PluginConfigParser(BClasses):
    """Parse plugin config sections according to `PluginConfigSchema`."""

    # #[STATIC/CLASS METHODS]#########################################################
    @classmethod
    def parse(
        cls,
        config_handler: ConfigTool,
        section: str,
        schema: PluginConfigSchema,
        logs: Optional[LoggerClient] = None,
    ) -> Dict[str, Any]:
        """Parse one config section using the declared schema.

        ### Arguments:
        * config_handler: ConfigTool - Configuration handler bound to the config file.
        * section: str - Section name to parse.
        * schema: PluginConfigSchema - Declared plugin configuration schema.
        * logs: Optional[LoggerClient] - Logger used for non-fatal validation warnings.

        ### Returns:
        Dict[str, Any] - Parsed and validated config values.
        """
        out: Dict[str, Any] = {}
        for field in schema.fields:
            value: Any = cls.__read_value(config_handler, section, field)
            cls.__validate_value(field, value)
            cls.__log_warnings(section, field, value, logs)
            out[field.name] = value
        return out

    # #[PRIVATE METHODS]##############################################################
    @classmethod
    def __build_at_channel_warnings(cls, value: Any) -> List[str]:
        """Return non-fatal warnings for `at_channel` values.

        ### Arguments:
        * value: Any - Parsed field value.

        ### Returns:
        List[str] - Human-readable warnings.
        """
        out: List[str] = []
        if not isinstance(value, list):
            return out

        cron_fields: List[Tuple[str, List[int]]] = [
            ("minute", [0, 59]),
            ("hour", [0, 23]),
            ("day_of_month", [1, 31]),
            ("month", [1, 12]),
            ("day_of_week", [0, 7]),
        ]
        for item in value:
            raw_item: str = str(item)
            if ":" not in raw_item:
                out.append(
                    f"`at_channel` entry '{raw_item}' is missing the required "
                    "`channel:minute;hour;day;month;weekday` separator."
                )
                continue

            channel, cron = raw_item.split(":", 1)
            if not cls.__is_integer(channel):
                out.append(
                    f"`at_channel` entry '{raw_item}' uses a non-integer channel "
                    f"identifier '{channel}'."
                )

            fragments: List[str] = cron.split(";")
            if len(fragments) != 5:
                out.append(
                    f"`at_channel` entry '{raw_item}' must contain exactly five "
                    "cron-like fragments separated by semicolons."
                )
                continue

            for index, field_data in enumerate(cron_fields):
                out.extend(
                    cls.__build_at_fragment_warnings(
                        raw_item=raw_item,
                        field_name=field_data[0],
                        fragment=fragments[index],
                        val_range=field_data[1],
                    )
                )
        return out

    @classmethod
    def __build_at_fragment_warnings(
        cls,
        raw_item: str,
        field_name: str,
        fragment: str,
        val_range: List[int],
    ) -> List[str]:
        """Return warnings for one `at_channel` cron fragment.

        ### Arguments:
        * raw_item: str - Full raw config entry.
        * field_name: str - Cron fragment logical name.
        * fragment: str - Fragment value to inspect.
        * val_range: List[int] - Inclusive allowed range.

        ### Returns:
        List[str] - Human-readable warnings.
        """
        out: List[str] = []
        if fragment == "*":
            return out
        if "*" in fragment:
            out.append(
                f"`at_channel` entry '{raw_item}' uses unsupported wildcard fragment "
                f"'{fragment}' for '{field_name}'; the current scheduler treats any "
                "fragment containing '*' as a full wildcard, so this entry will "
                f"match every allowed {field_name} value."
            )
            return out
        if "/" in fragment:
            out.append(
                f"`at_channel` entry '{raw_item}' uses unsupported step syntax "
                f"'{fragment}' for '{field_name}'."
            )
            return out

        for token in fragment.split("|"):
            if token == "":
                out.append(
                    f"`at_channel` entry '{raw_item}' contains an empty token in "
                    f"'{field_name}'."
                )
                continue
            if "-" in token:
                if token.count("-") != 1:
                    out.append(
                        f"`at_channel` entry '{raw_item}' uses an invalid range "
                        f"token '{token}' for '{field_name}'."
                    )
                    continue
                start_raw, end_raw = token.split("-")
                if not cls.__is_integer(start_raw) or not cls.__is_integer(end_raw):
                    out.append(
                        f"`at_channel` entry '{raw_item}' uses a non-integer range "
                        f"token '{token}' for '{field_name}'."
                    )
                    continue
                start: int = int(start_raw)
                end: int = int(end_raw)
                if start > end:
                    out.append(
                        f"`at_channel` entry '{raw_item}' uses a descending range "
                        f"'{token}' for '{field_name}'."
                    )
                if start not in range(val_range[0], val_range[1] + 1) or end not in range(
                    val_range[0], val_range[1] + 1
                ):
                    out.append(
                        f"`at_channel` entry '{raw_item}' uses an out-of-range "
                        f"token '{token}' for '{field_name}'."
                    )
                continue

            if not cls.__is_integer(token):
                out.append(
                    f"`at_channel` entry '{raw_item}' uses an invalid token "
                    f"'{token}' for '{field_name}'."
                )
                continue

            token_value: int = int(token)
            if token_value not in range(val_range[0], val_range[1] + 1):
                out.append(
                    f"`at_channel` entry '{raw_item}' uses an out-of-range token "
                    f"'{token}' for '{field_name}'."
                )
        return out

    @classmethod
    def __build_message_channel_warnings(cls, value: Any) -> List[str]:
        """Return non-fatal warnings for `message_channel` values.

        ### Arguments:
        * value: Any - Parsed field value.

        ### Returns:
        List[str] - Human-readable warnings.
        """
        out: List[str] = []
        if not isinstance(value, list):
            return out

        for item in value:
            raw_item: str = str(item)
            channel: str = raw_item
            interval: Optional[str] = None
            if ":" in raw_item:
                channel, interval = raw_item.split(":", 1)

            if not cls.__is_integer(channel):
                out.append(
                    f"`message_channel` entry '{raw_item}' uses a non-integer "
                    f"channel identifier '{channel}'."
                )

            if interval is not None:
                try:
                    MIntervals(cls.__name__).convert(interval)
                except Exception as ex:
                    out.append(
                        f"`message_channel` entry '{raw_item}' uses an invalid "
                        f"interval '{interval}'. Exception: {ex}"
                    )
        return out

    @classmethod
    def __build_semantic_warnings(cls, field: PluginConfigField, value: Any) -> List[str]:
        """Return field-specific non-fatal warnings.

        ### Arguments:
        * field: PluginConfigField - Declared field descriptor.
        * value: Any - Parsed field value.

        ### Returns:
        List[str] - Human-readable warnings.
        """
        if value is None:
            return []
        if field.name == "at_channel":
            return cls.__build_at_channel_warnings(value)
        if field.name == "message_channel":
            return cls.__build_message_channel_warnings(value)
        return []

    @classmethod
    def __is_integer(cls, value: str) -> bool:
        """Return whether a string can be converted to `int`.

        ### Arguments:
        * value: str - Raw string value.

        ### Returns:
        bool - `True` when the value is an integer string.
        """
        try:
            int(value)
        except Exception:
            return False
        return True

    @classmethod
    def __log_warnings(
        cls,
        section: str,
        field: PluginConfigField,
        value: Any,
        logs: Optional[LoggerClient],
    ) -> None:
        """Emit non-fatal validation warnings to the logger.

        ### Arguments:
        * section: str - Config section name.
        * field: PluginConfigField - Declared field descriptor.
        * value: Any - Parsed field value.
        * logs: Optional[LoggerClient] - Logger used for warnings.
        """
        if logs is None:
            return None
        for warning in cls.__build_semantic_warnings(field, value):
            logs.message_warning = (
                f"plugin config warning in section '[{section}]', field "
                f"'{field.name}': {warning}"
            )

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
