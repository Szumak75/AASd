# -*- coding: UTF-8 -*-
"""
Plugin configuration schema helpers.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Provide schema-oriented configuration descriptors for plugin API v1.
"""

from typing import Any, List, Optional

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.basetool import BData

from libs.templates.modules import TemplateConfigItem


class _Keys(object, metaclass=ReadOnlyClass):
    """Define internal storage keys for plugin schema helpers."""

    # #[CONSTANTS]####################################################################
    ALIASES: str = "__aliases__"
    CHOICES: str = "__choices__"
    DEFAULT: str = "__default__"
    DEPRECATED: str = "__deprecated__"
    DESCRIPTION: str = "__description__"
    EXAMPLE: str = "__example__"
    FIELDS: str = "__fields__"
    FIELD_TYPE: str = "__field_type__"
    GROUP: str = "__group__"
    NAME: str = "__name__"
    NULLABLE: str = "__nullable__"
    REQUIRED: str = "__required__"
    RESTART_REQUIRED: str = "__restart_required__"
    SECRET: str = "__secret__"
    TITLE: str = "__title__"
    VERSION: str = "__version__"


class PluginConfigField(BData):
    """Describe one semantic configuration field exposed by a plugin."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(
        self,
        name: str,
        field_type: object,
        default: Any,
        required: bool,
        description: str,
        secret: bool = False,
        nullable: bool = False,
        choices: Optional[List[Any]] = None,
        example: Any = None,
        deprecated: bool = False,
        aliases: Optional[List[str]] = None,
        group: Optional[str] = None,
        restart_required: bool = False,
    ) -> None:
        """Initialize a plugin configuration field descriptor.

        ### Arguments:
        * name: str - Configuration variable name.
        * field_type: object - Declared semantic field type.
        * default: Any - Default field value used for config generation.
        * required: bool - `True` when the field must be configured.
        * description: str - Human-readable description of the field.
        * secret: bool - `True` when the value should be treated as sensitive.
        * nullable: bool - `True` when the value may be `None`.
        * choices: Optional[List[Any]] - Optional list of allowed values.
        * example: Any - Optional example value.
        * deprecated: bool - `True` when the field is deprecated.
        * aliases: Optional[List[str]] - Optional list of legacy field aliases.
        * group: Optional[str] - Optional logical field group name.
        * restart_required: bool - `True` when changing the field needs restart.
        """
        self.name = name
        self.field_type = field_type
        self.default = default
        self.required = required
        self.description = description
        self.secret = secret
        self.nullable = nullable
        self.deprecated = deprecated
        self.restart_required = restart_required
        if choices is not None:
            self.choices = choices
        if example is not None:
            self.example = example
        if aliases is not None:
            self.aliases = aliases
        if group is not None:
            self.group = group

    # #[PUBLIC PROPERTIES]############################################################
    @property
    def aliases(self) -> Optional[List[str]]:
        """Return the list of legacy aliases for the field.

        ### Returns:
        Optional[List[str]] - Legacy aliases or `None`.
        """
        return self._get_data(key=_Keys.ALIASES, default_value=None)

    @aliases.setter
    def aliases(self, value: List[str]) -> None:
        """Store the list of legacy aliases for the field.

        ### Arguments:
        * value: List[str] - Legacy aliases for the field.
        """
        self._set_data(key=_Keys.ALIASES, value=value, set_default_type=List[str])

    @property
    def choices(self) -> Optional[List[Any]]:
        """Return the optional list of allowed values.

        ### Returns:
        Optional[List[Any]] - Allowed values or `None`.
        """
        return self._get_data(key=_Keys.CHOICES, default_value=None)

    @choices.setter
    def choices(self, value: List[Any]) -> None:
        """Store the optional list of allowed values.

        ### Arguments:
        * value: List[Any] - Allowed values.
        """
        self._set_data(key=_Keys.CHOICES, value=value, set_default_type=List)

    @property
    def default(self) -> Any:
        """Return the default field value.

        ### Returns:
        Any - Default value used for config generation.
        """
        return self._get_data(key=_Keys.DEFAULT, default_value=None)

    @default.setter
    def default(self, value: Any) -> None:
        """Store the default field value.

        ### Arguments:
        * value: Any - Default value used for config generation.
        """
        self._set_data(key=_Keys.DEFAULT, value=value)

    @property
    def deprecated(self) -> bool:
        """Return the deprecation flag.

        ### Returns:
        bool - `True` when the field is deprecated.
        """
        out: Optional[bool] = self._get_data(key=_Keys.DEPRECATED, default_value=False)
        if out is None:
            return False
        return out

    @deprecated.setter
    def deprecated(self, value: bool) -> None:
        """Store the deprecation flag.

        ### Arguments:
        * value: bool - Deprecation flag.
        """
        self._set_data(key=_Keys.DEPRECATED, value=value, set_default_type=bool)

    @property
    def description(self) -> str:
        """Return the human-readable field description.

        ### Returns:
        str - Field description.
        """
        out: Optional[str] = self._get_data(key=_Keys.DESCRIPTION, default_value=None)
        if out is None:
            return ""
        return out

    @description.setter
    def description(self, value: str) -> None:
        """Store the human-readable field description.

        ### Arguments:
        * value: str - Field description.
        """
        self._set_data(key=_Keys.DESCRIPTION, value=value, set_default_type=str)

    @property
    def example(self) -> Any:
        """Return the optional example field value.

        ### Returns:
        Any - Example value or `None`.
        """
        return self._get_data(key=_Keys.EXAMPLE, default_value=None)

    @example.setter
    def example(self, value: Any) -> None:
        """Store the optional example field value.

        ### Arguments:
        * value: Any - Example value.
        """
        self._set_data(key=_Keys.EXAMPLE, value=value)

    @property
    def field_type(self) -> object:
        """Return the declared semantic field type.

        ### Returns:
        object - Declared field type.
        """
        out: Optional[object] = self._get_data(key=_Keys.FIELD_TYPE, default_value=None)
        if out is None:
            return object
        return out

    @field_type.setter
    def field_type(self, value: object) -> None:
        """Store the declared semantic field type.

        ### Arguments:
        * value: object - Declared field type.
        """
        self._set_data(key=_Keys.FIELD_TYPE, value=value)

    @property
    def group(self) -> Optional[str]:
        """Return the optional logical field group.

        ### Returns:
        Optional[str] - Group name or `None`.
        """
        return self._get_data(key=_Keys.GROUP, default_value=None)

    @group.setter
    def group(self, value: str) -> None:
        """Store the optional logical field group.

        ### Arguments:
        * value: str - Group name.
        """
        self._set_data(key=_Keys.GROUP, value=value, set_default_type=str)

    @property
    def name(self) -> str:
        """Return the configuration variable name.

        ### Returns:
        str - Variable name.
        """
        out: Optional[str] = self._get_data(key=_Keys.NAME, default_value=None)
        if out is None:
            return ""
        return out

    @name.setter
    def name(self, value: str) -> None:
        """Store the configuration variable name.

        ### Arguments:
        * value: str - Variable name.
        """
        self._set_data(key=_Keys.NAME, value=value, set_default_type=str)

    @property
    def nullable(self) -> bool:
        """Return the nullable flag.

        ### Returns:
        bool - `True` when the field accepts `None`.
        """
        out: Optional[bool] = self._get_data(key=_Keys.NULLABLE, default_value=False)
        if out is None:
            return False
        return out

    @nullable.setter
    def nullable(self, value: bool) -> None:
        """Store the nullable flag.

        ### Arguments:
        * value: bool - Nullable flag.
        """
        self._set_data(key=_Keys.NULLABLE, value=value, set_default_type=bool)

    @property
    def required(self) -> bool:
        """Return the required flag.

        ### Returns:
        bool - `True` when the field is required.
        """
        out: Optional[bool] = self._get_data(key=_Keys.REQUIRED, default_value=False)
        if out is None:
            return False
        return out

    @required.setter
    def required(self, value: bool) -> None:
        """Store the required flag.

        ### Arguments:
        * value: bool - Required flag.
        """
        self._set_data(key=_Keys.REQUIRED, value=value, set_default_type=bool)

    @property
    def restart_required(self) -> bool:
        """Return the restart-required flag.

        ### Returns:
        bool - `True` when changing the field requires restart.
        """
        out: Optional[bool] = self._get_data(
            key=_Keys.RESTART_REQUIRED, default_value=False
        )
        if out is None:
            return False
        return out

    @restart_required.setter
    def restart_required(self, value: bool) -> None:
        """Store the restart-required flag.

        ### Arguments:
        * value: bool - Restart-required flag.
        """
        self._set_data(
            key=_Keys.RESTART_REQUIRED, value=value, set_default_type=bool
        )

    @property
    def secret(self) -> bool:
        """Return the secret flag.

        ### Returns:
        bool - `True` when the field contains sensitive data.
        """
        out: Optional[bool] = self._get_data(key=_Keys.SECRET, default_value=False)
        if out is None:
            return False
        return out

    @secret.setter
    def secret(self, value: bool) -> None:
        """Store the secret flag.

        ### Arguments:
        * value: bool - Secret flag.
        """
        self._set_data(key=_Keys.SECRET, value=value, set_default_type=bool)

    @property
    def type_name(self) -> str:
        """Return a readable name of the declared field type.

        ### Returns:
        str - Human-readable field type name.
        """
        field_type: object = self.field_type
        if hasattr(field_type, "__name__"):
            return str(getattr(field_type, "__name__"))
        return str(field_type)


class PluginConfigSchema(BData):
    """Describe the full configuration schema of a plugin instance."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(
        self,
        title: str,
        fields: List[PluginConfigField],
        description: Optional[str] = None,
        version: int = 1,
    ) -> None:
        """Initialize the plugin configuration schema descriptor.

        ### Arguments:
        * title: str - Human-readable schema title.
        * fields: List[PluginConfigField] - Declared plugin configuration fields.
        * description: Optional[str] - Optional schema description.
        * version: int - Schema version number.
        """
        self.title = title
        self.fields = fields
        self.version = version
        if description is not None:
            self.description = description

    # #[PUBLIC PROPERTIES]############################################################
    @property
    def description(self) -> Optional[str]:
        """Return the optional schema description.

        ### Returns:
        Optional[str] - Schema description or `None`.
        """
        return self._get_data(key=_Keys.DESCRIPTION, default_value=None)

    @description.setter
    def description(self, value: str) -> None:
        """Store the optional schema description.

        ### Arguments:
        * value: str - Schema description.
        """
        self._set_data(key=_Keys.DESCRIPTION, value=value, set_default_type=str)

    @property
    def fields(self) -> List[PluginConfigField]:
        """Return the list of declared configuration fields.

        ### Returns:
        List[PluginConfigField] - Configuration field descriptors.
        """
        out: Optional[List[PluginConfigField]] = self._get_data(
            key=_Keys.FIELDS, default_value=None
        )
        if out is None:
            return []
        return out

    @fields.setter
    def fields(self, value: List[PluginConfigField]) -> None:
        """Store the list of declared configuration fields.

        ### Arguments:
        * value: List[PluginConfigField] - Configuration field descriptors.
        """
        self._set_data(key=_Keys.FIELDS, value=value, set_default_type=List)

    @property
    def title(self) -> str:
        """Return the schema title.

        ### Returns:
        str - Schema title.
        """
        out: Optional[str] = self._get_data(key=_Keys.TITLE, default_value=None)
        if out is None:
            return ""
        return out

    @title.setter
    def title(self, value: str) -> None:
        """Store the schema title.

        ### Arguments:
        * value: str - Schema title.
        """
        self._set_data(key=_Keys.TITLE, value=value, set_default_type=str)

    @property
    def version(self) -> int:
        """Return the schema version.

        ### Returns:
        int - Schema version.
        """
        out: Optional[int] = self._get_data(key=_Keys.VERSION, default_value=1)
        if out is None:
            return 1
        return out

    @version.setter
    def version(self, value: int) -> None:
        """Store the schema version.

        ### Arguments:
        * value: int - Schema version.
        """
        self._set_data(key=_Keys.VERSION, value=value, set_default_type=int)


class PluginConfigSchemaRenderer(object):
    """Render plugin configuration schemas into legacy template rows."""

    # #[STATIC/CLASS METHODS]#########################################################
    @classmethod
    def render(cls, schema: PluginConfigSchema) -> List[TemplateConfigItem]:
        """Render a schema into `TemplateConfigItem` rows.

        ### Arguments:
        * schema: PluginConfigSchema - Schema descriptor to render.

        ### Returns:
        List[TemplateConfigItem] - Template rows describing the schema.
        """
        out: List[TemplateConfigItem] = []
        out.append(TemplateConfigItem(desc=schema.title))
        if schema.description:
            out.append(TemplateConfigItem(desc=schema.description))
        for field in schema.fields:
            out.append(TemplateConfigItem(desc=cls.__build_description(field)))
            if field.example is not None:
                out.append(TemplateConfigItem(desc=f"example: {field.example}"))
            out.append(TemplateConfigItem(varname=field.name, value=field.default))
        return out

    # #[PRIVATE METHODS]##############################################################
    @staticmethod
    def __build_description(field: PluginConfigField) -> str:
        """Build a human-readable description row for a schema field.

        ### Arguments:
        * field: PluginConfigField - Schema field descriptor.

        ### Returns:
        str - Rendered description line.
        """
        attrs: List[str] = []
        if field.required:
            attrs.append("required")
        else:
            attrs.append("optional")
        if field.nullable:
            attrs.append("nullable")
        if field.secret:
            attrs.append("secret")
        if field.restart_required:
            attrs.append("restart-required")
        if field.deprecated:
            attrs.append("deprecated")
        attrs_text: str = ", ".join(attrs)
        return (
            f"{field.name} [{field.type_name}] - {field.description}"
            f" ({attrs_text})"
        )


# #[EOF]#######################################################################
