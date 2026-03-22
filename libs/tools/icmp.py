# -*- coding: UTF-8 -*-
"""
ICMP and traceroute helpers.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-11-13

Purpose: Provide shell-based helpers for ICMP reachability and traceroute tests.
"""

import os
import subprocess

from inspect import currentframe
from distutils.spawn import find_executable
from typing import Optional, Dict, List

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.netaddresstool import Address
from jsktoolbox.basetool import BData


class _Keys(object, metaclass=ReadOnlyClass):
    """Define internal storage keys for ICMP and traceroute helpers."""

    # #[CONSTANTS]####################################################################
    CMD: str = "cmd"
    COMMAND: str = "__command_found__"
    COMMANDS: str = "__commands__"
    MULTIPLIER: str = "__multiplier__"
    OPTS: str = "opts"
    TIMEOUT: str = "__timeout__"


class Pinger(BData):
    """Check IPv4 reachability using system ICMP tools."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self, timeout: int = 1) -> None:
        """Initialize the ICMP helper.

        ### Arguments:
        * timeout: int - Timeout in seconds used by the underlying command.
        """
        self._set_data(key=_Keys.TIMEOUT, value=timeout, set_default_type=int)
        self._set_data(key=_Keys.MULTIPLIER, value=1, set_default_type=int)

        commands: List[Dict] = []

        # BSD fping
        commands.append(
            {
                _Keys.CMD: "fping",
                _Keys.MULTIPLIER: 1000,
                _Keys.OPTS: "-AaqR -B1 -r2 -t{} {} >/dev/null 2>&1",
            }
        )
        # FreeBSD ping
        commands.append(
            {
                _Keys.CMD: "ping",
                _Keys.MULTIPLIER: 1000,
                _Keys.OPTS: "-Qqo -c3 -W{} {} >/dev/null 2>&1",
            }
        )
        # Linux ping
        commands.append(
            {
                _Keys.CMD: "ping",
                _Keys.MULTIPLIER: 1,
                _Keys.OPTS: "-q -c3 -W{} {} >/dev/null 2>&1",
            }
        )
        self._set_data(key=_Keys.COMMANDS, value=commands, set_default_type=List[Dict])

        # Detect a working command and store it for later use.
        tmp: Optional[tuple] = self.__is_tool
        if tmp:
            (command, multiplier) = tmp
            self._set_data(key=_Keys.COMMAND, value=command, set_default_type=str)
            self._set_data(key=_Keys.MULTIPLIER, value=multiplier)

    # #[PUBLIC METHODS]###############################################################
    def is_alive(self, ip: str) -> bool:
        """Check whether the target IPv4 address responds to ICMP echo.

        ### Arguments:
        * ip: str - IPv4 address to test.

        ### Returns:
        bool - `True` when the target host responds.

        ### Raises:
        * ChildProcessError: If no supported ICMP command is available.
        """
        command: Optional[str] = self._get_data(key=_Keys.COMMAND)

        # Get timeout value
        obj: Optional[int] = self._get_data(key=_Keys.TIMEOUT)
        if obj is None:
            raise Raise.error(
                "Timeout value for ICMP command not found.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        timeout: int = obj

        # Get multiplier value
        obj = self._get_data(key=_Keys.MULTIPLIER)
        if obj is None:
            raise Raise.error(
                "Timeout multiplier for ICMP command not found.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        multiplier: int = obj

        if command is None:
            raise Raise.error(
                "Command for testing ICMP echo not found.",
                ChildProcessError,
                self._c_name,
                currentframe(),
            )
        if (
            os.system(
                command.format(
                    int(timeout * multiplier),
                    str(Address(ip)),
                )
            )
        ) == 0:
            return True
        return False

    # #[PRIVATE PROPERTIES]###########################################################
    @property
    def __is_tool(self) -> Optional[tuple]:
        """Find a working ICMP command implementation.

        ### Returns:
        Optional[tuple] - Command template and timeout multiplier or `None`.
        """
        commands: Optional[List[Dict]] = self._get_data(key=_Keys.COMMANDS, default=[])
        if commands is None:
            commands = []

        for cmd in commands:
            if find_executable(cmd[_Keys.CMD]) is not None:
                test_cmd: str = f"{cmd[_Keys.CMD]} {cmd[_Keys.OPTS]}"
                multiplier: int = cmd[_Keys.MULTIPLIER]
                timeout: Optional[int] = self._get_data(key=_Keys.TIMEOUT)
                if timeout is None:
                    timeout = 1
                if (
                    os.system(
                        test_cmd.format(
                            int(timeout * multiplier),
                            "127.0.0.1",
                        )
                    )
                    == 0
                ):
                    return test_cmd, multiplier
        return None


class Tracert(BData):
    """Execute traceroute against an IPv4 address using system tools."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self) -> None:
        """Initialize the traceroute helper and detect a working command."""

        commands: List[Dict] = []

        commands.append(
            {
                _Keys.CMD: "traceroute",
                _Keys.OPTS: "-I -q2 -S -e -w1 -n -m 10",
            }
        )
        commands.append(
            {
                _Keys.CMD: "traceroute",
                _Keys.OPTS: "-P UDP -q2 -S -e -w1 -n -m 10",
            }
        )
        commands.append(
            {
                _Keys.CMD: "traceroute",
                _Keys.OPTS: "-I -q2 -e -w1 -n -m 10",
            }
        )
        commands.append(
            {
                _Keys.CMD: "traceroute",
                _Keys.OPTS: "-U -q2 -e -w1 -n -m 10",
            }
        )

        self._set_data(key=_Keys.COMMANDS, value=commands, set_default_type=List)
        self._set_data(
            key=_Keys.COMMAND, value=self.__is_tool, set_default_type=Optional[Dict]
        )

    # #[PUBLIC METHODS]###############################################################
    def execute(self, ip: str) -> List[str]:
        """Execute traceroute for the selected IPv4 address.

        ### Arguments:
        * ip: str - IPv4 address to trace.

        ### Returns:
        List[str] - Raw traceroute output lines.

        ### Raises:
        * ChildProcessError: If no supported traceroute command is available.
        """
        command: Optional[Dict] = self._get_data(key=_Keys.COMMAND)
        if command is None:
            raise Raise.error(
                "Command for testing ICMP echo not found.",
                ChildProcessError,
                self._c_name,
                currentframe(),
            )
        out: List[str] = []
        args: List[str] = []
        args.append(command[_Keys.CMD])
        args.extend(command[_Keys.OPTS].split(" "))
        args.append(str(Address(ip)))

        with subprocess.Popen(
            args,
            env={
                "PATH": "/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin",
            },
            stdout=subprocess.PIPE,
        ) as proc:
            if proc.stdout is not None:
                for line in proc.stdout:
                    out.append(line.decode("utf-8"))
        return out

    # #[PRIVATE PROPERTIES]###########################################################
    @property
    def __is_tool(self) -> Optional[Dict]:
        """Find a working traceroute command implementation.

        ### Returns:
        Optional[Dict] - Command descriptor or `None`.
        """
        commands: Optional[List[Dict]] = self._get_data(key=_Keys.COMMANDS, default=[])
        if commands is None:
            commands = []

        for cmd in commands:
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


# #[EOF]#######################################################################
