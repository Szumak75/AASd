# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 23.11.2023

  Purpose: ICMP host testing module
"""

import time
from inspect import currentframe
from typing import Dict, List, Optional, Any
from threading import Thread, Event
from queue import Queue

from jsktoolbox.libs.base_th import ThBaseObject
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.netaddresstool.ipv4 import Address
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.datetool import Timestamp

from libs.base.classes import BModule, BClasses
from libs.interfaces.modules import IRunModule
from libs.base.classes import BModuleConfig
from libs.interfaces.conf import IModuleConfig
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart, Priority
from libs.tools.icmp import Pinger
from libs.tools.datetool import DateTime


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    MODCONF = "__MODULE_CONF__"
    SLEEP_PERIOD = "sleep_period"
    MESSAGE_PRIORITY = "message_priority"
    HOSTS = "hosts"
    IP = "__ip__"
    LASTUP = "__up__"
    LASTDOWN = "__down__"
    CHANGE = "__change__"


class _ModuleConf(IModuleConfig, BModuleConfig):
    """Module Config private class."""

    def _get(self, varname: str) -> Any:
        """Get variable from config."""
        return self._cfh.get(self._section, varname)

    @property
    def hosts(self) -> Optional[List[str]]:
        """Returns hosts IP addrresses list."""
        var = self._get(varname=_Keys.HOSTS)
        if var is not None and not isinstance(var, List):
            raise Raise.error(
                "Expected list type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def message_priority(self) -> Optional[List[str]]:
        """Return message priority list."""
        var = self._get(varname=_Keys.MESSAGE_PRIORITY)
        if var is not None and not isinstance(var, List):
            raise Raise.error(
                "Expected list type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def sleep_period(self) -> float:
        """Return sleep_period var."""
        var = self._get(varname=_Keys.SLEEP_PERIOD)
        if not isinstance(var, (int, float)):
            raise Raise.error(
                "Expected float type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return float(var)


class Ipv4Test(BClasses):
    """Ipv4 container class."""

    def __init__(self, address: Address) -> None:
        """Constructor."""
        self._data[_Keys.IP] = address
        now = Timestamp.now
        self._data[_Keys.LASTUP] = now
        self._data[_Keys.LASTDOWN] = now
        self._data[_Keys.CHANGE] = False

    @property
    def address(self) -> str:
        """Returns ipv4 address object."""
        return str(self._data[_Keys.IP])

    @property
    def change(self) -> bool:
        """Returns True if change is set."""
        if self._data[_Keys.CHANGE]:
            self._data[_Keys.CHANGE] = False
            return True
        return False

    @property
    def last_up(self) -> int:
        """Last UP timestamp."""
        return self._data[_Keys.LASTUP]

    @property
    def last_down(self) -> int:
        """Last down timestamp."""
        return self._data[_Keys.LASTDOWN]

    @property
    def result(self) -> bool:
        """Returns last avability result."""
        if self.last_up >= self.last_down:
            return True
        return False

    @result.setter
    def result(self, value: bool) -> None:
        """Set result."""
        if value:
            if self.last_up <= self.last_down:
                if self.last_up < self.last_down:
                    self._data[_Keys.CHANGE] = True
                self._data[_Keys.LASTUP] = Timestamp.now
        else:
            if self.last_up >= self.last_down:
                if self.last_up > self.last_down:
                    self._data[_Keys.CHANGE] = True
                self._data[_Keys.LASTDOWN] = Timestamp.now


class MIcmp(Thread, ThBaseObject, BModule, IRunModule):
    """ICMP testing module."""

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
        self._data[_Keys.MODCONF] = _ModuleConf(self._cfh, self._section)

        # logging level
        self._debug = debug
        self._verbose = verbose

        # logger client initialization
        self.logs = LoggerClient(queue=qlog, name=self._c_name)

        # communication queue
        self.qcom = qcom

    def _apply_config(self) -> bool:
        """Apply config from module_conf"""
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

        # initialization local variables
        ping = Pinger()
        hosts = []
        priority = Priority(self.module_conf.message_priority)

        # initialization variables from config file
        if not self._apply_config():
            self.logs.message_error = "configuration error."
            return

        # append tested IPs
        for host in self.module_conf.hosts:
            hosts.append(Ipv4Test(Address(host)))

        if self.debug:
            self.logs.message_debug = "configuration processing complete"
            self.logs.message_debug = "entering to the main loop"

        # starting module loop
        while not self.stopped:
            # TODO: not implemented
            # TODO: do something, build a message if necessary, put it in the qcom queue
            # test
            for item in hosts:
                host: Ipv4Test = item
                host.result = ping.is_alive(host.address)
            # analize
            up_now = []
            down_now = []
            down = []
            msg = []
            for item in hosts:
                host: Ipv4Test = item
                if not host.result:
                    if host.change:
                        down_now.append(host)
                    else:
                        down.append(host)
                elif host.change:
                    up_now.append(host)

            # down_now - build message now
            for item in down_now:
                host: Ipv4Test = item
                for prio in priority.priorities:
                    message = Message()
                    message.priority = int(prio)
                    message.messages = f"{host.address} is down at {DateTime.datetime_from_timestamp(host.last_down)}"
                    msg.append(message)
                self.logs.message_notice = f"{host.address} is down at {DateTime.datetime_from_timestamp(host.last_down)}"
                # reset priorities timeout
                priority.get

            # up_now - build message now
            for item in up_now:
                host: Ipv4Test = item
                for prio in priority.priorities:
                    message = Message()
                    message.priority = int(prio)
                    message.messages = f"{host.address} is up now after {DateTime.elapsed_time_from_seconds(host.last_up - host.last_down)}"
                    msg.append(message)
                self.logs.message_notice = f"{host.address} is up now after {DateTime.elapsed_time_from_seconds(host.last_up - host.last_down)}"

            # down - build message if priority has expired timeout
            if priority.check and down:
                if self.debug:
                    self.logs.message_debug = "expired priority found"
                for prio in priority.get:
                    for item in down:
                        host: Ipv4Test = item
                        if self.debug:
                            self.logs.message_debug = (
                                f"create message for priority: '{prio}'"
                            )
                            message = Message()
                            message.priority = int(prio)
                            message.messages = f"{host.address} is down since {DateTime.elapsed_time_from_seconds(Timestamp.now - host.last_down)}"
                            msg.append(message)
                    self.logs.message_notice = f"{host.address} is down since {DateTime.elapsed_time_from_seconds(Timestamp.now - host.last_down)}"
            # build and send message
            if msg:
                # build priorities dict
                tmp = dict()
                for item in msg:
                    msg_tmp: Message = item
                    if str(msg_tmp.priority) not in tmp:
                        tmp[str(msg_tmp.priority)] = list()
                    tmp[str(msg_tmp.priority)].append(msg_tmp)
                # build messages
                for key in tmp.keys():
                    message = Message()
                    message.priority = int(key)
                    message.subject = f"[{self._c_name}] host reachability report"
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
        sbreak = Timestamp.now + self.sleep_period
        while not self.stopped and sbreak > Timestamp.now:
            time.sleep(0.2)

    def stop(self) -> None:
        """Set stop event."""
        if self._debug:
            self.logs.message_debug = "stop signal received."
        self._stop_event.set()

    @property
    def debug(self) -> bool:
        """Return debug flag."""
        return self._debug

    @property
    def verbose(self) -> bool:
        """Return verbose flag."""
        return self._verbose

    @property
    def stopped(self) -> bool:
        """Return stop flag."""
        return self._stop_event.is_set()

    @property
    def module_conf(self) -> Optional[_ModuleConf]:
        """Return module conf object."""
        return self._data[_Keys.MODCONF]

    @classmethod
    def template_module_name(cls) -> str:
        """Return module name for configuration builder."""
        return cls.__name__.lower()

    @classmethod
    def template_module_variables(cls) -> List:
        """Return configuration variables template."""
        out = []
        # item format:
        # TemplateConfigItem()
        out.append(TemplateConfigItem(desc="ICMP configuration for module."))
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.SLEEP_PERIOD}' [float], which determines the length of the break"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="between subsequent executions of the program's main loop"
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.MESSAGE_PRIORITY}' [List[str]], comma separated communication priority list,"
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
                desc="subsequent notifications for a given priority and can be given in"
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
            TemplateConfigItem(varname=_Keys.SLEEP_PERIOD, value=15, desc="[second]")
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.MESSAGE_PRIORITY,
                value=["1:30m"],
            )
        )
        out.append(TemplateConfigItem(varname=_Keys.HOSTS, value=[]))
        return out


# #[EOF]#######################################################################
