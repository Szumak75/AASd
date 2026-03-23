"""Plugin runtime package with lazy exports."""

from importlib import import_module
from typing import TYPE_CHECKING, Any, Final

__all__: list[str] = [
    "DispatcherAdapter",
    "PluginHealth",
    "PluginHealthSnapshot",
    "PluginCommonKeys",
    "PluginConfigParser",
    "PluginContext",
    "PluginDefinition",
    "PluginFailure",
    "PluginHostKeys",
    "PluginKind",
    "PluginLoader",
    "PluginRuntime",
    "PluginRegistryService",
    "PluginSkip",
    "PluginServiceReport",
    "PluginState",
    "PluginStateSnapshot",
    "PluginSpec",
]

_EXPORTS: Final[dict[str, str]] = {
    "DispatcherAdapter": "libs.plugins.runtime",
    "PluginHealth": "libs.plugins.runtime",
    "PluginHealthSnapshot": "libs.plugins.runtime",
    "PluginCommonKeys": "libs.plugins.keys",
    "PluginConfigParser": "libs.plugins.config",
    "PluginContext": "libs.plugins.runtime",
    "PluginDefinition": "libs.plugins.loader",
    "PluginFailure": "libs.plugins.service",
    "PluginHostKeys": "libs.plugins.keys",
    "PluginKind": "libs.plugins.runtime",
    "PluginLoader": "libs.plugins.loader",
    "PluginRuntime": "libs.plugins.runtime",
    "PluginRegistryService": "libs.plugins.service",
    "PluginSkip": "libs.plugins.service",
    "PluginServiceReport": "libs.plugins.service",
    "PluginState": "libs.plugins.runtime",
    "PluginStateSnapshot": "libs.plugins.runtime",
    "PluginSpec": "libs.plugins.runtime",
}

if TYPE_CHECKING:
    from libs.plugins.config import PluginConfigParser
    from libs.plugins.keys import PluginCommonKeys, PluginHostKeys
    from libs.plugins.loader import PluginDefinition, PluginLoader
    from libs.plugins.service import (
        PluginFailure,
        PluginRegistryService,
        PluginSkip,
        PluginServiceReport,
    )
    from libs.plugins.runtime import (
        DispatcherAdapter,
        PluginHealth,
        PluginHealthSnapshot,
        PluginContext,
        PluginKind,
        PluginRuntime,
        PluginState,
        PluginStateSnapshot,
        PluginSpec,
    )


def __dir__() -> list[str]:
    """Return package attributes including lazy exports.

    ### Returns:
    list[str] - Sorted package attribute names.
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
