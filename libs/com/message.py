# -*- coding: UTF-8 -*-
"""
Messaging subsystem primitives.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-11-14

Purpose: Provide message containers, channel schedulers, and dispatcher logic.
"""

from datetime import datetime
from inspect import currentframe
from typing import Any, Dict, List, Mapping, Optional, Union
from threading import Thread, Event
from queue import Queue, Empty, Full

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.basetool import ThBaseObject
from jsktoolbox.logstool import LoggerClient, LoggerQueue
from jsktoolbox.datetool import Timestamp
from jsktoolbox.basetool import BData

from libs.base import ThProcessorMixin
from libs.tools import MDateTime, MIntervals


class _Keys(object, metaclass=ReadOnlyClass):
    """Define internal storage keys for the messaging subsystem."""

    # #[CONSTANTS]#####################################################################
    AT_DAY: str = "day_of_month"
    AT_DAY_WEEK: str = "day_of_week"
    AT_HOUR: str = "hour"
    AT_MINUTE: str = "minute"
    AT_MONTH: str = "month"
    AT_SCHEDULER: str = "__at_scheduler__"
    CHANNELS: str = "__channels__"
    CHECK_INTERVAL: str = "__interval__"
    CHECK_NEXT: str = "__next__"
    INTERVAL_SCHEDULER: str = "__interval_scheduler__"
    MSG_CHANNEL: str = "__channel__"
    MSG_COM_QUEUES: str = "__com_q__"
    MSG_COUNTER: str = "__counter__"
    MSG_FOOTER: str = "__foot__"
    MSG_MESS: str = "__message__"
    MSG_MULTIPART: str = "__m_message__"
    MSG_REPLY: str = "__reply__"
    MSG_SENDER: str = "__sender__"
    MSG_SUBJECT: str = "__subject__"
    MSG_TO: str = "__to__"


class AtChannel(BData):
    """Implement cron-like scheduling for message channels."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self, config_channel: List[str]) -> None:
        """Initialize the cron-style channel scheduler.

        ### Arguments:
        * config_channel: List[str] - Channel definitions in
          `channel:minute;hour;day;month;weekday` format.
        """
        # config_channel example:
        # ["1:0;0;7|10|12|13;*;*", "1:0;8|12|16|21;14;*;*"]
        # explanation of string format:
        # "channel:minute;hour;day-of-month;month;day-of-week"
        self._set_data(key=_Keys.CHANNELS, value={}, set_default_type=Dict)
        self.__config_channels(config_channel)

    # #[PUBLIC PROPERTIES]#############################################################
    @property
    def channels(self) -> List[str]:
        """Return the configured channel identifiers.

        ### Returns:
        List[str] - Configured channel identifiers.
        """
        return list(self.get_channels.keys())

    @property
    def check(self) -> bool:
        """Return whether at least one configured channel is currently due.

        ### Returns:
        bool - `True` when at least one channel is ready.
        """
        date: datetime = MDateTime.now()

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
                    if date.weekday() + 1 in item[_Keys.AT_DAY_WEEK]:
                        return True
        return False

    @property
    def get(self) -> List[str]:
        """Return channels whose cron schedule is currently due.

        ### Returns:
        List[str] - Due channel identifiers.
        """
        date: datetime = MDateTime.now()
        out: List[str] = []
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
    def get_channels(self) -> Dict[str, List[Dict[str, List[int]]]]:
        """Return the internal cron channel mapping.

        ### Returns:
        Dict - Mapping of channel identifiers to cron schedule definitions.
        """
        return self._get_data(key=_Keys.CHANNELS)  # type: ignore

    # #[PRIVATE METHODS]###############################################################
    def __build_cron_data(self, cron: str) -> Dict[str, List[int]]:
        """Convert a cron-style channel definition to internal scheduling data.

        ### Arguments:
        * cron: str - Cron-style field definition without the channel prefix.

        ### Returns:
        Dict[str, List[int]] - Parsed scheduling fields.
        """
        out: Dict[str, List[int]] = {}
        tmp: List[str] = cron.split(";")
        if len(tmp) != 5:
            raise Raise.error(
                "String format error, check example in config file.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        out[_Keys.AT_MINUTE] = self.__build_value_list(form=tmp[0], val_range=[0, 59])
        out[_Keys.AT_HOUR] = self.__build_value_list(form=tmp[1], val_range=[0, 23])
        out[_Keys.AT_DAY] = self.__build_value_list(form=tmp[2], val_range=[1, 31])
        out[_Keys.AT_MONTH] = self.__build_value_list(form=tmp[3], val_range=[1, 12])
        out[_Keys.AT_DAY_WEEK] = self.__build_value_list(form=tmp[4], val_range=[0, 7])
        return out

    def __build_value_list(self, form: str, val_range: List[int]) -> List[int]:
        """Convert one cron field definition to a list of integers.

        ### Arguments:
        * form: str - Raw cron field string.
        * val_range: List[int] - Inclusive minimum and maximum allowed values.

        ### Returns:
        List[int] - Expanded list of accepted integer values.
        """
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
            tmp: List[str] = form.split("|")
            for item in tmp:
                try:
                    out.append(int(item))
                except Exception as ex:
                    raise Raise.error(
                        f"String format error, check example in config file. Exception: {ex}",
                        ValueError,
                        self._c_name,
                        currentframe(),
                    )
        elif form.find("-") > -1 and form.find("|") == -1:
            tmp_range: List[str] = form.split("-")
            if len(tmp_range) == 2:
                try:
                    for item in range(int(tmp_range[0]), int(tmp_range[1]) + 1):
                        if item in range(val_range[0], val_range[1] + 1):
                            out.append(item)
                except Exception as ex:
                    raise Raise.error(
                        f"String format error, check example in config file. Exception: {ex}",
                        ValueError,
                        self._c_name,
                        currentframe(),
                    )
        elif form.find("-") > -1 and form.find("|") > -1:
            tmp: List[str] = form.split("|")
            for item in tmp:
                if item.find("-") > -1:
                    tmp_range = item.split("-")
                    if len(tmp_range) == 2:
                        try:
                            for value in range(
                                int(tmp_range[0]), int(tmp_range[1]) + 1
                            ):
                                if value in range(val_range[0], val_range[1] + 1):
                                    out.append(value)
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

    def __config_channels(self, config_channel: List[str]) -> None:
        """Build the internal cron schedule mapping.

        ### Arguments:
        * config_channel: List[str] - Channel configuration definitions.
        """
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
                    "Channel string format error, check example in config file.",
                    ValueError,
                    self._c_name,
                    currentframe(),
                )
            channel, cron = item.split(":", 1)
            channels = self.get_channels
            if channel not in channels:
                channels[channel] = []
            channels[channel].append(self.__build_cron_data(cron))


class Channel(BData):
    """Implement interval-based scheduling for message channels."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self, config_channel: List[str]) -> None:
        """Initialize the interval-based channel scheduler.

        ### Arguments:
        * config_channel: List[str] - Channel definitions such as
          `["1", "2:300s", "3:3h"]`.
        """
        # config_channel example:
        # ['1','2:300s','3:3h']
        self._set_data(key=_Keys.CHANNELS, value={}, set_default_type=Dict)
        self.__config_channels(config_channel)

    # #[PUBLIC PROPERTIES]#############################################################
    @property
    def channels(self) -> List[str]:
        """Return the configured channel identifiers.

        ### Returns:
        List[str] - Configured channel identifiers.
        """
        return list(self.get_channels.keys())

    @property
    def check(self) -> bool:
        """Return whether at least one configured channel is currently due.

        ### Returns:
        bool - `True` when at least one channel is ready.
        """
        now: int = Timestamp.now()  # type: ignore
        for item in self.channels:
            if self.get_channels[item][_Keys.CHECK_NEXT] < now:
                return True
        return False

    @property
    def get(self) -> List[str]:
        """Return channels whose interval timer has expired.

        ### Returns:
        List[str] - Due channel identifiers.
        """
        now: int = Timestamp.now()  # type: ignore
        out: List[str] = []
        for item in self.channels:
            check_dict: Dict[str, Union[int, float]] = self.get_channels[item]
            if check_dict[_Keys.CHECK_NEXT] < now:
                out.append(item)
                check_dict[_Keys.CHECK_NEXT] = now + check_dict[_Keys.CHECK_INTERVAL]
        return out

    @property
    def get_channels(self) -> Dict[str, Dict[str, Union[int, float]]]:
        """Return the internal interval channel mapping.

        ### Returns:
        Dict - Mapping of channel identifiers to scheduling metadata.
        """
        obj: Optional[Dict[str, Dict[str, Union[int, float]]]] = self._get_data(
            key=_Keys.CHANNELS
        )
        if obj is None:
            raise Raise.error(
                "Internal error: Channel mapping is not initialized.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        return obj

    # #[PRIVATE METHODS]###############################################################
    def __add_channel(self, channel: str, interval: int) -> None:
        """Register one channel and its interval in the internal mapping.

        ### Arguments:
        * channel: str - Channel identifier.
        * interval: int - Interval in seconds.
        """
        if channel in self.channels:
            raise Raise.error(
                f"Duplicate channel key found: '{channel}'",
                KeyError,
                self._c_name,
                currentframe(),
            )
        self.get_channels[channel] = {
            _Keys.CHECK_INTERVAL: interval,
            _Keys.CHECK_NEXT: Timestamp.now() - 1,
        }

    def __config_channels(self, config_channel: List[str]) -> None:
        """Build the internal interval schedule mapping.

        ### Arguments:
        * config_channel: List[str] - Channel configuration definitions.
        """
        if not isinstance(config_channel, List):
            raise Raise.error(
                f"Expected List type, received: '{type(config_channel)}'",
                TypeError,
                self._c_name,
                currentframe(),
            )
        for item in config_channel:
            if str(item).find(":") > -1:
                channel, interval = str(item).split(":")
                conv = MIntervals(self._c_name)
                self.__add_channel(channel, conv.convert(interval))
            else:
                self.__add_channel(str(item), 0)


class NotificationScheduler(BData):
    """Decide which outbound notification channels are currently due."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(
        self,
        message_channel: Optional[List[Union[int, str]]] = None,
        at_channel: Optional[List[str]] = None,
    ) -> None:
        """Initialize the combined notification scheduler helper.

        ### Arguments:
        * message_channel: Optional[List[Union[int, str]]] - Interval-based
          notification channel definitions.
        * at_channel: Optional[List[str]] - Cron-like notification channel
          definitions.
        """
        self._set_data(
            key=_Keys.AT_SCHEDULER,
            value=None,
            set_default_type=Optional[AtChannel],
        )
        self._set_data(
            key=_Keys.INTERVAL_SCHEDULER,
            value=None,
            set_default_type=Optional[Channel],
        )
        if message_channel:
            self._interval_scheduler = Channel([str(item) for item in message_channel])
        if at_channel:
            self._at_scheduler = AtChannel(at_channel)

    # #[PRIVATE PROPERTIES]###########################################################
    @property
    def _at_scheduler(self) -> Optional[AtChannel]:
        """Return the optional cron-like scheduler.

        ### Returns:
        Optional[AtChannel] - Cron-like scheduler or `None`.
        """
        return self._get_data(key=_Keys.AT_SCHEDULER, default_value=None)

    @_at_scheduler.setter
    def _at_scheduler(self, value: Optional[AtChannel]) -> None:
        """Store the optional cron-like scheduler.

        ### Arguments:
        * value: Optional[AtChannel] - Cron-like scheduler or `None`.
        """
        self._set_data(key=_Keys.AT_SCHEDULER, value=value)

    @property
    def _interval_scheduler(self) -> Optional[Channel]:
        """Return the optional interval-based scheduler.

        ### Returns:
        Optional[Channel] - Interval-based scheduler or `None`.
        """
        return self._get_data(key=_Keys.INTERVAL_SCHEDULER, default_value=None)

    @_interval_scheduler.setter
    def _interval_scheduler(self, value: Optional[Channel]) -> None:
        """Store the optional interval-based scheduler.

        ### Arguments:
        * value: Optional[Channel] - Interval-based scheduler or `None`.
        """
        self._set_data(key=_Keys.INTERVAL_SCHEDULER, value=value)

    # #[PUBLIC PROPERTIES]############################################################
    @property
    def has_schedule(self) -> bool:
        """Return whether any notification schedule is configured.

        ### Returns:
        bool - `True` when at least one schedule source is configured.
        """
        return self._at_scheduler is not None or self._interval_scheduler is not None

    # #[PUBLIC METHODS]################################################################
    def due_channels(self) -> List[int]:
        """Return notification channels that are currently due.

        ### Returns:
        List[int] - Channel identifiers ready for emission.
        """
        out: List[int] = []
        if self._interval_scheduler is not None:
            out.extend(self.__normalize_channels(self._interval_scheduler.get))
        if self._at_scheduler is not None:
            out.extend(self.__normalize_channels(self._at_scheduler.get))

        deduplicated: List[int] = []
        for channel in out:
            if channel not in deduplicated:
                deduplicated.append(channel)
        return deduplicated

    @classmethod
    def from_config(
        cls,
        config: Mapping[str, Any],
        message_channel_key: str = "message_channel",
        at_channel_key: str = "at_channel",
    ) -> "NotificationScheduler":
        """Build a scheduler helper from parsed plugin config values.

        ### Arguments:
        * config: Mapping[str, Any] - Parsed plugin config values.
        * message_channel_key: str - Key used for interval-based targets.
        * at_channel_key: str - Key used for cron-like targets.

        ### Returns:
        NotificationScheduler - Combined scheduler helper.
        """
        message_channel: Optional[List[Union[int, str]]] = None
        at_channel: Optional[List[str]] = None

        raw_message_channel = config.get(message_channel_key)
        if raw_message_channel is not None:
            if not isinstance(raw_message_channel, list):
                raise Raise.error(
                    f"Expected list type for '{message_channel_key}'.",
                    TypeError,
                    cls.__name__,
                    currentframe(),
                )
            message_channel = list(raw_message_channel)

        raw_at_channel = config.get(at_channel_key)
        if raw_at_channel is not None:
            if not isinstance(raw_at_channel, list):
                raise Raise.error(
                    f"Expected list type for '{at_channel_key}'.",
                    TypeError,
                    cls.__name__,
                    currentframe(),
                )
            at_channel = [str(item) for item in raw_at_channel]

        return cls(message_channel=message_channel, at_channel=at_channel)

    # #[PRIVATE METHODS]###############################################################
    def __normalize_channels(self, channels: List[str]) -> List[int]:
        """Convert raw channel identifiers to integers.

        ### Arguments:
        * channels: List[str] - Raw channel identifiers.

        ### Returns:
        List[int] - Normalized integer channel identifiers.
        """
        out: List[int] = []
        for channel in channels:
            try:
                out.append(int(channel))
            except Exception as ex:
                raise Raise.error(
                    f"Notification channel '{channel}' is not a valid integer. Exception: {ex}",
                    ValueError,
                    self._c_name,
                    currentframe(),
                )
        return out


class Multipart(object, metaclass=ReadOnlyClass):
    """Expose public keys used for multipart message payloads."""

    # #[CONSTANTS]#####################################################################
    PLAIN: str = "plain"
    HTML: str = "html"


class Message(BData):
    """Store a message exchanged between worker and communication plugins."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self) -> None:
        """Initialize an empty message container."""
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

    # #[PUBLIC PROPERTIES]#############################################################
    @property
    def channel(self) -> Optional[int]:
        """Return the target communication channel.

        ### Returns:
        Optional[int] - Target communication channel or `None`.
        """
        return self._get_data(key=_Keys.MSG_CHANNEL)

    @channel.setter
    def channel(self, value: int) -> None:
        """Store the target communication channel.

        ### Arguments:
        * value: int - Target communication channel number.
        """
        self._set_data(
            key=_Keys.MSG_CHANNEL,
            value=value,
        )

    @property
    def counter(self) -> int:
        """Increment and return the internal message counter.

        ### Returns:
        int - Updated counter value.
        """
        count: Optional[int] = self._get_data(key=_Keys.MSG_COUNTER)
        if count is None:
            raise Raise.error(
                "Internal error: Message counter is not initialized.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        count += 1
        self._set_data(key=_Keys.MSG_COUNTER, value=count)
        return count

    @property
    def footer(self) -> Optional[str]:
        """Return the message footer.

        ### Returns:
        Optional[str] - Footer text or `None`.
        """
        return self._get_data(key=_Keys.MSG_FOOTER, default_value=None)

    @footer.setter
    def footer(self, value: str) -> None:
        """Store the message footer.

        ### Arguments:
        * value: str - Footer text appended by the delivery plugin.
        """
        self._set_data(key=_Keys.MSG_FOOTER, value=value, set_default_type=str)

    @property
    def reply_to(self) -> Optional[str]:
        """Return the reply-to address.

        ### Returns:
        Optional[str] - Reply-to address or `None`.
        """
        return self._get_data(key=_Keys.MSG_REPLY)

    @reply_to.setter
    def reply_to(self, value: str) -> None:
        """Store the reply-to address.

        ### Arguments:
        * value: str - Reply-to address.
        """
        self._set_data(key=_Keys.MSG_REPLY, value=value)

    @property
    def messages(self) -> List[str]:
        """Return the plain message fragments.

        ### Returns:
        List[str] - Plain message fragments.
        """
        obj: Optional[List[str]] = self._get_data(key=_Keys.MSG_MESS)
        if obj is None:
            raise Raise.error(
                "Internal error: Message fragments list is not initialized.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        return obj

    @messages.setter
    def messages(self, message: Union[str, List[str]]) -> None:
        """Append one or many plain message fragments.

        ### Arguments:
        * message: Union[str, List[str]] - Plain message fragment or fragment
          list to append.
        """
        if isinstance(message, str):
            self.messages.append(message)
        elif isinstance(message, List):
            for item in message:
                self.messages.append(str(item))
        else:
            self.messages.append(str(message))

    @property
    def mmessages(self) -> Optional[Dict[str, Any]]:
        """Return multipart message fragments.

        ### Returns:
        Optional[Dict[str, Any]] - Multipart message mapping or `None`.
        """
        return self._get_data(key=_Keys.MSG_MULTIPART)

    @mmessages.setter
    def mmessages(self, msg_dict: Dict[str, Any]) -> None:
        """Merge multipart message fragments into the container.

        ### Arguments:
        * msg_dict: Dict[str, Any] - Multipart message mapping keyed by
          `Multipart.PLAIN` and `Multipart.HTML`.

        ### Raises:
        * TypeError: If `msg_dict` is not a dictionary.
        """
        if not isinstance(msg_dict, Dict):
            raise Raise.error(
                f"Expected Dict type, received: '{type(msg_dict)}'",
                TypeError,
                self._c_name,
                currentframe(),
            )
        mmessages: Optional[Dict[str, Any]] = self.mmessages
        if mmessages is None:
            self._set_data(key=_Keys.MSG_MULTIPART, value={})
            mmessages: Optional[Dict[str, Any]] = self.mmessages
            if mmessages is None:
                raise Raise.error(
                    "Internal error: Multipart message mapping is not initialized.",
                    ValueError,
                    self._c_name,
                    currentframe(),
                )
        mmessages.update(msg_dict)

    @property
    def sender(self) -> Optional[str]:
        """Return the sender address override.

        ### Returns:
        Optional[str] - Sender address or `None`.
        """
        return self._get_data(key=_Keys.MSG_SENDER)

    @sender.setter
    def sender(self, value: str) -> None:
        """Store the sender address override.

        ### Arguments:
        * value: str - Sender address.
        """
        self._set_data(
            key=_Keys.MSG_SENDER,
            value=value,
        )

    @property
    def subject(self) -> Optional[str]:
        """Return the message subject.

        ### Returns:
        Optional[str] - Message subject or `None`.
        """
        return self._get_data(key=_Keys.MSG_SUBJECT)

    @subject.setter
    def subject(self, value: str) -> None:
        """Store the message subject.

        ### Arguments:
        * value: str - Message subject.
        """
        self._set_data(
            key=_Keys.MSG_SUBJECT,
            value=value,
        )

    @property
    def to(self) -> Optional[Union[List[str], str]]:
        """Return destination recipients collected for the message.

        ### Returns:
        Optional[Union[List[str], str]] - Recipient list or `None`.
        """
        return self._get_data(key=_Keys.MSG_TO)

    @to.setter
    def to(self, value: Union[List[str], str]) -> None:
        """Append one or many destination recipients.

        ### Arguments:
        * value: Union[List[str], str] - Recipient address or recipient list.

        ### Raises:
        * TypeError: If `value` is neither a string nor a list of strings.
        """
        if self.to is None:
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


class ThDispatcher(Thread, ThBaseObject, ThProcessorMixin):
    """Route outbound messages to queues registered for communication plugins."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(
        self,
        qlog: LoggerQueue,
        qcom: Queue,
        verbose: bool = False,
        debug: bool = False,
    ) -> None:
        """Initialize the dispatcher thread.

        ### Arguments:
        * qlog: LoggerQueue - Shared logging queue.
        * qcom: Queue - Shared message queue read by the dispatcher.
        * verbose: bool - Initial verbose flag value.
        * debug: bool - Initial debug flag value.
        """
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

        # communication queues for target plugins
        # example:
        # {
        #    level_1: [registered_queue1, registered_queue2, ]
        #    level_2: [registered_queue3, ]
        # }
        self._set_data(key=_Keys.MSG_COM_QUEUES, value={}, set_default_type=Dict)

    # #[PRIVATE PROPERTIES]############################################################
    @property
    def __get_comm_queues(self) -> Dict[str, List[Queue]]:
        """Return internal queue registry keyed by communication channel.

        ### Returns:
        Dict[str, List[Queue]] - Registered queues for each communication channel.
        """
        return self._get_data(key=_Keys.MSG_COM_QUEUES)  # type: ignore

    # #[PUBLIC METHODS]################################################################
    def register_queue(self, channel: int) -> Queue:
        """Register a target queue for the selected communication channel.

        ### Arguments:
        * channel: int - Channel identifier handled by a communication plugin.

        ### Returns:
        Queue - Newly created queue registered for the channel.

        ### Raises:
        * TypeError: If `channel` is neither a string nor an integer.
        """
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
        """Read shared messages and forward them to registered channel queues."""
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

    # #[PRIVATE METHODS]###############################################################
    def __dispatch_message(self, message: Message) -> None:
        """Forward one message to every queue registered for its channel.

        ### Arguments:
        * message: Message - Message object to dispatch.

        ### Raises:
        * TypeError: If `message` is not an instance of `Message`.
        * ValueError: If the message references an unknown channel.
        """
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
