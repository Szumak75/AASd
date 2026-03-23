# -*- coding: UTF-8 -*-
"""
Legacy runtime importer mixin.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-23

Purpose: Preserve the legacy module-path loader used before the plugin runtime.
"""

import os

from inspect import currentframe
from typing import List, Optional

from jsktoolbox.basetool import BData
from jsktoolbox.raisetool import Raise


class ImporterMixin(BData):
    """Preserve the archived legacy loader for `modules.*` imports."""

    # #[PUBLIC METHODS]################################################################
    def import_name_list(self, package: str) -> List:
        """Return importable legacy module file names from the selected package.

        ### Arguments:
        * package: str - Dotted package path relative to the repository root.

        ### Returns:
        List - Sorted list of module names without the `.py` suffix.

        ### Raises:
        * TypeError: If `package` is not a string.
        """
        out = []
        if not isinstance(package, str):
            raise Raise.error(
                f"Expected package name as string type, received: '{type(package)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        dirname: str = os.path.join("./", *package.split("."))
        with os.scandir(dirname) as itr:
            for entry in itr:
                if (
                    entry.name.startswith("m")
                    and entry.name.endswith("y")
                    and entry.name.find(".py") > 0
                ):
                    out.append(entry.name[:-3])
        return sorted(out)

    def import_module(self, package: str, name: str) -> Optional[object]:
        """Import a legacy runtime module class from the selected package.

        ### Arguments:
        * package: str - Dotted package path relative to the repository root.
        * name: str - Module file name without the `.py` suffix.

        ### Returns:
        Optional[object] - Imported class object or `None` when import fails.
        """
        modulename: str = f"{package}.{name}"
        name = f"{name[:2].upper()}{name[2:]}"
        try:
            module = __import__(modulename, globals(), locals(), [name])
        except ImportError:
            return None
        return getattr(module, name)


# #[EOF]#######################################################################
