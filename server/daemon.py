# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 06.11.2023

  Purpose: Daemon main class.
"""

from inspect import currentframe

from jsktoolbox.attribtool import NoDynamicAttributes
from jsktoolbox.raisetool import Raise
from jsktoolbox.logstool.logs import (
    LoggerEngine,
    LoggerClient,
    LoggerEngineFile,
    LoggerEngineStderr,
    LoggerEngineStdout,
    LoggerEngineSyslog,
    LoggerQueue,
)
from jsktoolbox.libs.system import CommandLineParser


class AASd(NoDynamicAttributes):
    """"""

    def __init__(self):
        """Constructor."""


# #[EOF]#######################################################################
