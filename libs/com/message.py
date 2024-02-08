# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 14.11.2023

  Purpose: communication subsystem classes.
"""

from datetime import datetime
from inspect import currentframe
from typing import Optional, Union, Dict, List
from threading import Thread, Event
from queue import Queue, Empty, Full

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.libs.base_th import ThBaseObject
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.datetool import Timestamp

from libs.base.classes import BThProcessor, BClasses
from libs.tools.datetool import MIntervals, MDateTime


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys definition class.

    For internal purpose only.
    """

    AT_DAY: str = "dmonth"
    AT_DWEEK: str = "dweek"
    AT_HOUR: str = "hour"
    AT_MINUTE: str = "minute"
    AT_MONTH: str = "month"
    CHANNELS: str = "__channels__"
    MCHANNEL: str = "__channel__"
    MCOMQUEUES: str = "__comq__"
    MCOUNTER: str = "__counter__"
    MMESS: str = "__message__"
    MMULTIPART: str = "__mmessage__"
    MREPLY: str = "__reply__"
    MSENDER: str = "__sender__"
    MSUBJECT: str = "__subject__"
    MTO: str = "__to__"
    PINT: str = "__interval__"
    PNEXT: str = "__next__"


class AtChannel(BClasses):
    """AtChannel class."""

    def __init__(self, config_channel: List[str]) -> None:
        """Constructor."""
        # config_channel example:
        # ["1:0;0;7|10|12|13;*;*", "1:0;8|12|16|21;14;*;*"]
        # explanation of string format:
        # "channel:minute;hour;day-of-month;month;day-of-week"
        self._data[_Keys.CHANNELS] = dict()
        self.__config_channels(config_channel)

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
            tmp: list[str] = form.split("-")
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
                    tmp2: list[str] = item.split("-")
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
        tmp: list[str] = cron.split(";")
        if len(tmp) != 5:
            raise Raise.error(
                f"String format error, check example in config file.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        # value format: '\d+', '\d+|\d+|\d+', '\d+-\d+', '\d+|\d+-\d+', '*'
        # minutes
        out[_Keys.AT_MINUTE] = self.__build_value_list(form=tmp[0], vrange=[0, 59])
        # hours
        out[_Keys.AT_HOUR] = self.__build_value_list(form=tmp[1], vrange=[0, 23])
        # days-of-month
        out[_Keys.AT_DAY] = self.__build_value_list(form=tmp[2], vrange=[1, 31])
        # months
        out[_Keys.AT_MONTH] = self.__build_value_list(form=tmp[3], vrange=[1, 12])
        # days-of-week
        out[_Keys.AT_DWEEK] = self.__build_value_list(form=tmp[4], vrange=[0, 7])

        return out

    def __config_channels(self, config_channel: List[str]) -> None:
        """Create channels dict."""
        if not isinstance(config_channel, List):
            raise Raise.error(
                f"Expected List type, received: '{type(config_channel)}'",
                TypeError,
                self._c_name,
                currentframe(),
            )
        for item in config_channel:
            if item.find(":") < 0:
                raise Raise.error(
                    f"Channel string format error, check example in config file.",
                    ValueError,
                    self._c_name,
                    currentframe(),
                )
            channel, cron = item.split(":", 1)
            if channel not in self._data[_Keys.CHANNELS]:
                self._data[_Keys.CHANNELS][channel] = []
            self._data[_Keys.CHANNELS][channel].append(self.__build_cron_data(cron))

    @property
    def check(self) -> bool:
        """Returns True, if the time has come :)"""
        date: datetime = MDateTime.now()
        # "channel:minute;hour;day-of-month;month;day-of-week"
        # date.minute
        # date.hour
        # date.day
        # date.month
        # date.weekday() + 1 == crontab weekday (sunday:0 or 7)

        for chan in self.channels:
            for item in self._data[_Keys.CHANNELS][chan]:
                if (
                    date.minute in item[_Keys.AT_MINUTE]
                    and date.hour in item[_Keys.AT_HOUR]
                    and date.day in item[_Keys.AT_DAY]
                    and date.month in item[_Keys.AT_MONTH]
                ):
                    if date.weekday() == 6 and (
                        0 in item[_Keys.AT_DWEEK] or 7 in item[_Keys.AT_DWEEK]
                    ):
                        return True
                    elif date.weekday() + 1 in item[_Keys.AT_DWEEK]:
                        return True
        return False

    @property
    def get(self) -> List[str]:
        """Get a list of expired channels."""
        date: datetime = MDateTime.now()
        out = list()
        for channel in self.channels:
            for item in self._data[_Keys.CHANNELS][channel]:
                if (
                    date.minute in item[_Keys.AT_MINUTE]
                    and date.hour in item[_Keys.AT_HOUR]
                    and date.day in item[_Keys.AT_DAY]
                    and date.month in item[_Keys.AT_MONTH]
                ):
                    if date.weekday() == 6 and (
                        0 in item[_Keys.AT_DWEEK] or 7 in item[_Keys.AT_DWEEK]
                    ):
                        if channel not in out:
                            out.append(channel)
                    elif date.weekday() + 1 in item[_Keys.AT_DWEEK]:
                        if channel not in out:
                            out.append(channel)
        return out

    @property
    def channels(self) -> List[str]:
        """Get configured channels list."""
        return list(self._data[_Keys.CHANNELS].keys())

    @property
    def dump(self) -> Dict:
        """Test."""
        return self._data[_Keys.CHANNELS]


class Channel(BClasses):
    """Channel class."""

    def __init__(self, config_channel: List[str]) -> None:
        """Constructor."""
        # config_channel example:
        # ['1','2:300s','3:3h']
        self._data[_Keys.CHANNELS] = dict()
        self.__config_channels(config_channel)

    def __config_channels(self, config_channel: List[str]) -> None:
        """Create channels dict."""
        if not isinstance(config_channel, List):
            raise Raise.error(
                f"Expected List type, received: '{type(config_channel)}'",
                TypeError,
                self._c_name,
                currentframe(),
            )
        for item in config_channel:
            if str(item).find(":") > -1:
                (channel, interval) = item.split(":")
                conv = MIntervals(self._c_name)
                self.__add_channel(channel, conv.convert(interval))
            else:
                self.__add_channel(item, 0)

    def __add_channel(self, channel: str, interval: int) -> None:
        """Add channel config to dict."""
        if channel in self._data[_Keys.CHANNELS]:
            raise Raise.error(
                f"Duplicate channel key found: '{channel}'",
                KeyError,
                self._c_name,
                currentframe(),
            )
        self._data[_Keys.CHANNELS][channel] = {
            _Keys.PINT: interval,
            _Keys.PNEXT: Timestamp.now,
        }

    @property
    def check(self) -> bool:
        """Returns True, if the time has come :)"""
        now = Timestamp.now
        for item in self.channels:
            if self._data[_Keys.CHANNELS][item][_Keys.PNEXT] < now:
                return True
        return False

    @property
    def get(self) -> List[str]:
        """Get a list of expired channels."""
        now: int = Timestamp.now
        out = []
        for item in self.channels:
            pdict: Dict = self._data[_Keys.CHANNELS][item]
            if pdict[_Keys.PNEXT] < now:
                out.append(item)
                pdict[_Keys.PNEXT] = now + pdict[_Keys.PINT]
        return out

    @property
    def channels(self) -> List[str]:
        """Get configured channels list."""
        return list(self._data[_Keys.CHANNELS].keys())


class Multipart(object, metaclass=ReadOnlyClass):
    """Keys definition class.

    For define multipart message public keys.
    """

    PLAIN: str = "plain"
    HTML: str = "html"


class Message(BClasses):
    """Communication message container class."""

    def __init__(self) -> None:
        """Constructor."""
        self._data[_Keys.MMESS] = []
        self._data[_Keys.MMULTIPART] = None
        self._data[_Keys.MCHANNEL] = None
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
    def channel(self) -> Optional[int]:
        """Return channel int."""
        return self._data[_Keys.MCHANNEL]

    @channel.setter
    def channel(self, value: int) -> None:
        """Set message communication channel."""
        if isinstance(value, int):
            self._data[_Keys.MCHANNEL] = value
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
    def subject(self, value: str) -> None:
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
        elif isinstance(value, list):
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


class ThDispatcher(Thread, ThBaseObject, BThProcessor):
    """ThDispatcher class for assigning messages to different queues."""

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
        #    level_1: [registered_queue1, registered_queue2, ]
        #    level_2: [registered_queue3, ]
        # }
        self._data[_Keys.MCOMQUEUES] = dict()

    def register_queue(self, channel: int) -> Queue:
        """Register queue for communication module."""
        if not isinstance(channel, (str, int)):
            raise Raise.error(
                f"Expected string or integer type, received '{type(channel)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if str(channel) not in self._data[_Keys.MCOMQUEUES]:
            self._data[_Keys.MCOMQUEUES][str(channel)] = []
        queue = Queue(maxsize=3000)
        if self._debug:
            self.logs.message_debug = f"add queue for communication channel: {channel}"
        self._data[_Keys.MCOMQUEUES][str(channel)].append(queue)
        return queue

    def run(self) -> None:
        """Main loop."""
        # 1. read qcom
        # 2. dispatch received message object to queues with appropriate communication channel
        # 3. loop to 1.
        if self._debug:
            self.logs.message_debug = "entering to the main loop"

        if self.qcom is not None:
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
                f"Received message for channel: '{message.channel}'"
            )
        if str(message.channel) in self._data[_Keys.MCOMQUEUES]:
            for item in self._data[_Keys.MCOMQUEUES][str(message.channel)]:
                try:
                    queue: Queue = item
                    queue.put(message, block=True, timeout=0.1)
                except Full:
                    self.logs.message_critical = (
                        f"Queue is full exception... check procedure."
                    )
        else:
            raise Raise.error(
                f"Received message with unknown channel: {message.channel}",
                ValueError,
                self._c_name,
                currentframe(),
            )

    def stop(self) -> None:
        """Set stop event."""
        if self._debug:
            self.logs.message_debug = "stop signal received"
        if self._stop_event:
            self._stop_event.set()

    @property
    def stopped(self) -> bool:
        """Return stop flag."""
        if self._stop_event is not None:
            return self._stop_event.is_set()
        return False


# #[EOF]#######################################################################
