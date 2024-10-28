# -*- coding: utf-8 -*-
"""
  mzfssnapshot.py
  Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 24.10.2024, 09:58:51
  
  Purpose: 
"""

import time
import subprocess
import re
import os
from inspect import currentframe
from typing import Dict, List, Optional, Any, Union
from threading import Thread, Event
from queue import Queue

from jsktoolbox.basetool.threads import ThBaseObject
from jsktoolbox.basetool.data import BData
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.datetool import Timestamp

from libs.base.classes import BModule
from libs.interfaces.modules import IRunModule
from libs.base.classes import BModuleConfig
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart, Channel
from libs.tools.datetool import MDateTime, MIntervals


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    S_FREE_SPACE: str = "min_free_space"
    S_INTERVAL: str = "snapshot_interval"
    S_MAX_COUNT: str = "max_snapshot_count"
    S_VOLUMES: str = "volumes"

    ZP_VOLUME: str = "__zfs_volume__"
    ZP_ROOT_VOLUME: str = "__zfs_root_volume__"
    ZP_MESSAGE: str = "__messages__"

    ZD_DATA: str = "__zfs_data__"
    ZD_ERROR: str = "__zfs_error__"


class _ModuleConf(BModuleConfig):
    """Module Config private class."""

    @property
    def min_free_space(self) -> Optional[int]:
        """Minimum free space in percent."""
        var = self._get(varname=_Keys.S_FREE_SPACE)
        if var is not None and not isinstance(var, int):
            raise Raise.error(
                "Expected integer value for min_free_space",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def snapshot_interval(self) -> Optional[str]:
        """Snapshot interval."""
        var = self._get(varname=_Keys.S_INTERVAL)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected string value for snapshot_interval",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def max_snapshot_count(self) -> Optional[int]:
        """Maximum snapshot count."""
        var = self._get(varname=_Keys.S_MAX_COUNT)
        if var is not None and not isinstance(var, int):
            raise Raise.error(
                "Expected integer value for max_snapshot_count",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def volumes(self) -> Optional[List[str]]:
        """List of ZFS volumes."""
        var = self._get(varname=_Keys.S_VOLUMES)
        if var is not None and not isinstance(var, List):
            raise Raise.error(
                "Expected list value for ZFS volumes",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var


class ZfsData(BData):
    """ZFS data."""

    def __init__(self, data: str) -> None:
        """Initialize ZFS data."""
        self._set_data(key=_Keys.ZD_DATA, value={}, set_default_type=Dict)
        self._set_data(
            key=_Keys.ZD_ERROR, value=self.__parser(data), set_default_type=bool
        )

    @property
    def __data(self) -> Dict[str, str]:
        """Data."""
        return self._get_data(key=_Keys.ZD_DATA)  # type: ignore

    @property
    def volume_root(self) -> Optional[str]:
        """Root of the volume."""
        if self.volume:
            tmp: List[str] = self.volume.split(os.path.sep)
            if len(tmp) > 0:
                return tmp[0]
        return None

    @property
    def volume(self) -> Optional[str]:
        """ZFS volume."""
        if self.__data:
            return self.__data["volume"]
        return None

    @property
    def used(self) -> Optional[int]:
        """Used space."""
        if self.__data:
            return int(self.__data["used"]) if self.__data["used"] != "-" else -1
        return None

    @property
    def available(self) -> Optional[int]:
        """Available space."""
        if self.__data:
            return (
                int(self.__data["available"]) if self.__data["available"] != "-" else -1
            )
        return None

    @property
    def mount_point(self) -> Optional[str]:
        """ZFS  mountpoint."""
        if self.__data:
            return self.__data["mount_point"]
        return None

    @property
    def snapshot_root(self) -> Optional[str]:
        """ZFS snapshot root."""
        if self.__data:
            return (
                self.__data["snapshot_root"] if "snapshot_root" in self.__data else None
            )
        return None

    @property
    def snapshot_name(self) -> Optional[str]:
        """ZFS snapshot name."""
        if self.__data:
            return (
                self.__data["snapshot_name"] if "snapshot_name" in self.__data else None
            )
        return None

    def __parser(self, data: str) -> bool:
        """Parse ZFS data."""
        pa: re.Pattern[str] = re.compile(r"^(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+(\S+)$")
        pa_snap: re.Pattern[str] = re.compile(r"(\S+)@([\d]{14})")
        match: Optional[re.Match[str]] = pa.match(data)
        if match:
            vol: Dict[str, str] = {}
            vol["volume"] = match.group(1)
            vol["used"] = match.group(2)
            vol["available"] = match.group(3)
            vol["mount_point"] = match.group(4)
            match_snap: Optional[re.Match[str]] = pa_snap.match(vol["volume"])
            if match_snap:
                vol["snapshot_root"] = match_snap.group(1)
                vol["snapshot_name"] = match_snap.group(2)
            self.__data.update(vol)
            return True
        return False

    @property
    def error(self) -> bool:
        """ZFS data error."""
        return not self._get_data(key=_Keys.ZD_ERROR)


class ZfsProcessor(BData):
    """ZFS processor."""

    def __init__(self, volume: str) -> None:
        """Initialize ZFS processor."""
        # volume to  process
        self._set_data(key=_Keys.ZP_VOLUME, value=volume, set_default_type=str)
        # messages container
        self._set_data(key=_Keys.ZP_MESSAGE, value=[], set_default_type=List)

    def check_volume(self) -> bool:
        """Check if zfs volume exists."""
        # check if variable is correct
        if not self.__volume:
            self.__messages.append("invalid volume received as empty string")
            return False
        # check if volume exists
        with subprocess.Popen(
            ["zfs", "list", "-Hp", self.__volume],
            stdout=subprocess.PIPE,
            env={"PATH": "/sbin"},
        ) as proc:
            # process output
            if proc.stdout:
                for line in proc.stdout:
                    if line:
                        tmp = ZfsData(line.decode("utf-8"))
                        if tmp.error:
                            self.__messages.append(
                                f"Invalid zfs volume: {self.__volume}"
                            )
                            return False
                        # check  if volume is proper
                        if (
                            tmp.volume != self.__volume
                            and tmp.mount_point == self.__volume
                        ):
                            self._set_data(key=_Keys.ZP_VOLUME, value=tmp.volume)
                            self.__messages.append(
                                f"Volume updated to: {self.__volume}"
                            )
                        return True
        self.__messages.append(f"ZFS volume is missing: {self.__volume}")
        return False

    def clear(self) -> None:
        """Clear messages."""
        if self.__messages:
            self.__messages.clear()

    @property
    def __volume(self) -> str:
        """ZFS volume."""
        return self._get_data(key=_Keys.ZP_VOLUME)  # type: ignore

    @property
    def __messages(self) -> List[str]:
        """List of messages."""
        return self._get_data(key=_Keys.ZP_MESSAGE)  # type: ignore

    @property
    def messages(self) -> Optional[List[str]]:
        """Return messages list."""
        msg = self.__messages
        if msg:
            return msg
        # if list is empty return None
        return None


class MZfssnapshot(Thread, ThBaseObject, BModule, IRunModule):
    """MZfssnapshot module."""

    def __init__(
        self,
        conf: ConfigTool,
        qlog: LoggerQueue,
        qcom: Queue,
        verbose: bool = False,
        debug: bool = False,
    ) -> None:
        """Constructor."""
        # Thread initialization
        Thread.__init__(self, name=self._c_name)
        self._stop_event = Event()
        self.daemon = True
        self.sleep_period = 5.0

        # configuration section name
        self._section = self._c_name
        self._cfh = conf
        self._module_conf = _ModuleConf(self._cfh, self._section)

        # logging level
        self._debug = debug
        self._verbose = verbose

        # logger client initialization
        self.logs = LoggerClient(queue=qlog, name=self._c_name)

        # communication queue
        self.qcom = qcom

    def _apply_config(self) -> bool:
        """Apply config from module_conf"""
        if self.module_conf is None:
            return False

        try:
            if self.module_conf.sleep_period:
                self.sleep_period = self.module_conf.sleep_period
        except Exception as ex:
            self.logs.message_critical = f"{ex}"
            return False
        return True

    def run(self) -> None:
        """Main loop."""
        self.logs.message_notice = "starting..."

        if self.module_conf is None or self.module_conf.message_channel is None:
            return None

        # initialization local variables
        channel = Channel(self.module_conf.message_channel)

        # initialization variables from config file
        if not self._apply_config():
            self.logs.message_error = "configuration error."
            return

        if self.debug:
            self.logs.message_debug = "configuration processing complete"
            self.logs.message_debug = "entering to the main loop"

        # starting module loop
        while not self._stopped:
            # TODO: not implemented
            # TODO: do something, build a message if necessary, put it in the qcom queue

            # sleep time
            self.sleep()

        # exiting from loop
        self.logs.message_notice = "exit"

    def sleep(self) -> None:
        """Sleep interval for main loop."""
        sleep_break: float = Timestamp.now() + self.sleep_period
        while not self._stopped and sleep_break > Timestamp.now():
            time.sleep(0.2)

    def stop(self) -> None:
        """Set stop event."""
        if self._debug:
            self.logs.message_debug = "stop signal received"
        if self._stop_event:
            self._stop_event.set()

    @property
    def _stopped(self) -> bool:
        """Return stop flag."""
        if self._stop_event:
            return self._stop_event.is_set()
        return True

    @property
    def module_stopped(self) -> bool:
        """Return stop flag."""
        return self._is_stopped  # type: ignore

    @property
    def debug(self) -> bool:
        """Return debug flag."""
        if self._debug is not None:
            return self._debug
        return False

    @property
    def verbose(self) -> bool:
        """Return verbose flag."""
        return self._verbose

    @property
    def module_conf(self) -> Optional[_ModuleConf]:
        """Return module conf object."""
        return self._module_conf  # type: ignore

    @classmethod
    def template_module_name(cls) -> str:
        """Return module name for configuration builder."""
        return cls.__name__.lower()

    @classmethod
    def template_module_variables(cls) -> List[TemplateConfigItem]:
        """Return configuration variables template."""
        out: List[TemplateConfigItem] = []
        # item format:
        # TemplateConfigItem()
        out.append(
            TemplateConfigItem(desc="ZFS Snapshot automation configuration module.")
        )
        out.append(TemplateConfigItem(desc="Variables:"))
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.S_VOLUMES}' [List[str]] - List of ZFS volumes to monitor,"
            )
        )
        out.append(
            TemplateConfigItem(desc="for example:  ['tank/volume1', 'tank/volume2'].")
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.S_INTERVAL}' [str] - how often to take the snapshot,"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="this is an integer representing 'seconds' or a numerical value with the suffix 's|m|h|d|w'.",
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.S_MAX_COUNT}' [int] - maximum number of snapshots for rotation procedure."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.S_FREE_SPACE}' [int] - minimum percentage of free space needed to trigger a snapshot."
            )
        )
        out.append(
            TemplateConfigItem(
                desc="After exceeding the above occupancy, a warning message will be generated"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="if a communication channel has been configured for the module."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_ModuleConf.Keys.MESSAGE_CHANNEL}' [List[str]], comma separated communication channels list,"
            )
        )
        out.append(
            TemplateConfigItem(desc="['nr(:default delay=0)'|'nr1:delay', 'nr2:delay']")
        )
        out.append(
            TemplateConfigItem(desc="where 'delay' means the time between generating")
        )
        out.append(
            TemplateConfigItem(
                desc="subsequent notifications for a given channel and can be given in"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="seconds or a numerical value with the suffix 's|m|h|d|w'"
            )
        )
        out.append(TemplateConfigItem(desc="Optional variables:"))
        out.append(
            TemplateConfigItem(
                desc=f"'{_ModuleConf.Keys.SLEEP_PERIOD}' [float], which determines the length of the break"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="between subsequent executions of the program's main loop"
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_ModuleConf.Keys.MESSAGE_CHANNEL,
                value=["1"],
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.S_VOLUMES,
                value=[],
                desc="[List[str]]",
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.S_MAX_COUNT,
                value=24,
                desc="[int]",
            )
        )
        out.append(
            TemplateConfigItem(varname=_Keys.S_INTERVAL, value="1h", desc="[int|str]")
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.S_FREE_SPACE,
                value=20,
                desc="[int]",
            )
        )
        return out


# #[EOF]#######################################################################
