# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 23.11.2023

  Purpose: ICMP host testing module
"""

import time
from inspect import currentframe
from typing import Dict, List, Optional, Any, Union
from threading import Thread, Event
from queue import Queue

from jsktoolbox.basetool.threads import ThBaseObject
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.netaddresstool.ipv4 import Address
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.datetool import Timestamp

from libs.base.classes import BModule, BData
from libs.interfaces.modules import IRunModule
from libs.base.classes import BModuleConfig
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart, Channel
from libs.tools.icmp import Pinger
from libs.tools.datetool import MDateTime
from libs.app import AppName


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    CHANGE: str = "__change__"
    HOSTS: str = "hosts"
    IP: str = "__ip__"
    LAST_DOWN: str = "__down__"
    LAST_UP: str = "__up__"


class _ModuleConf(BModuleConfig):
    """Module Config private class."""

    @property
    def hosts(self) -> Optional[List[str]]:
        """Returns hosts IP addresses list."""
        var = self._get(varname=_Keys.HOSTS)
        if var is not None and not isinstance(var, List):
            raise Raise.error(
                "Expected list type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var


class Ipv4Test(BData):
    """Ipv4 container class."""

    def __init__(self, address: Address) -> None:
        """Constructor."""
        self._set_data(key=_Keys.IP, value=address, set_default_type=Address)
        now = Timestamp.now()
        self._set_data(key=_Keys.LAST_UP, value=now, set_default_type=Union[int, float])
        self._set_data(
            key=_Keys.LAST_DOWN, value=now, set_default_type=Union[int, float]
        )
        self._set_data(key=_Keys.CHANGE, value=False, set_default_type=bool)

    @property
    def address(self) -> str:
        """Returns ipv4 address object."""
        return str(self._get_data(key=_Keys.IP))

    @property
    def change(self) -> bool:
        """Returns True if change is set."""
        if self._get_data(key=_Keys.CHANGE):
            self._set_data(key=_Keys.CHANGE, value=False)
            return True
        return False

    @property
    def last_up(self) -> int:
        """Last UP timestamp."""
        return self._get_data(key=_Keys.LAST_UP)  # type: ignore

    @property
    def last_down(self) -> int:
        """Last down timestamp."""
        return self._get_data(key=_Keys.LAST_DOWN)  # type: ignore

    @property
    def result(self) -> bool:
        """Returns last availability result."""
        if self.last_up >= self.last_down:
            return True
        return False

    @result.setter
    def result(self, value: bool) -> None:
        """Set result."""
        if value:
            if self.last_up <= self.last_down:
                if self.last_up < self.last_down:
                    self._set_data(key=_Keys.CHANGE, value=True)
                self._set_data(key=_Keys.LAST_UP, value=Timestamp.now())
        else:
            if self.last_up >= self.last_down:
                if self.last_up > self.last_down:
                    self._set_data(key=_Keys.CHANGE, value=True)
                self._set_data(key=_Keys.LAST_DOWN, value=Timestamp.now())


class MIcmp(Thread, ThBaseObject, BModule, IRunModule):
    """ICMP testing module."""

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
        self._bm_debug = debug
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

        if (
            self.module_conf is None
            or self.module_conf.message_channel is None
            or self.module_conf.hosts is None
            or self.qcom is None
        ):
            return None

        # initialization local variables
        ping = Pinger()
        channel = Channel(self.module_conf.message_channel)
        hosts: List[Ipv4Test] = []

        # initialization variables from config file
        if not self._apply_config():
            self.logs.message_error = "configuration error."
            return

        # append tested IPs
        for host_str in self.module_conf.hosts:
            hosts.append(Ipv4Test(Address(host_str)))

        if self.debug:
            self.logs.message_debug = "configuration processing complete"
            self.logs.message_debug = "entering to the main loop"

        # starting module loop
        while not self._stopped:
            # test
            for host in hosts:
                host.result = ping.is_alive(host.address)
            # analyze
            up_now: List[Ipv4Test] = []
            down_now: List[Ipv4Test] = []
            down: List[Ipv4Test] = []
            msg: List[Message] = []
            for host in hosts:
                if not host.result:
                    if host.change:
                        down_now.append(host)
                    else:
                        down.append(host)
                elif host.change:
                    up_now.append(host)

            # down_now - build message now
            for host in down_now:
                tmp_msg = f"{host.address} is down at {MDateTime.datetime_from_timestamp(host.last_down)}"
                for chan in channel.channels:
                    message = Message()
                    message.channel = int(chan)
                    message.messages = tmp_msg
                    msg.append(message)
                self.logs.message_notice = tmp_msg
                # reset channels timeout
                channel.get

            # up_now - build message now
            for host in up_now:
                tmp_msg = (
                    f"{host.address} is up now"
                    f" after {MDateTime.elapsed_time_from_seconds(host.last_up - host.last_down)}"
                )
                for chan in channel.channels:
                    message = Message()
                    message.channel = int(chan)
                    message.messages = tmp_msg
                    msg.append(message)
                self.logs.message_notice = tmp_msg

            # down - build message if channel has expired timeout
            if channel.check and down:
                if self.debug:
                    self.logs.message_debug = "expired channel found"
                for chan in channel.get:
                    for host in down:
                        tmp_msg = (
                            f"{host.address} is down"
                            f" since {MDateTime.elapsed_time_from_seconds(Timestamp.now() - host.last_down)}"
                        )
                        if self.debug:
                            self.logs.message_debug = (
                                f"create message for channel: '{chan}'"
                            )
                            message = Message()
                            message.channel = int(chan)
                            message.messages = tmp_msg
                            msg.append(message)
                        self.logs.message_notice = tmp_msg
            # build and send message
            if msg:
                # build channels dict
                tmp = dict()
                for msg_tmp in msg:
                    if str(msg_tmp.channel) not in tmp:
                        tmp[str(msg_tmp.channel)] = list()
                    tmp[str(msg_tmp.channel)].append(msg_tmp)
                # build messages
                for key in tmp.keys():
                    message = Message()
                    message.channel = int(key)
                    message.subject = f"[{self.application.app_name}:{self._c_name}] host reachability report."
                    message.footer = f"{self.application.app_name} {self.application.app_version} on {self.application.app_host_name}"
                    for item in tmp[key]:
                        tmp2: Message = item
                        for item2 in tmp2.messages:
                            message.messages = item2
                    if self.debug:
                        self.logs.message_debug = "add message to queue"
                    self.qcom.put(message)
            # sleep
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
        if self.debug:
            self.logs.message_debug = "stop signal received"
        if self._stop_event:
            self._stop_event.set()

    @property
    def debug(self) -> bool:
        """Return debug flag."""
        if self._bm_debug is not None:
            return self._bm_debug
        return False

    @property
    def verbose(self) -> bool:
        """Return verbose flag."""
        return self._verbose

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
        out.append(TemplateConfigItem(desc="ICMP configuration module."))
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
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.HOSTS}' [List[str]], list of hosts IP addresses for reachability test"
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_ModuleConf.Keys.SLEEP_PERIOD, value=15, desc="[second]"
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_ModuleConf.Keys.MESSAGE_CHANNEL,
                value=["1:30m"],
            )
        )
        out.append(TemplateConfigItem(varname=_Keys.HOSTS, value=[]))
        return out


# #[EOF]#######################################################################
