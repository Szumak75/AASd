"""Base package exposing shared mixin classes through lazy exports."""

from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, Final, List

__all__: List[str] = [
    "AppNameMixin",
    "ComMixin",
    "ConfigMixin",
    "ConfigHandlerMixin",
    "ConfigSectionMixin",
    "DebugMixin",
    "LogsMixin",
    "PluginRuntimeMixin",
    "PluginConfigMixin",
    "ProjectClassMixin",
    "ThProcessorMixin",
    "VerboseMixin",
]

_EXPORTS: Final[Dict[str, str]] = {
    export_name: "libs.base.classes" for export_name in __all__
}

if TYPE_CHECKING:
    from libs.base.classes import (
        AppNameMixin,
        ComMixin,
        ConfigMixin,
        ConfigHandlerMixin,
        ConfigSectionMixin,
        DebugMixin,
        LogsMixin,
        PluginRuntimeMixin,
        PluginConfigMixin,
        ProjectClassMixin,
        ThProcessorMixin,
        VerboseMixin,
    )


def __dir__() -> List[str]:
    """Return package attributes including lazy exports.

    ### Returns:
    List[str] - Sorted package attribute names.
    """
    return sorted(set(globals()) | set(__all__))


def __getattr__(name: str) -> Any:
    """Resolve exported symbols lazily from implementation modules.

    ### Arguments:
    * name: str - Exported attribute name requested from the package.

    ### Returns:
    Any - Exported object loaded from the backing module.

    ### Raises:
    * AttributeError: If the requested name is not exported by the package.
    """
    module_name: str = _EXPORTS.get(name, "")
    if not module_name:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    module = import_module(module_name)
    value: Any = getattr(module, name)
    globals()[name] = value
    return value
