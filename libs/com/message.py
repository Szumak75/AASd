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


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys definition class.

    For internal purpose only.
    """

    CMESS = "__message__"
    CLEVEL = "__level__"
    CTO = "__to__"
    CTITLE = "__title__"
    COMQUEUES = "__comq__"
    CSENDER = "__sender__"


class Message(BClasses):
    """Communication message container class."""

    def __init__(self):
        """Constructor."""
        self._data[_Keys.CMESS] = []
        self._data[_Keys.CLEVEL] = None
        self._data[_Keys.CTO] = None
        self._data[_Keys.CTITLE] = None
        self._data[_Keys.CSENDER] = None

    @property
    def level(self) -> Optional[int]:
        """Return level int."""
        return self._data[_Keys.CLEVEL]

    @level.setter
    def level(self, value: int) -> None:
        """Set message communication level."""
        if isinstance(value, int):
            self._data[_Keys.CLEVEL] = value
        else:
            raise Raise.error(
                f"Expected integer type, received '{type(value)}'.",
                TypeError,
                self.c_name,
                currentframe(),
            )

    @property
    def messages(self) -> List:
        """Return messages list."""
        return self._data[_Keys.CMESS]

    @messages.setter
    def messages(self, message: str) -> None:
        """Append message to list."""
        self._data[_Keys.CMESS].append(str(message))

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
                self.c_name,
                currentframe(),
            )
        self._data[_Keys.CSENDER] = value

    @property
    def title(self) -> Optional[str]:
        """Return optional title string."""
        return self._data[_Keys.CTITLE]

    @title.setter
    def title(self, value: str):
        """Set optional title string."""
        if not isinstance(value, str):
            raise Raise.error(
                f"Expected string type, received '{type(value)}'.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        self._data[_Keys.CTITLE] = value

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
                self.c_name,
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
        Thread.__init__(self, name=self.c_name)
        self._stop_event = Event()
        self.daemon = True
        self.sleep_period = 5.0

        # logging level
        self._debug = debug
        self._verbose = verbose

        # logger client initialization
        self.logs = LoggerClient(queue=qlog, name=self.c_name)

        # communication queue for reading
        self.qcom = qcom

        # communication queues for target modules
        # example:
        # {
        #    level_1: [regisetred_queue1, registered_queue2, ]
        #    level_2: [regisetred_queue3, ]
        # }
        self._data[_Keys.COMQUEUES] = dict()

    def register_queue(self, level: int) -> Queue:
        """Register queue for communication module."""
        if not isinstance(level, (str, int)):
            raise Raise.error(
                f"Expected string or integer type, received '{type(level)}'.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        if str(level) not in self._data[_Keys.COMQUEUES]:
            self._data[_Keys.COMQUEUES][str(level)] = []
        queue = Queue(maxsize=1000)
        if self._debug:
            self.logs.message_debug = f"add queue for communication level: {level}"
        self._data[_Keys.COMQUEUES][str(level)].append(queue)
        return queue

    def run(self) -> None:
        """Main loop."""
        # 1. read qcom
        # 2. dispatch received message object to queues with appropriate communication level
        # 3. loop to 1.
        if self._debug:
            self.logs.message_debug = "Starting loop."

        while not self.stopped:
            try:
                message = self.qcom.get(block=True, timeout=0.1)
                if message is None:
                    continue

                try:
                    self.__dispatch_message(message)
                finally:
                    self.qcom.task_done()

            except Empty:
                pass
            except Exception as ex:
                self.logs.message_critical = f'error while processing message: "{ex}"'

        if self._debug:
            self.logs.message_debug = "Exit from loop."

    def __dispatch_message(self, message: Message) -> None:
        """Put message to queues."""
        if not isinstance(message, Message):
            raise Raise.error(
                f"Expected Message type, received '{type(message)}'.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        if str(message.level) in self._data[_Keys.COMQUEUES]:
            for item in self._data[_Keys.COMQUEUES][str(message.level)]:
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
                f"Received message with unknown level: {message.level}",
                ValueError,
                self.c_name,
                currentframe(),
            )

    def stop(self) -> None:
        """Set stop event."""
        if self._debug:
            self.logs.message_debug = "stop signal received."
        self._stop_event.set()

    @property
    def stopped(self) -> bool:
        """Return stop flag."""
        return self._stop_event.is_set()


# #[EOF]#######################################################################
