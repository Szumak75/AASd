"""Plugin runtime package with lazy exports."""

from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, Final, List

__all__: List[str] = [
    "DispatcherAdapter",
    "NotificationScheduler",
    "PluginHealth",
    "PluginHealthPolicy",
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
    "PluginRestartPolicy",
    "PluginSkip",
    "PluginServiceReport",
    "PluginState",
    "PluginStateSnapshot",
    "PluginSpec",
    "ThPluginMixin",
]

_EXPORTS: Final[Dict[str, str]] = {
    "DispatcherAdapter": "libs.plugins.runtime",
    "NotificationScheduler": "libs.com.message",
    "PluginHealth": "libs.plugins.runtime",
    "PluginHealthPolicy": "libs.plugins.service",
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
    "PluginRestartPolicy": "libs.plugins.service",
    "PluginSkip": "libs.plugins.service",
    "PluginServiceReport": "libs.plugins.service",
    "PluginState": "libs.plugins.runtime",
    "PluginStateSnapshot": "libs.plugins.runtime",
    "PluginSpec": "libs.plugins.runtime",
    "ThPluginMixin": "libs.plugins.mixins",
}

if TYPE_CHECKING:
    from libs.com.message import NotificationScheduler
    from libs.plugins.config import PluginConfigParser
    from libs.plugins.keys import PluginCommonKeys, PluginHostKeys
    from libs.plugins.loader import PluginDefinition, PluginLoader
    from libs.plugins.mixins import ThPluginMixin
    from libs.plugins.service import (
        PluginFailure,
        PluginHealthPolicy,
        PluginRegistryService,
        PluginRestartPolicy,
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
