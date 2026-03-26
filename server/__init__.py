"""AASd - AAS Daemon"""

from typing import Tuple


__author__ = "Jacek 'Szumak' Kotlarski"
__version_info__: Tuple[int, int, int] = (2, 4, 7)
__suffix__: str = "-DEV"
# __suffix__: str = ""
__version__: str = ".".join(map(str, __version_info__)) + __suffix__
