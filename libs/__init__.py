"""Shared project libraries package with lazy exports."""

from importlib import import_module
from typing import TYPE_CHECKING, Any, Final

__all__: list[str] = [
    "AppConfig",
    "AppName",
    "Keys",
]

_EXPORTS: Final[dict[str, str]] = {
    "AppConfig": "libs.conf",
    "AppName": "libs.app",
    "Keys": "libs.keys",
}

if TYPE_CHECKING:
    from libs.app import AppName
    from libs.conf import AppConfig
    from libs.keys import Keys


def __dir__() -> list[str]:
    """Return package attributes including lazy exports.

    ### Returns:
    list[str] - Sorted package attribute names.
    """
    return sorted(set(globals()) | set(__all__))


def __getattr__(name: str) -> Any:
    """Resolve exported symbols lazily from first-level modules.

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
