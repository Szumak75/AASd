# -*- coding: UTF-8 -*-
"""
Plugin discovery and loading helpers.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Discover plugin instances from `plugins_dir` and load `PluginSpec`.
"""

import importlib.util

from dataclasses import dataclass
from inspect import currentframe
from pathlib import Path
from typing import List

from jsktoolbox.raisetool import Raise

from libs.plugins.runtime import PluginKind, PluginSpec


@dataclass(slots=True)
class PluginDefinition:
    """Describe one discovered plugin instance."""

    instance_name: str
    plugin_path: Path
    spec: PluginSpec


class PluginLoader(object):
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
    def __load_spec(cls, instance_name: str, load_file: Path) -> PluginSpec:
        """Load one `PluginSpec` from plugin `load.py`.

        ### Arguments:
        * instance_name: str - Plugin instance name derived from directory entry.
        * load_file: Path - Path to the plugin `load.py`.

        ### Returns:
        PluginSpec - Loaded and validated plugin spec.
        """
        module_name = f"aasd_plugin_{instance_name}_load"
        module_spec = importlib.util.spec_from_file_location(module_name, load_file)
        if module_spec is None or module_spec.loader is None:
            raise Raise.error(
                f"Cannot load plugin module from '{load_file}'.",
                RuntimeError,
                cls.__name__,
                currentframe(),
            )
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)

        factory = getattr(module, "get_plugin_spec", None)
        if factory is None or not callable(factory):
            raise Raise.error(
                f"Plugin '{instance_name}' does not expose callable 'get_plugin_spec'.",
                RuntimeError,
                cls.__name__,
                currentframe(),
            )

        plugin_spec = factory()
        cls.__validate_spec(instance_name, plugin_spec)
        return plugin_spec

    @classmethod
    def __validate_spec(cls, instance_name: str, plugin_spec: PluginSpec) -> None:
        """Validate the loaded plugin specification.

        ### Arguments:
        * instance_name: str - Plugin instance name.
        * plugin_spec: PluginSpec - Loaded plugin spec.
        """
        if not isinstance(plugin_spec, PluginSpec):
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


# #[EOF]#######################################################################
