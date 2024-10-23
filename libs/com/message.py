# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 14.11.2023

  Purpose: communication subsystem classes.
"""

from datetime import datetime
from inspect import currentframe
from typing import Optional, Union, Dict, List, Any
from threading import Thread, Event
from queue import Queue, Empty, Full

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.basetool.threads import ThBaseObject
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.datetool import Timestamp
from jsktoolbox.basetool.data import BData

from libs.base.classes import BThProcessor
from libs.tools.datetool import MIntervals, MDateTime


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys definition class.

    For internal purpose only.
    """

    AT_DAY: str = "day_of_month"
    AT_DAY_WEEK: str = "day_of_week"
    AT_HOUR: str = "hour"
    AT_MINUTE: str = "minute"
    AT_MONTH: str = "month"
    CHANNELS: str = "__channels__"
    CHECK_INTERVAL: str = "__interval__"
    CHECK_NEXT: str = "__next__"
    MSG_CHANNEL: str = "__channel__"
    MSG_COM_QUEUES: str = "__com_q__"
    MSG_COUNTER: str = "__counter__"
    MSG_MESS: str = "__message__"
    MSG_MULTIPART: str = "__m_message__"
    MSG_REPLY: str = "__reply__"
    MSG_SENDER: str = "__sender__"
    MSG_SUBJECT: str = "__subject__"
    MSG_TO: str = "__to__"


class AtChannel(BData):
    """AtChannel class."""

    def __init__(self, config_channel: List[str]) -> None:
        """Constructor."""
        # config_channel example:
        # ["1:0;0;7|10|12|13;*;*", "1:0;8|12|16|21;14;*;*"]
        # explanation of string format:
        # "channel:minute;hour;day-of-month;month;day-of-week"
        self._set_data(key=_Keys.CHANNELS, value={}, set_default_type=Dict)
        self.__config_channels(config_channel)

    def __build_value_list(self, form: str, val_range: List[int]) -> List[int]:
        """Create list of integer from formatted string."""
        out: List[int] = []
        if form.find("*") > -1:
            for i in range(val_range[0], val_range[1] + 1):
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
                        if i in range(val_range[0], val_range[1] + 1):
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
                                if i in range(val_range[0], val_range[1] + 1):
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

    def __build_cron_data(self, cron: str) -> Dict[str, List[int]]:
        """Create dictionary for cron configuration."""
        out: Dict[str, List[int]] = {}
        tmp: List[str] = cron.split(";")
        if len(tmp) != 5:
            raise Raise.error(
                f"String format error, check example in config file.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        # value format: '\d+', '\d+|\d+|\d+', '\d+-\d+', '\d+|\d+-\d+', '*'
        # minutes
        out[_Keys.AT_MINUTE] = self.__build_value_list(form=tmp[0], val_range=[0, 59])
        # hours
        out[_Keys.AT_HOUR] = self.__build_value_list(form=tmp[1], val_range=[0, 23])
        # days-of-month
        out[_Keys.AT_DAY] = self.__build_value_list(form=tmp[2], val_range=[1, 31])
        # months
        out[_Keys.AT_MONTH] = self.__build_value_list(form=tmp[3], val_range=[1, 12])
        # days-of-week
        out[_Keys.AT_DAY_WEEK] = self.__build_value_list(form=tmp[4], val_range=[0, 7])

        return out

    def __config_channels(self, config_channel: List[str]) -> None:
        """Create channels dict."""
        channel: str
        cron: str
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
            (channel, cron) = item.split(":", 1)
            channels: Dict = self._get_data(key=_Keys.CHANNELS)  # type: ignore
            if channel not in channels:
                channels[channel] = []
            channels[channel].append(self.__build_cron_data(cron))

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
            for item in self.get_channels[chan]:
                if (
                    date.minute in item[_Keys.AT_MINUTE]
                    and date.hour in item[_Keys.AT_HOUR]
                    and date.day in item[_Keys.AT_DAY]
                    and date.month in item[_Keys.AT_MONTH]
                ):
                    if date.weekday() == 6 and (
                        0 in item[_Keys.AT_DAY_WEEK] or 7 in item[_Keys.AT_DAY_WEEK]
                    ):
                        return True
                    elif date.weekday() + 1 in item[_Keys.AT_DAY_WEEK]:
                        return True
        return False

    @property
    def get(self) -> List[str]:
        """Get a list of expired channels."""
        date: datetime = MDateTime.now()
        out = list()
        for channel in self.channels:
            for item in self.get_channels[channel]:
                if (
                    date.minute in item[_Keys.AT_MINUTE]
                    and date.hour in item[_Keys.AT_HOUR]
                    and date.day in item[_Keys.AT_DAY]
                    and date.month in item[_Keys.AT_MONTH]
                ):
                    if date.weekday() == 6 and (
                        0 in item[_Keys.AT_DAY_WEEK] or 7 in item[_Keys.AT_DAY_WEEK]
                    ):
                        if channel not in out:
                            out.append(channel)
                    elif date.weekday() + 1 in item[_Keys.AT_DAY_WEEK]:
                        if channel not in out:
                            out.append(channel)
        return out

    @property
    def channels(self) -> List[str]:
        """Get configured channels list."""
        return list(self.get_channels.keys())

    @property
    def get_channels(self) -> Dict:
        """Return channels Dict."""
        return self._get_data(key=_Keys.CHANNELS)  # type: ignore


class Channel(BData):
    """Channel class."""

    def __init__(self, config_channel: List[str]) -> None:
        """Constructor."""
        # config_channel example:
        # ['1','2:300s','3:3h']
        self._set_data(key=_Keys.CHANNELS, value={}, set_default_type=Dict)
        self.__config_channels(config_channel)

    def __config_channels(self, config_channel: List[str]) -> None:
        """Create channels dict."""
        channel: str
        interval: str
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
        if channel in self.channels:
            raise Raise.error(
                f"Duplicate channel key found: '{channel}'",
                KeyError,
                self._c_name,
                currentframe(),
            )
        self.get_channels[channel] = {
            _Keys.CHECK_INTERVAL: interval,
            _Keys.CHECK_NEXT: Timestamp.now(),
        }

    @property
    def check(self) -> bool:
        """Returns True, if the time has come :)"""
        now: int = Timestamp.now()  # type: ignore
        for item in self.channels:
            if self.get_channels[item][_Keys.CHECK_NEXT] < now:
                return True
        return False

    @property
    def get(self) -> List[str]:
        """Get a list of expired channels."""
        now: int = Timestamp.now()  # type: ignore
        out = []
        for item in self.channels:
            check_dict: Dict = self.get_channels[item]
            if check_dict[_Keys.CHECK_NEXT] < now:
                out.append(item)
                check_dict[_Keys.CHECK_NEXT] = now + check_dict[_Keys.CHECK_INTERVAL]
        return out

    @property
    def channels(self) -> List[str]:
        """Get configured channels list."""
        return list(self.get_channels.keys())

    @property
    def get_channels(self) -> Dict:
        """Return channels Dict."""
        return self._get_data(key=_Keys.CHANNELS)  # type: ignore


class Multipart(object, metaclass=ReadOnlyClass):
    """Keys definition class.

    For define multipart message public keys.
    """

    PLAIN: str = "plain"
    HTML: str = "html"


class Message(BData):
    """Communication message container class."""

    def __init__(self) -> None:
        """Constructor."""
        self._set_data(key=_Keys.MSG_MESS, value=[], set_default_type=List)
        self._set_data(
            key=_Keys.MSG_MULTIPART, value=None, set_default_type=Optional[Dict]
        )
        self._set_data(
            key=_Keys.MSG_CHANNEL, value=None, set_default_type=Optional[int]
        )
        self._set_data(
            key=_Keys.MSG_TO, value=None, set_default_type=Optional[Union[List, str]]
        )
        self._set_data(
            key=_Keys.MSG_SUBJECT, value=None, set_default_type=Optional[str]
        )
        self._set_data(key=_Keys.MSG_SENDER, value=None, set_default_type=Optional[str])
        self._set_data(key=_Keys.MSG_REPLY, value=None, set_default_type=Optional[str])
        self._set_data(key=_Keys.MSG_COUNTER, value=0, set_default_type=int)

    @property
    def counter(self) -> int:
        """Return counter."""
        count: int = self._get_data(key=_Keys.MSG_COUNTER)  # type: ignore
        count += 1
        self._set_data(key=_Keys.MSG_COUNTER, value=count)
        return count

    @property
    def channel(self) -> Optional[int]:
        """Return channel int."""
        return self._get_data(key=_Keys.MSG_CHANNEL)

    @channel.setter
    def channel(self, value: int) -> None:
        """Set message communication channel."""
        self._set_data(
            key=_Keys.MSG_CHANNEL,
            value=value,
        )

    @property
    def reply_to(self) -> Optional[str]:
        """Return optional reply-to string."""
        return self._get_data(key=_Keys.MSG_REPLY)

    @reply_to.setter
    def reply_to(self, value: str) -> None:
        """Set reply-to string."""
        self._set_data(key=_Keys.MSG_REPLY, value=value)

    @property
    def messages(self) -> List[str]:
        """Return messages list."""
        return self._get_data(key=_Keys.MSG_MESS)  # type: ignore

    @messages.setter
    def messages(self, message: str) -> None:
        """Append message to list."""
        self.messages.append(str(message))

    @property
    def mmessages(self) -> Optional[Dict]:
        """Return optional multipart messages list."""
        return self._get_data(key=_Keys.MSG_MULTIPART)

    @mmessages.setter
    def mmessages(self, msg_dict: Dict[str, Any]) -> None:
        """Append multipart dict messages.

        Example:
        msg_dict = {
        Multipart.PLAIN: []
        Multipart.HTML: []
        }
        """
        if not isinstance(msg_dict, Dict):
            raise Raise.error(
                f"Expected Dict type, received: '{type(msg_dict)}'",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if self.mmessages is None:
            self._set_data(key=_Keys.MSG_MULTIPART, value={})
        self.mmessages.update(msg_dict)  # type: ignore

    @property
    def sender(self) -> Optional[str]:
        """Return optional sender string."""
        return self._get_data(key=_Keys.MSG_SENDER)

    @sender.setter
    def sender(self, value: str) -> None:
        """Set sender string."""
        self._set_data(
            key=_Keys.MSG_SENDER,
            value=value,
        )

    @property
    def subject(self) -> Optional[str]:
        """Return optional title string."""
        return self._get_data(key=_Keys.MSG_SUBJECT)

    @subject.setter
    def subject(self, value: str) -> None:
        """Set optional title string."""
        self._set_data(
            key=_Keys.MSG_SUBJECT,
            value=value,
        )

    @property
    def to(self) -> Optional[List[str]]:
        """Return optional TO string.

        For example: custom email address.
        """
        return self._get_data(key=_Keys.MSG_TO)

    @to.setter
    def to(self, value: Union[List[str], str]) -> None:
        """Set optional TO string."""
        if not self.to:
            self._set_data(
                key=_Keys.MSG_TO,
                value=[],
            )
        if isinstance(value, str):
            self.to.append(value)  # type: ignore
        elif isinstance(value, List):
            for item in value:
                if item:
                    self.to.append(item)  # type: ignore
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
        self._set_data(key=_Keys.MSG_COM_QUEUES, value={}, set_default_type=Dict)

    @property
    def __get_comm_queues(self) -> Dict:
        return self._get_data(key=_Keys.MSG_COM_QUEUES)  # type: ignore

    def register_queue(self, channel: int) -> Queue:
        """Register queue for communication module."""
        if not isinstance(channel, (str, int)):
            raise Raise.error(
                f"Expected string or integer type, received '{type(channel)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if str(channel) not in self.__get_comm_queues.keys():
            self.__get_comm_queues[str(channel)] = []
        queue = Queue(maxsize=3000)
        if self._debug:
            self.logs.message_debug = f"add queue for communication channel: {channel}"
        self.__get_comm_queues[str(channel)].append(queue)
        return queue

    def run(self) -> None:
        """Main loop."""
        # 1. read qcom
        # 2. dispatch received message object to queues with appropriate communication channel
        # 3. loop to 1.
        if self._debug:
            self.logs.message_debug = "entering to the main loop"

        if self.qcom is not None:
            while self.stopped != True:
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
        if str(message.channel) in self.__get_comm_queues.keys():
            for item in self.__get_comm_queues[str(message.channel)]:
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


# #[EOF]#######################################################################
