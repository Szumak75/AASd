# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 13.11.2023

  Purpose: ICMP testing tools.
"""

import os
import subprocess

from inspect import currentframe
from distutils.spawn import find_executable
from typing import Optional, Dict, List

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.netaddresstool.ipv4 import Address

from libs.base.classes import BClasses


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    TIMEOUT = "__timeout__"
    COMMANDS = "__commands__"
    COMMAND = "__command_found__"
    CMD = "cmd"
    OPTS = "opts"


class Pinger(BClasses):
    """Pinger class for testing ICMP echo."""

    def __init__(self, timeout: int = 1) -> None:
        """Constructor."""
        if not isinstance(timeout, int):
            raise Raise.error(
                f"Expected Integer type, received: '{type(timeout)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self._data[_Keys.TIMEOUT] = timeout
        self._data[_Keys.COMMANDS] = []
        self._data[_Keys.COMMANDS].append(
            {
                _Keys.CMD: "fping",
                _Keys.OPTS: "-AaqR -B1 -r2 -t{} {} >/dev/null 2>&1",
            }
        )
        self._data[_Keys.COMMANDS].append(
            {
                _Keys.CMD: "ping",
                _Keys.OPTS: "-Qqo -c3 -W{} {} >/dev/null 2>&1",
            }
        )
        self._data[_Keys.COMMAND] = self.__is_tool

    def is_alive(self, ip: str) -> bool:
        """Check ICMP echo response."""
        if self._data[_Keys.COMMAND] is None:
            raise Raise.error(
                "Command for testing ICMP echo not found.",
                ChildProcessError,
                self._c_name,
                currentframe(),
            )
        if (
            os.system(
                self._data[_Keys.COMMAND].format(
                    int(self._data[_Keys.TIMEOUT] * 1000), str(Address(ip))
                )
            )
        ) == 0:
            return True
        return False

    @property
    def __is_tool(self) -> Optional[str]:
        """Check system command."""
        for cmd in self._data[_Keys.COMMANDS]:
            if find_executable(cmd[_Keys.CMD]) is not None:
                test_cmd = f"{cmd[_Keys.CMD]} {cmd[_Keys.OPTS]}"
                if (
                    os.system(
                        test_cmd.format(
                            int(self._data[_Keys.TIMEOUT] * 10), "127.0.0.1"
                        )
                    )
                    == 0
                ):
                    return test_cmd
        return None


class Tracert(BClasses):
    """Tracert class for testing route to IPv4 address."""

    def __init__(self):
        """Constructor."""
        self._data[_Keys.COMMANDS] = []
        self._data[_Keys.COMMANDS].append(
            {
                _Keys.CMD: "traceroute",
                _Keys.OPTS: "-I -q2 -S -e -w1 -n -m 10",
            }
        )
        self._data[_Keys.COMMANDS].append(
            {
                _Keys.CMD: "traceroute",
                _Keys.OPTS: "-P UDP -q2 -S -e -w1 -n -m 10",
            }
        )
        self._data[_Keys.COMMANDS].append(
            {
                _Keys.CMD: "traceroute",
                _Keys.OPTS: "-I -q2 -e -w1 -n -m 10",
            }
        )
        self._data[_Keys.COMMANDS].append(
            {
                _Keys.CMD: "traceroute",
                _Keys.OPTS: "-U -q2 -e -w1 -n -m 10",
            }
        )
        self._data[_Keys.COMMAND] = self.__is_tool

    @property
    def __is_tool(self) -> Optional[Dict]:
        """Check system commend."""
        for cmd in self._data[_Keys.COMMANDS]:
            if find_executable(cmd[_Keys.CMD]) is not None:
                if (
                    os.system(
                        "{} {} {} > /dev/null 2>&1".format(
                            cmd[_Keys.CMD], cmd[_Keys.OPTS], "127.0.0.1"
                        )
                    )
                    == 0
                ):
                    out = {}
                    out.update(cmd)
                    return out
        return None

    def execute(self, ip: str) -> List:
        """Traceroute to given IPv4 address."""
        if self._data[_Keys.COMMAND] is None:
            raise Raise.error(
                "Command for testing ICMP echo not found.",
                ChildProcessError,
                self._c_name,
                currentframe(),
            )
        out = []
        args = []
        args.append(self._data[_Keys.COMMAND][_Keys.CMD])
        args.extend(self._data[_Keys.COMMAND][_Keys.OPTS].split(" "))
        args.append(str(Address(ip)))

        with subprocess.Popen(
            args,
            env={
                "PATH": "/bin:/sbin:/usr/bin:/usr/sbin",
            },
            stdout=subprocess.PIPE,
        ) as proc:
            for line in proc.stdout:
                out.append(line.decode("utf-8"))
        return out


# #[EOF]#######################################################################
