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
from libs.tools.datetool import Intervals, Timestamp


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys definition class.

    For internal purpose only.
    """

    CMESS = "__message__"
    CMULTIPART = "__mmessage__"
    CPRIORITY = "__priority__"
    CTO = "__to__"
    CSUBJECT = "__subject__"
    COMQUEUES = "__comq__"
    COUNTER = "__counter__"
    CSENDER = "__sender__"
    PCONF = "__priorities__"
    PNEXT = "__next__"
    PINT = "__interval__"


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
        return self._data[_Keys.PCONF].keys()


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
        self._data[_Keys.CMESS] = []
        self._data[_Keys.CMULTIPART] = None
        self._data[_Keys.CPRIORITY] = None
        self._data[_Keys.CTO] = None
        self._data[_Keys.CSUBJECT] = None
        self._data[_Keys.CSENDER] = None
        self._data[_Keys.COUNTER] = 0

    @property
    def counter(self) -> int:
        """Return counter."""
        self._data[_Keys.COUNTER] += 1
        return self._data[_Keys.COUNTER]

    @property
    def priority(self) -> Optional[int]:
        """Return priority int."""
        return self._data[_Keys.CPRIORITY]

    @priority.setter
    def priority(self, value: int) -> None:
        """Set message communication priority."""
        if isinstance(value, int):
            self._data[_Keys.CPRIORITY] = value
        else:
            raise Raise.error(
                f"Expected integer type, received '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def messages(self) -> List[str]:
        """Return messages list."""
        return self._data[_Keys.CMESS]

    @messages.setter
    def messages(self, message: str) -> None:
        """Append message to list."""
        self._data[_Keys.CMESS].append(str(message))

    @property
    def mmessages(self) -> Optional[Dict]:
        """Return optional multipart messages list."""
        return self._data[_Keys.CMULTIPART]

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
        if self._data[_Keys.CMULTIPART] is None:
            self._data[_Keys.CMULTIPART] = {}
        self._data[_Keys.CMULTIPART].update(mdict)

    @property
    def sender(self) -> Optional[str]:
        """Return optional sender string."""
        return self._data[_Keys.CSENDER]

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
        self._data[_Keys.CSENDER] = value

    @property
    def subject(self) -> Optional[str]:
        """Return optional title string."""
        return self._data[_Keys.CSUBJECT]

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
        self._data[_Keys.CSUBJECT] = value

    @property
    def to(self) -> Optional[str]:
        """Return optional to string.

        For example: custom email address.
        """
        return self._data[_Keys.CTO]

    @to.setter
    def to(self, value: str) -> None:
        """Set optional to string."""
        if not isinstance(value, str):
            raise Raise.error(
                f"Expected string type, received '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self._data[_Keys.CTO] = value


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
        self._data[_Keys.COMQUEUES] = dict()

    def register_queue(self, priority: int) -> Queue:
        """Register queue for communication module."""
        if not isinstance(priority, (str, int)):
            raise Raise.error(
                f"Expected string or integer type, received '{type(priority)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if str(priority) not in self._data[_Keys.COMQUEUES]:
            self._data[_Keys.COMQUEUES][str(priority)] = []
        queue = Queue(maxsize=1000)
        if self._debug:
            self.logs.message_debug = (
                f"add queue for communication priority: {priority}"
            )
        self._data[_Keys.COMQUEUES][str(priority)].append(queue)
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
                finally:
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
        if str(message.priority) in self._data[_Keys.COMQUEUES]:
            for item in self._data[_Keys.COMQUEUES][str(message.priority)]:
                try:
                    queue: Queue = item
                    queue.put(message, block=True, timeout=5.0)
                except Full:
                    self.logs.message_critical = (
                        f"Queue is full exception... check procedure."
                    )
                finally:
                    queue.task_done()
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
