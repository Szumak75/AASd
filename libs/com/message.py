# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 14.11.2023

  Purpose: communication subsystem classes.
"""

from inspect import currentframe
from typing import Optional, Union, Dict, List, Any
from threading import Thread, Event
from queue import Queue, Empty, Full

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.libs.base_th import ThBaseObject
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue

from libs.base.classes import BThProcessor, BClasses
from libs.tools.datetool import Intervals, Timestamp, DateTime


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys definition class.

    For internal purpose only.
    """

    ATDAY = "dmonth"
    ATDWEEK = "dweek"
    ATHOUR = "hour"
    ATMINUTE = "minute"
    ATMONTH = "month"
    MMESS = "__message__"
    MMULTIPART = "__mmessage__"
    MPRIORITY = "__priority__"
    MTO = "__to__"
    MSUBJECT = "__subject__"
    MCOMQUEUES = "__comq__"
    MCOUNTER = "__counter__"
    MSENDER = "__sender__"
    MREPLY = "__reply__"
    PCONF = "__priorities__"
    PNEXT = "__next__"
    PINT = "__interval__"


class AtPriority(BClasses):
    """AtPriority class."""

    def __init__(self, config_priority: List[str]) -> None:
        """Constructor."""
        # config_priority example:
        # ["1:0;0;7|10|12|13;*;*", "1:0;8|12|16|21;14;*;*"]
        # explanation of string format:
        # "priority:minute;hour;day-of-month;month;day-of-week"
        self._data[_Keys.PCONF] = dict()
        self.__config_priorities(config_priority)

    def __build_value_list(self, form: str, vrange: List[int]) -> List[int]:
        """Create list of integer from formatted string."""
        out = list()
        if form.find("*") > -1:
            for i in range(vrange[0], vrange[1] + 1):
                out.append(i)
        elif form.find("|") == -1 and form.find("-") == -1:
            try:
                out.append(int(form))
            except Exception as ex:
                raise Raise.error(
                    f"String format error, check example in config file. Exception: {ex}",
                    ValueError,
                    self._c_name,
                    currentframe(),
                )
        elif form.find("|") > -1 and form.find("-") == -1:
            tmp = form.split("|")
            for i in tmp:
                try:
                    out.append(int(i))
                except Exception as ex:
                    raise Raise.error(
                        f"String format error, check example in config file. Exception: {ex}",
                        ValueError,
                        self._c_name,
                        currentframe(),
                    )
        elif form.find("-") > -1 and form.find("|") == -1:
            tmp = form.split("-")
            if len(tmp) == 2:
                try:
                    for i in range(int(tmp[0]), int(tmp[1]) + 1):
                        if i in range(vrange[0], vrange[1] + 1):
                            out.append(i)
                except Exception as ex:
                    raise Raise.error(
                        f"String format error, check example in config file. Exception: {ex}",
                        ValueError,
                        self._c_name,
                        currentframe(),
                    )
        elif form.find("-") > -1 and form.find("|") > -1:
            tmp = form.split("|")
            for item in tmp:
                if item.find("-") > -1:
                    tmp2 = item.split("-")
                    if len(tmp2) == 2:
                        try:
                            for i in range(int(tmp2[0]), int(tmp2[1]) + 1):
                                if i in range(vrange[0], vrange[1] + 1):
                                    out.append(i)
                        except Exception as ex:
                            raise Raise.error(
                                f"String format error, check example in config file. Exception: {ex}",
                                ValueError,
                                self._c_name,
                                currentframe(),
                            )
                else:
                    try:
                        out.append(int(item))
                    except Exception as ex:
                        raise Raise.error(
                            f"String format error, check example in config file. Exception: {ex}",
                            ValueError,
                            self._c_name,
                            currentframe(),
                        )

        return out

    def __build_cron_data(self, cron: str) -> Dict:
        """Create dictionary for cron configuration."""
        out = dict()
        tmp = cron.split(";")
        if len(tmp) != 5:
            raise Raise.error(
                f"String format error, check example in config file.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        # value format: '\d+', '\d+|\d+|\d+', '\d+-\d+', '\d+|\d+-\d+', '*'
        # minutes
        out[_Keys.ATMINUTE] = self.__build_value_list(
            form=tmp[0], vrange=[0, 59]
        )
        # hours
        out[_Keys.ATHOUR] = self.__build_value_list(
            form=tmp[1], vrange=[0, 23]
        )
        # days-of-month
        out[_Keys.ATDAY] = self.__build_value_list(
            form=tmp[2], vrange=[1, 31]
        )
        # months
        out[_Keys.ATMONTH] = self.__build_value_list(
            form=tmp[3], vrange=[1, 12]
        )
        # days-of-week
        out[_Keys.ATDWEEK] = self.__build_value_list(
            form=tmp[4], vrange=[0, 7]
        )

        return out

    def __config_priorities(self, config_priority: List[str]) -> None:
        """Create priorities dict."""
        if not isinstance(config_priority, List):
            raise Raise.error(
                f"Expected List type, received: '{type(config_priority)}'",
                self._c_name,
                currentframe(),
            )
        for item in config_priority:
            if item.find(":") < 0:
                raise Raise.error(
                    f"Priority string format error, check example in config file.",
                    ValueError,
                    self._c_name,
                    currentframe(),
                )
            priority, cron = item.split(":", 1)
            if priority not in self._data[_Keys.PCONF]:
                self._data[_Keys.PCONF][priority] = []
            self._data[_Keys.PCONF][priority].append(
                self.__build_cron_data(cron)
            )

    @property
    def check(self) -> bool:
        """Returns True, if the time has come :)"""
        date = DateTime.now()
        # "priority:minute;hour;day-of-month;month;day-of-week"
        # date.minute
        # date.hour
        # date.day
        # date.month
        # date.weekday() + 1 == crontab weekday (sunday:0 or 7)

        for prio in self.priorities:
            for item in self._data[_Keys.PCONF][prio]:
                if (
                    date.minute in item[_Keys.ATMINUTE]
                    and date.hour in item[_Keys.ATHOUR]
                    and date.day in item[_Keys.ATDAY]
                    and date.month in item[_Keys.ATMONTH]
                ):
                    if date.weekday() == 6 and (
                        0 in item[_Keys.ATDWEEK] or 7 in item[_Keys.ATDWEEK]
                    ):
                        return True
                    elif date.weekday() + 1 in item[_Keys.ATDWEEK]:
                        return True
        return False

    @property
    def get(self) -> List[str]:
        """Get a list of expired priorities."""
        date = DateTime.now()
        out = list()
        for prio in self.priorities:
            for item in self._data[_Keys.PCONF][prio]:
                if (
                    date.minute in item[_Keys.ATMINUTE]
                    and date.hour in item[_Keys.ATHOUR]
                    and date.day in item[_Keys.ATDAY]
                    and date.month in item[_Keys.ATMONTH]
                ):
                    if date.weekday() == 6 and (
                        0 in item[_Keys.ATDWEEK] or 7 in item[_Keys.ATDWEEK]
                    ):
                        if prio not in out:
                            out.append(prio)
                    elif date.weekday() + 1 in item[_Keys.ATDWEEK]:
                        if prio not in out:
                            out.append(prio)
        return out

    @property
    def priorities(self) -> List[str]:
        """Get configured priorities list."""
        return list(self._data[_Keys.PCONF].keys())

    @property
    def dump(self) -> Dict:
        """Test."""
        return self._data[_Keys.PCONF]


class Priority(BClasses):
    """Priority class."""

    def __init__(self, config_priority: List[str]) -> None:
        """Constructor."""
        # config_priority example:
        # ['1','2:300s','3:3h']
        self._data[_Keys.PCONF] = dict()
        self.__config_priorities(config_priority)

    def __config_priorities(self, config_priority: List[str]) -> None:
        """Create priorities dict."""
        if not isinstance(config_priority, List):
            raise Raise.error(
                f"Expected List type, received: '{type(config_priority)}'",
                self._c_name,
                currentframe(),
            )
        for item in config_priority:
            if str(item).find(":") > -1:
                (priority, interval) = item.split(":")
                conv = Intervals(self._c_name)
                self.__add_priority(priority, conv.convert(interval))
            else:
                self.__add_priority(item, 0)

    def __add_priority(self, priority: str, interval: int) -> None:
        """Add priority config to dict."""
        if priority in self._data[_Keys.PCONF]:
            raise Raise.error(
                f"Duplicate priority key found: '{priority}'",
                KeyError,
                self._c_name,
                currentframe(),
            )
        self._data[_Keys.PCONF][priority] = {
            _Keys.PINT: interval,
            _Keys.PNEXT: Timestamp.now,
        }

    @property
    def check(self) -> bool:
        """Returns True, if the time has come :)"""
        now = Timestamp.now
        for item in self.priorities:
            if self._data[_Keys.PCONF][item][_Keys.PNEXT] < now:
                return True
        return False

    @property
    def get(self) -> List[str]:
        """Get a list of expired priorities."""
        now = Timestamp.now
        out = []
        for item in self.priorities:
            pdict: Dict = self._data[_Keys.PCONF][item]
            if pdict[_Keys.PNEXT] < now:
                out.append(item)
                pdict[_Keys.PNEXT] = now + pdict[_Keys.PINT]
        return out

    @property
    def priorities(self) -> List[str]:
        """Get configured priorities list."""
        return list(self._data[_Keys.PCONF].keys())


class Multipart(object, metaclass=ReadOnlyClass):
    """Keys definition class.

    For define multipart message public keys.
    """

    PLAIN = "plain"
    HTML = "html"


class Message(BClasses):
    """Communication message container class."""

    def __init__(self):
        """Constructor."""
        self._data[_Keys.MMESS] = []
        self._data[_Keys.MMULTIPART] = None
        self._data[_Keys.MPRIORITY] = None
        self._data[_Keys.MTO] = None
        self._data[_Keys.MSUBJECT] = None
        self._data[_Keys.MSENDER] = None
        self._data[_Keys.MREPLY] = None
        self._data[_Keys.MCOUNTER] = 0

    @property
    def counter(self) -> int:
        """Return counter."""
        self._data[_Keys.MCOUNTER] += 1
        return self._data[_Keys.MCOUNTER]

    @property
    def priority(self) -> Optional[int]:
        """Return priority int."""
        return self._data[_Keys.MPRIORITY]

    @priority.setter
    def priority(self, value: int) -> None:
        """Set message communication priority."""
        if isinstance(value, int):
            self._data[_Keys.MPRIORITY] = value
        else:
            raise Raise.error(
                f"Expected integer type, received '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def reply_to(self) -> Optional[str]:
        """Return optional reply-to string."""
        return self._data[_Keys.MREPLY]

    @reply_to.setter
    def reply_to(self, value: str) -> None:
        """Set reply-to string."""
        if not isinstance(value, str):
            raise Raise.error(
                f"Expected string type, received '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self._data[_Keys.MREPLY] = value

    @property
    def messages(self) -> List[str]:
        """Return messages list."""
        return self._data[_Keys.MMESS]

    @messages.setter
    def messages(self, message: str) -> None:
        """Append message to list."""
        self._data[_Keys.MMESS].append(str(message))

    @property
    def mmessages(self) -> Optional[Dict]:
        """Return optional multipart messages list."""
        return self._data[_Keys.MMULTIPART]

    @mmessages.setter
    def mmessages(self, mdict: Dict) -> None:
        """Append multipart dict messages.

        Example:
        mdict = {
        Multipart.PLAIN: []
        Multipart.HTML: []
        }
        """
        if not isinstance(mdict, Dict):
            raise Raise.error(
                f"Expected Dict type, received: '{type(mdict)}'",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if self._data[_Keys.MMULTIPART] is None:
            self._data[_Keys.MMULTIPART] = {}
        self._data[_Keys.MMULTIPART].update(mdict)

    @property
    def sender(self) -> Optional[str]:
        """Return optional sender string."""
        return self._data[_Keys.MSENDER]

    @sender.setter
    def sender(self, value: str) -> None:
        """Set sender string."""
        if not isinstance(value, str):
            raise Raise.error(
                f"Expected string type, received '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self._data[_Keys.MSENDER] = value

    @property
    def subject(self) -> Optional[str]:
        """Return optional title string."""
        return self._data[_Keys.MSUBJECT]

    @subject.setter
    def subject(self, value: str):
        """Set optional title string."""
        if not isinstance(value, str):
            raise Raise.error(
                f"Expected string type, received '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self._data[_Keys.MSUBJECT] = value

    @property
    def to(self) -> Optional[List[str]]:
        """Return optional to string.

        For example: custom email address.
        """
        return self._data[_Keys.MTO]

    @to.setter
    def to(self, value: Union[List[str], str]) -> None:
        """Set optional to string."""
        if not self.to:
            self._data[_Keys.MTO] = []
        if isinstance(value, str):
            self._data[_Keys.MTO].append(value)
        elif isinstance(value, List[str]):
            for item in value:
                if item:
                    self._data[_Keys.MTO].append(item)
        else:
            raise Raise.error(
                f"Expected string or list type, received '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )


class Dispatcher(Thread, ThBaseObject, BThProcessor):
    """Dispatcher class for assigning messages to different queues."""

    def __init__(
        self,
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

        # logging level
        self._debug = debug
        self._verbose = verbose

        # logger client initialization
        self.logs = LoggerClient(queue=qlog, name=self._c_name)

        # communication queue for reading
        self.qcom = qcom

        # communication queues for target modules
        # example:
        # {
        #    level_1: [regisetred_queue1, registered_queue2, ]
        #    level_2: [regisetred_queue3, ]
        # }
        self._data[_Keys.MCOMQUEUES] = dict()

    def register_queue(self, priority: int) -> Queue:
        """Register queue for communication module."""
        if not isinstance(priority, (str, int)):
            raise Raise.error(
                f"Expected string or integer type, received '{type(priority)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if str(priority) not in self._data[_Keys.MCOMQUEUES]:
            self._data[_Keys.MCOMQUEUES][str(priority)] = []
        queue = Queue(maxsize=1000)
        if self._debug:
            self.logs.message_debug = (
                f"add queue for communication priority: {priority}"
            )
        self._data[_Keys.MCOMQUEUES][str(priority)].append(queue)
        return queue

    def run(self) -> None:
        """Main loop."""
        # 1. read qcom
        # 2. dispatch received message object to queues with appropriate communication priority
        # 3. loop to 1.
        if self._debug:
            self.logs.message_debug = "entering to the main loop"

        while not self.stopped:
            try:
                message: Message = self.qcom.get(block=True, timeout=0.1)
                if message is None:
                    continue

                try:
                    self.__dispatch_message(message)
                except Exception as ex:
                    self.logs.message_critical = (
                        f'error while dispatch message: "{ex}"'
                    )
                self.qcom.task_done()

            except Empty:
                pass
            except Exception as ex:
                self.logs.message_critical = (
                    f'error while processing message: "{ex}"'
                )

        if self._debug:
            self.logs.message_debug = "exit from loop"

    def __dispatch_message(self, message: Message) -> None:
        """Put message to queues."""
        if not isinstance(message, Message):
            raise Raise.error(
                f"Expected Message type, received '{type(message)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if self._debug:
            self.logs.message_debug = (
                f"Received message for priority: '{message.priority}'"
            )
        if str(message.priority) in self._data[_Keys.MCOMQUEUES]:
            for item in self._data[_Keys.MCOMQUEUES][str(message.priority)]:
                try:
                    queue: Queue = item
                    queue.put(message, block=True, timeout=0.1)
                except Full:
                    self.logs.message_critical = (
                        f"Queue is full exception... check procedure."
                    )
        else:
            raise Raise.error(
                f"Received message with unknown priority: {message.priority}",
                ValueError,
                self._c_name,
                currentframe(),
            )

    def stop(self) -> None:
        """Set stop event."""
        if self._debug:
            self.logs.message_debug = "stop signal received"
        self._stop_event.set()

    @property
    def stopped(self) -> bool:
        """Return stop flag."""
        return self._stop_event.is_set()


# #[EOF]#######################################################################
