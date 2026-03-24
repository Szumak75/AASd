# -*- coding: UTF-8 -*-
"""
Plugin discovery and loading helpers.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Discover plugin instances from `plugins_dir` and load `PluginSpec`.
"""

import importlib.util
import sys

from dataclasses import dataclass
from inspect import currentframe
from pathlib import Path
from types import ModuleType
from typing import Callable, List, Set, TypeGuard, cast

from jsktoolbox.basetool import BClasses
from jsktoolbox.raisetool import Raise

from libs.plugins.keys import PluginHostKeys
from libs.plugins.runtime import PluginKind, PluginSpec
from libs.templates import PluginConfigSchema


@dataclass(slots=True)
class PluginDefinition:
    """Describe one discovered plugin instance."""

    instance_name: str
    plugin_path: Path
    spec: PluginSpec


class PluginLoader(BClasses):
    """Discover plugin instances from the configured plugins directory."""

    # #[STATIC/CLASS METHODS]#########################################################
    @classmethod
    def discover(cls, plugins_dir: Path) -> List[PluginDefinition]:
        """Discover plugin instances from `plugins_dir`.

        ### Arguments:
        * plugins_dir: Path - Directory containing plugin instances.

        ### Returns:
        List[PluginDefinition] - Discovered plugin instance definitions.
        """
        out: List[PluginDefinition] = []
        if not plugins_dir.exists() or not plugins_dir.is_dir():
            return out

        for entry in sorted(plugins_dir.iterdir(), key=lambda item: item.name):
            if not (entry.is_dir() or entry.is_symlink()):
                continue
            load_file = entry / "load.py"
            if not load_file.exists():
                continue
            spec = cls.__load_spec(entry.name, load_file)
            out.append(
                PluginDefinition(
                    instance_name=entry.name,
                    plugin_path=entry.resolve(),
                    spec=spec,
                )
            )
        return out

    # #[PRIVATE METHODS]##############################################################
    @classmethod
    def __build_module_name(cls, instance_name: str) -> str:
        """Build a stable synthetic package name for one plugin instance.

        ### Arguments:
        * instance_name: str - Plugin instance name derived from directory entry.

        ### Returns:
        str - Synthetic package name used during plugin loading.
        """
        normalized_name = "".join(
            char if char.isalnum() else "_" for char in instance_name
        )
        return f"aasd_plugin_{normalized_name}"

    @classmethod
    def __ensure_package_module(cls, package_name: str, plugin_path: Path) -> None:
        """Ensure that the synthetic plugin package exists in `sys.modules`.

        ### Arguments:
        * package_name: str - Synthetic package name for the plugin instance.
        * plugin_path: Path - Root path of the plugin instance.
        """
        package_path = str(plugin_path.resolve())
        cached_module = sys.modules.get(package_name)
        if cached_module is not None:
            cached_module.__path__ = [package_path]  # type: ignore[attr-defined]
            return

        package_module = ModuleType(package_name)
        package_module.__file__ = str((plugin_path / "__init__.py").resolve())
        package_module.__package__ = package_name
        package_module.__path__ = [package_path]  # type: ignore[attr-defined]
        sys.modules[package_name] = package_module

    @classmethod
    def __load_spec(cls, instance_name: str, load_file: Path) -> PluginSpec:
        """Load one `PluginSpec` from plugin `load.py`.

        ### Arguments:
        * instance_name: str - Plugin instance name derived from directory entry.
        * load_file: Path - Path to the plugin `load.py`.

        ### Returns:
        PluginSpec - Loaded and validated plugin spec.
        """
        package_name = cls.__build_module_name(instance_name)
        module_name = f"{package_name}.load"
        cls.__ensure_package_module(package_name, load_file.parent)
        module_spec = importlib.util.spec_from_file_location(module_name, load_file)
        if module_spec is None or module_spec.loader is None:
            raise Raise.error(
                f"Cannot load plugin module from '{load_file}'.",
                RuntimeError,
                cls.__name__,
                currentframe(),
            )
        sys.modules.pop(module_name, None)
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[module_name] = module
        try:
            module_spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop(module_name, None)
            raise

        factory_obj: object = getattr(module, "get_plugin_spec", None)
        if factory_obj is None or not callable(factory_obj):
            raise Raise.error(
                f"Plugin '{instance_name}' does not expose callable 'get_plugin_spec'.",
                RuntimeError,
                cls.__name__,
                currentframe(),
            )

        factory: Callable[[], object] = cast(Callable[[], object], factory_obj)
        plugin_spec: object = factory()
        return cls.__validate_spec(instance_name, plugin_spec)

    @classmethod
    def __is_plugin_spec(cls, plugin_spec: object) -> TypeGuard[PluginSpec]:
        """Return whether the provided object is a valid `PluginSpec` instance.

        ### Arguments:
        * plugin_spec: object - Object returned from plugin entry-point.

        ### Returns:
        bool - `True` when `plugin_spec` is an instance of `PluginSpec`.
        """
        return isinstance(plugin_spec, PluginSpec)

    @classmethod
    def __reserved_host_keys(cls) -> Set[str]:
        """Return the set of daemon-reserved plugin configuration keys.

        ### Returns:
        Set[str] - Reserved configuration key names.
        """
        out: Set[str] = set()
        for name, value in PluginHostKeys.__dict__.items():
            if name.startswith("_"):
                continue
            if isinstance(value, str):
                out.add(value)
        return out

    @classmethod
    def __validate_schema(
        cls,
        instance_name: str,
        schema: PluginConfigSchema,
    ) -> None:
        """Validate one plugin configuration schema.

        ### Arguments:
        * instance_name: str - Plugin instance name.
        * schema: PluginConfigSchema - Plugin schema definition.
        """
        used_names: Set[str] = set()
        reserved_host_keys: Set[str] = cls.__reserved_host_keys()

        for field in schema.fields:
            if field.name in reserved_host_keys:
                raise Raise.error(
                    f"Plugin '{instance_name}' uses reserved host key "
                    f"'{field.name}' in config schema.",
                    ValueError,
                    cls.__name__,
                    currentframe(),
                )
            if field.name in used_names:
                raise Raise.error(
                    f"Plugin '{instance_name}' defines duplicate config name "
                    f"'{field.name}'.",
                    ValueError,
                    cls.__name__,
                    currentframe(),
                )
            used_names.add(field.name)

            if field.aliases is None:
                continue
            for alias in field.aliases:
                if alias in reserved_host_keys:
                    raise Raise.error(
                        f"Plugin '{instance_name}' uses reserved host key "
                        f"'{alias}' as config alias.",
                        ValueError,
                        cls.__name__,
                        currentframe(),
                    )
                if alias in used_names:
                    raise Raise.error(
                        f"Plugin '{instance_name}' defines duplicate config "
                        f"name or alias '{alias}'.",
                        ValueError,
                        cls.__name__,
                        currentframe(),
                    )
                used_names.add(alias)

    @classmethod
    def __validate_spec(cls, instance_name: str, plugin_spec: object) -> PluginSpec:
        """Validate the loaded plugin specification.

        ### Arguments:
        * instance_name: str - Plugin instance name.
        * plugin_spec: object - Loaded plugin spec candidate.

        ### Returns:
        PluginSpec - Validated plugin specification.
        """
        if not cls.__is_plugin_spec(plugin_spec):
            raise Raise.error(
                f"Plugin '{instance_name}' did not return PluginSpec.",
                TypeError,
                cls.__name__,
                currentframe(),
            )
        if plugin_spec.plugin_kind not in (
            PluginKind.COMMUNICATION,
            PluginKind.WORKER,
        ):
            raise Raise.error(
                f"Plugin '{instance_name}' returned unsupported plugin kind '{plugin_spec.plugin_kind}'.",
                ValueError,
                cls.__name__,
                currentframe(),
            )
        cls.__validate_schema(
            instance_name=instance_name,
            schema=plugin_spec.config_schema,
        )
        return plugin_spec


# #[EOF]#######################################################################
