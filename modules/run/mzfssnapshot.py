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
from jsktoolbox.datetool import Timestamp, DateTime

from libs.base.classes import BModule
from libs.interfaces.modules import IRunModule
from libs.base.classes import BModuleConfig
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart, Channel
from libs.tools.datetool import MDateTime, MIntervals
from libs.app import AppName


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
    ZP_FREE_SPACE: str = "__free_space__"

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
    def snapshot_interval(self) -> Optional[Union[str, int]]:
        """Snapshot interval."""
        var = self._get(varname=_Keys.S_INTERVAL)
        if var is not None and not isinstance(var, Union[str, int]):
            raise Raise.error(
                "Expected string or integer value for snapshot_interval",
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
            return int(self.__data["used"]) if self.__data["used"] != "-" else None
        return None

    @property
    def available(self) -> Optional[int]:
        """Available space."""
        if self.__data:
            return (
                int(self.__data["available"])
                if self.__data["available"] != "-"
                else None
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
        # pa_snap: re.Pattern[str] = re.compile(r"(\S+)@([\d]{14})")
        pa_snap: re.Pattern[str] = re.compile(r"(\S+)@(\S+)")
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
        # free space in percent (stored by check_free_space method)
        self._set_data(key=_Keys.ZP_FREE_SPACE, value=-1, set_default_type=int)

    def check_volume(self) -> bool:
        """Check if zfs volume exists."""
        # check if variable is correct
        if not self.volume:
            self.__messages.append("invalid volume received as empty string")
            return False
        # check if volume exists
        out: bool = False
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            ["zfs", "list", "-Hp", self.volume],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={"PATH": "/sbin"},
        )

        if result.returncode == 0:
            out = True
            tmp = ZfsData(result.stdout.decode("utf-8"))
            if tmp.error:
                self.__messages.append(f"Invalid zfs volume: {self.volume}")
                out = False
            else:
                # check  if volume is proper
                if tmp.volume != self.volume and tmp.mount_point == self.volume:
                    self._set_data(key=_Keys.ZP_VOLUME, value=tmp.volume)
                    self.__messages.append(f"Volume updated to: {self.volume}")

        else:
            self.__messages.append(result.stderr.decode("utf-8"))
        return out

    def get_volume(self, volume: Optional[str] = None) -> Optional[ZfsData]:
        """Get zfs volume information."""
        if not volume:
            volume = self.volume
        # check if volume exists
        out: Optional[ZfsData] = None
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            ["zfs", "list", "-Hp", volume],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={"PATH": "/sbin"},
        )

        if result.returncode == 0:
            tmp = ZfsData(result.stdout.decode("utf-8"))
            if tmp.error:
                self.__messages.append(f"Invalid zfs volume: {volume}")
            else:
                out = tmp
        else:
            self.__messages.append(result.stderr.decode("utf-8"))
        return out

    def get_volumes(self, volume: Optional[str] = None) -> List[ZfsData]:
        """Get all zfs volumes."""
        output: List[ZfsData] = []
        if not volume:
            volume = self.volume

        with subprocess.Popen(
            ["zfs", "list", "-Hpr", "-tall", volume],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={"PATH": "/sbin"},
        ) as proc:
            # process output
            if proc.stdout:
                for line in proc.stdout:
                    if line:
                        tmp = ZfsData(line.decode("utf-8"))
                        if tmp.error:
                            self.__messages.append(f"Invalid zfs volume: {self.volume}")
                        else:
                            output.append(tmp)
            elif proc.stderr:
                for line in proc.stderr:
                    self.__messages.append(line.decode("utf-8"))
        return output

    def get_snapshots(self, volume: Optional[str] = None) -> List[ZfsData]:
        """Get all zfs snapshots."""
        output: List[ZfsData] = []
        if not volume:
            volume = self.volume
        out: List[ZfsData] = self.get_volumes(volume)
        for item in out:
            if item.snapshot_name:
                output.append(item)
        return output

    def create_snapshot(self, snapshot_name: Optional[str] = None) -> bool:
        """Create zfs snapshot.

        Args:
        snapshot_name (str): Name of the snapshot to create (suffix after '@').
        """
        if not snapshot_name:
            snapshot_name = DateTime.now().strftime("%Y%m%d%H%M%S")

        # check if snapshot  exists
        out = self.get_volume(f"{self.volume}@{snapshot_name}")
        if out:
            self.__messages.append(
                f"Snapshot already exists: {self.volume}@{snapshot_name}"
            )
            return False
        else:
            self.clear()
        # create snapshot
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            ["zfs", "snapshot", f"{self.volume}@{snapshot_name}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={"PATH": "/sbin"},
        )
        if result.returncode == 0:
            return True
        else:
            self.__messages.append(result.stderr.decode("utf-8"))
        return False

    def cleanup_snapshots(
        self,
        volume: Optional[str] = None,
        max_count: Optional[int] = None,
        snapshot_name: Optional[str] = None,
    ) -> bool:
        """Cleanup zfs snapshots."""
        pa_snap: re.Pattern[str] = re.compile(r"([\d]{14})")
        if not volume:
            volume = self.volume
        if snapshot_name:
            out: Optional[ZfsData] = self.get_volume(f"{volume}@{snapshot_name}")
            if out:
                result: subprocess.CompletedProcess[bytes] = subprocess.run(
                    ["zfs", "destroy", f"{volume}@{snapshot_name}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env={"PATH": "/sbin"},
                )
                if result.returncode == 0:
                    return True
            return False
        else:
            snapshots: List[ZfsData] = []
            cleanup: List[str] = []
            if not max_count:
                max_count = 10
            tmp = self.get_volumes(volume)
            if tmp:
                for item in tmp:
                    if item.snapshot_name and pa_snap.match(item.snapshot_name):
                        snapshots.append(item)
                if snapshots and len(snapshots) > max_count:
                    count = len(snapshots) - max_count
                    for i in range(count):
                        cleanup.append(
                            f"{snapshots[i].snapshot_root}@{snapshots[i].snapshot_name}"
                        )
                if cleanup:
                    clean_out = True
                    for item in cleanup:
                        result: subprocess.CompletedProcess[bytes] = subprocess.run(
                            ["zfs", "destroy", item],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            env={"PATH": "/sbin"},
                        )
                        if result.returncode != 0:
                            self.__messages.append(result.stderr.decode("utf-8"))
                            clean_out = False
                    return clean_out
            return True

    def check_free_space(self, percent: int = 20) -> bool:
        """Check free space on root zfs volume.

        Below 20%: False
        Above 20%: True
        """
        vol: Optional[ZfsData] = self.get_volume()
        if not vol:
            self.__messages.append(f"Missing volume: {self.volume}")
            return False
        root_vol: Optional[ZfsData] = self.get_volume(vol.volume_root)
        if root_vol:
            free_space: Optional[int] = root_vol.available
            used_space: Optional[int] = root_vol.used
            if free_space is not None and used_space is not None:
                free_space_percent: float = (
                    free_space / (free_space + used_space)
                ) * 100
                self._set_data(key=_Keys.ZP_FREE_SPACE, value=int(free_space_percent))
                if free_space_percent > percent:
                    return True
        return False

    def get_free_space(self) -> int:
        """Get free space on root zfs volume."""
        if self._get_data(key=_Keys.ZP_FREE_SPACE) == -1:
            self.check_free_space()
        return self._get_data(key=_Keys.ZP_FREE_SPACE)  # type: ignore

    def clear(self) -> None:
        """Clear messages."""
        if self.__messages:
            self.__messages.clear()

    @property
    def volume(self) -> str:
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
        app_name: AppName,
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
        self.application = app_name
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
            # config checks #
            #################
            if self.module_conf.sleep_period:
                self.sleep_period = self.module_conf.sleep_period
            # message channel
            if self.module_conf.message_channel is None:
                self.logs.message_critical = (
                    f"'{_ModuleConf.Keys.MESSAGE_CHANNEL}' not set, exiting..."
                )
                self.stop()
            # volumes
            if not self.module_conf.volumes:
                self.logs.message_critical = f"No '{_Keys.S_VOLUMES}' specified."
                self.stop()
            else:
                self._volumes = self.module_conf.volumes
            # max_snapshot_count
            if not self.module_conf.max_snapshot_count:
                self.logs.message_critical = f"No '{_Keys.S_MAX_COUNT}' specified."
                self.stop()
            else:
                self._max_snapshot_count = self.module_conf.max_snapshot_count
            # snapshot_interval
            if not self.module_conf.snapshot_interval:
                self.logs.message_critical = f"No '{_Keys.S_INTERVAL}' specified."
                self.stop()
            else:
                self._snapshot_interval = self.module_conf.snapshot_interval
            # min_free_space
            if not self.module_conf.min_free_space:
                self.logs.message_critical = f"No '{_Keys.S_FREE_SPACE}' specified."
                self.stop()
            else:
                # minimum free space in percent
                self._min_free_space = self.module_conf.min_free_space
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
        next_run = Timestamp.now()

        # initialization variables from config file
        if not self._apply_config():
            self.logs.message_error = "configuration error."
            return

        if self.debug:
            self.logs.message_debug = "configuration processing complete"
            self.logs.message_debug = "entering to the main loop"

        # starting module loop
        while not self._stopped:
            # TODO: do something, build a message if necessary, put it in the qcom queue

            if Timestamp.now() < next_run:
                # sleep time
                self.sleep()
                continue

            # set next time to run
            next_run = Timestamp.now() + self._snapshot_interval

            # process volume from config list
            for volume in self._volumes:
                if not volume:
                    self.logs.message_warning = f"check '{_Keys.S_VOLUMES}' variable in configuration file, i have got empty string."
                    continue

                # zfs processor
                zp = ZfsProcessor(volume)
                if not zp.check_volume():
                    if zp.messages:
                        for item in zp.messages:
                            self.logs.message_error = item
                    else:
                        self.logs.message_error = f"some error for '{volume}' volume"
                    continue

                # check messages
                if zp.messages:
                    for item in zp.messages:
                        self.logs.message_error = item
                    zp.clear()

                # check free space
                if zp.check_free_space(self._min_free_space):
                    # create snapshot
                    if not zp.create_snapshot():
                        self.logs.message_error = (
                            f"create snapshot for '{volume}' volume failed"
                        )
                    else:
                        self.logs.message_info = f"snapshot for '{volume}' created, free space: {zp.get_free_space()}%"

                    # check messages
                    if zp.messages:
                        for item in zp.messages:
                            self.logs.message_error = item
                        zp.clear()

                    # destroy old snapshots
                    if not zp.cleanup_snapshots(max_count=self._max_snapshot_count):
                        self.logs.message_error = (
                            f"cleanup snapshots for '{volume}' volume failed"
                        )

                    # check messages
                    if zp.messages:
                        for item in zp.messages:
                            self.logs.message_error = item
                        zp.clear()

                else:
                    self.logs.message_critical = f"free space on volume '{volume}' is less than {self._min_free_space}% and is {zp.get_free_space()}%"
                    # TODO: send  message to qcom queue

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
    def _min_free_space(self) -> int:
        return self._get_data(key=_Keys.S_FREE_SPACE)  # type: ignore

    @_min_free_space.setter
    def _min_free_space(self, value: int) -> None:
        self._set_data(key=_Keys.S_FREE_SPACE, value=value, set_default_type=int)

    @property
    def _snapshot_interval(self) -> int:
        return self._get_data(key=_Keys.S_INTERVAL)  # type: ignore

    @_snapshot_interval.setter
    def _snapshot_interval(self, value: Union[int, str]) -> None:
        self._set_data(
            key=_Keys.S_INTERVAL,
            value=MIntervals(self._c_name).convert(f"{value}"),
            set_default_type=int,
        )

    @property
    def _max_snapshot_count(self) -> int:
        return self._get_data(key=_Keys.S_MAX_COUNT)  # type: ignore

    @_max_snapshot_count.setter
    def _max_snapshot_count(self, value: int) -> None:
        self._set_data(key=_Keys.S_MAX_COUNT, value=value, set_default_type=int)

    @property
    def _volumes(self) -> List[str]:
        return self._get_data(key=_Keys.S_VOLUMES)  # type: ignore

    @_volumes.setter
    def _volumes(self, value: List[str]) -> None:
        self._set_data(key=_Keys.S_VOLUMES, value=value, set_default_type=List)

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
