# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 14.11.2023

  Purpose: communication module: Email
"""

import time
import smtplib
import ssl
import email

from inspect import currentframe
from typing import Dict, List, Optional, Union, Any
from threading import Thread, Event
from queue import Queue, Empty, Full
from email.message import EmailMessage
from email.utils import make_msgid

from jsktoolbox.libs.base_th import ThBaseObject
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.stringtool.crypto import SimpleCrypto

from libs.base.classes import BModule
from libs.interfaces.modules import IComModule
from libs.base.classes import BModuleConfig
from libs.interfaces.conf import IModuleConfig
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart
from libs.tools.datetool import Timestamp, DateTime

# https://realpython.com/python-send-email/
# https://docs.python.org/3/library/email.examples.html#email-examples
# https://www.tutorialspoint.com/python_network_programming/python_email_messages.htm


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    MODCONF = "__MODULE_CONF__"
    SLEEP_PERIOD = "sleep_period"
    PRIORITY = "priority"
    SMTP_SERVER = "smtp_server"
    SMTP_PORT = "smtp_port"
    SMTP_USER = "smtp_user"
    SMTP_PASS = "smtp_pass"
    ADDRESS_FROM = "address_from"
    ADDRESS_TO = "address_to"


class _ModuleConf(IModuleConfig, BModuleConfig):
    """Module Config private class."""

    def _get(self, varname: str) -> Any:
        """Get variable from config."""
        return self._cfh.get(self._section, varname)

    @property
    def priority(self) -> int:
        """Return priority var."""
        var = self._get(varname=_Keys.PRIORITY)
        if var is not None and not isinstance(var, int):
            raise Raise.error(
                "Expected int type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def sleep_period(self) -> float:
        """Return sleep_period var."""
        var = self._get(varname=_Keys.SLEEP_PERIOD)
        if var is None:
            return None
        if not isinstance(var, (int, float)):
            raise Raise.error(
                "Expected float type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return float(var)

    @property
    def smtp_server(self) -> str:
        """Return smtp_server var."""
        var = self._get(varname=_Keys.SMTP_SERVER)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected str type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def smtp_user(self) -> str:
        """Return smtp_user var."""
        var = self._get(varname=_Keys.SMTP_USER)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected str type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def smtp_pass(self) -> str:
        """Return smtp_pass var."""
        var = self._get(varname=_Keys.SMTP_PASS)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected str type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def address_from(self) -> str:
        """Return address_from var."""
        var = self._get(varname=_Keys.ADDRESS_FROM)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected str type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def address_to(self) -> str:
        """Return address_to var."""
        var = self._get(varname=_Keys.ADDRESS_TO)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected str type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var


class MEmailalert(Thread, ThBaseObject, BModule, IComModule):
    """Email alert module."""

    def __init__(
        self,
        conf: ConfigTool,
        qlog: LoggerQueue,
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
        self._data[_Keys.SMTP_PORT] = None

        # logging level
        self._debug = debug
        self._verbose = verbose

        # logger client initialization
        self.logs = LoggerClient(queue=qlog, name=self._c_name)

    def _apply_config(self) -> bool:
        """Apply config from module_conf"""
        try:
            if self.module_conf.sleep_period is not None:
                self.sleep_period = self.module_conf.sleep_period
            # priority
            if not self.module_conf.priority:
                self.logs.message_critical = "'priority' not set, exiting..."
                self.stop()
            # smtp_server
            if not self.module_conf.smtp_server:
                self.logs.message_critical = (
                    "'smtp_server' not set, exiting..."
                )
                self.stop()
            # smtp_user
            if not self.module_conf.smtp_user:
                self.logs.message_warning = "'smtp_user' not set, it doesn't have to be a mistake, but check..."
            # smtp_pass
            if not self.module_conf.smtp_pass:
                self.logs.message_warning = "'smtp_pass' not set, it doesn't have to be a mistake, but check..."
            # address_from
            if not self.module_conf.address_from:
                self.logs.message_critical = (
                    "'address_from' not set, exiting..."
                )
                self.stop()
            # address_to
            if not self.module_conf.address_to:
                self.logs.message_critical = (
                    "'address_to' not set, exiting..."
                )
                self.stop()

        except Exception as ex:
            self.logs.message_critical = f"[{self._f_name}] {ex}"
            return False
        if self._debug:
            self.logs.message_debug = "configuration processing complete"
        return True

    def __init_smtp(self) -> Optional[Union[smtplib.SMTP, smtplib.SMTP_SSL]]:
        """Try to connect."""
        smtp = None
        if self._data[_Keys.SMTP_PORT] is None:
            ports = [587, 465, 25]
        else:
            ports = [self._data[_Keys.SMTP_PORT]]

        for port in ports:
            if port == 465:
                try:
                    smtp = smtplib.SMTP_SSL(
                        host=self.module_conf.smtp_server,
                        port=port,
                        context=ssl.create_default_context(),
                    )
                    self._data[_Keys.SMTP_PORT] = port
                    break
                except ConnectionRefusedError:
                    continue
                except smtplib.SMTPConnectError:
                    continue
                except Exception as ex:
                    self.logs.message_debug = (
                        f"smtp ssl connection error: {ex}"
                    )
            else:
                try:
                    smtp = smtplib.SMTP(
                        host=self.module_conf.smtp_server, port=port
                    )
                    self._data[_Keys.SMTP_PORT] = port
                    break
                except ConnectionRefusedError:
                    continue
                except smtplib.SMTPConnectError:
                    continue
                except Exception as ex:
                    self.logs.message_debug = f"smtp connection error: {ex}"
        return smtp

    def __send_message(self, message: Message) -> bool:
        """Try to send message."""
        out = False
        # build email message
        msg = EmailMessage()
        if message.subject:
            msg.add_header("Subject", message.subject)
        if message.sender:
            msg.add_header("From", message.sender)
        else:
            msg.add_header("From", self.module_conf.address_from)
        if message.reply_to:
            msg.add_header("Reply-To", message.reply_to)
        if message.to:
            test = False
            cc = []
            for item in message.to:
                if test:
                    cc.append(item)
                else:
                    msg.add_header("To", item)
                    test = True
            if cc:
                msg.add_header("Cc", ", ".join(cc))
        else:
            if isinstance(self.module_conf.address_to, str):
                msg.add_header("To", self.module_conf.address_to)
            elif isinstance(self.module_conf.address_to, (tuple, list)):
                test = False
                cc = []
                for item in self.module_conf.address_to:
                    if test:
                        cc.append(item)
                    else:
                        msg.add_header("To", item)
                        test = True
                if cc:
                    msg.add_header("Cc", ", ".join(cc))
            else:
                self.logs.message_critical = f'cannot build address to: "{self.module_conf.address_to}"'
                return out
        msg.add_header("Message-Id", make_msgid())
        msg.add_header("Date", DateTime.email_date)

        # add email content
        if message.mmessages is not None:
            if Multipart.PLAIN in message.mmessages:
                tmp = ""
                if isinstance(message.mmessages[Multipart.PLAIN], list):
                    for line in message.mmessages[Multipart.PLAIN]:
                        tmp += f"{line}\n"
                elif isinstance(message.mmessages[Multipart.PLAIN], str):
                    tmp += f"{message.mmessages[Multipart.PLAIN]}\n"
                else:
                    self.logs.message_critical = (
                        f"the message format cannot be recognize"
                    )
                    return out
                msg.set_content(tmp, subtype="plain", charset="utf-8")
            if Multipart.HTML in message.mmessages:
                tmp = ""
                if isinstance(message.mmessages[Multipart.HTML], List):
                    for line in message.mmessages[Multipart.HTML]:
                        tmp += f"{line}\n"
                elif isinstance(message.mmessages[Multipart.HTML], str):
                    tmp += f"{message.mmessages[Multipart.HTML]}\n"
                else:
                    self.logs.message_critical = (
                        f"the message format cannot be recognize"
                    )
                    return out
                msg.add_alternative(tmp, subtype="html", charset="utf-8")
        else:
            tmp = ""
            if isinstance(message.messages, List):
                for line in message.messages:
                    tmp += f"{line}\n"
            else:
                self.logs.message_critical = (
                    f"the message format cannot be recognize"
                )
                return out
            self.logs.message_debug = tmp
            msg.set_content(tmp, subtype="plain", charset="utf-8")

        # try to init connection
        smtp = self.__init_smtp()

        if smtp is None:
            self.logs.message_critical = (
                "connection not initialized properly, cannot continue"
            )
            return out

        # try to send message
        try:
            if self._data[_Keys.SMTP_PORT] == 587:
                smtp.ehlo()
                smtp.starttls()
            if self._data[_Keys.SMTP_PORT] != 25:
                salt = self._cfh.get(self._cfh.main_section_name, "salt")
                if salt is not None:
                    password = SimpleCrypto.multiple_decrypt(
                        salt, self.module_conf.smtp_pass
                    )
                else:
                    password = self.module_conf.smtp_pass
                smtp.ehlo()
                smtp.login(
                    self.module_conf.smtp_user,
                    password,
                )
            smtp.send_message(msg)
            if self.debug:
                self.logs.message_debug = "message was send"
            out = True
        except smtplib.SMTPAuthenticationError as ex:
            self.logs.message_critical = f"authentication error: {ex}"
        except ssl.SSLError as ex:
            self.logs.message_critical = f"ssl error: {ex}"
        except smtplib.SMTPSenderRefused as ex:
            self.logs.message_critical = f"sender refused error: {ex}"
        except smtplib.SMTPServerDisconnected as ex:
            self.logs.message_critical = f"server disconnected: {ex}"
        except Exception as ex:
            self.logs.message_critical = f"exception was thrown: {ex}"
        finally:
            try:
                smtp.quit()
            except:
                pass

        return out

    def run(self) -> None:
        """Main loop."""
        # initialize local vars
        deffered_shift = 15 * 60  # 15 minutes
        deffered = deffered_shift + Timestamp.now
        deffered_count = 7 * 24 * 4  # 7 days every 15 minutes
        deffered_queue = Queue(maxsize=500)

        self.logs.message_notice = "starting..."

        # initialization variables from config file
        if not self._apply_config():
            self.logs.message_error = "configuration error"
            return

        # starting module loop
        if self._debug:
            self.logs.message_debug = "entering to the main loop"
        while not self.stopped:
            # read from deffered queue
            if deffered < Timestamp.now:
                tmp = []
                while not self.stopped:
                    try:
                        message: Message = deffered_queue(timeout=0.1)
                        # try to send for deffered_count times
                        if (
                            not self.__send_message(message)
                            and message.counter < deffered_count
                        ):
                            tmp.append(message)

                    except Empty:
                        break
                    except Exception as ex:
                        self.logs.message_critical = (
                            f"error while processing deffered queue: {ex}"
                        )
                deffered = Timestamp.now + deffered_shift
                for item in tmp:
                    deffered_queue.put(item)

            # read from queue, process message if received
            try:
                message: Message = self.qcom.get(block=True, timeout=0.1)
                if message is None:
                    continue
                # try to process message
                if self.debug:
                    self.logs.message_debug = "received message for sending"
                try:
                    if not self.__send_message(message):
                        deffered_queue.put(message)
                except Exception as ex:
                    self.logs.message_warning = "error processing message"
                    if self.debug:
                        self.logs.message_debug = f"[{self._f_name}] {ex}"
                # finally:
                # self.qcom.task_done()

            except Empty:
                pass
            except Exception as ex:
                self.logs.message_critical = (
                    f'error while processing message: "{ex}"'
                )

            time.sleep(self.sleep_period)

        # exiting from loop
        self.logs.message_notice = "exit"

    def stop(self) -> None:
        """Set stop event."""
        if self._debug:
            self.logs.message_debug = "stop signal received"
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
        out.append(
            TemplateConfigItem(desc="Email alert configuration module.")
        )
        out.append(TemplateConfigItem(desc="Variables:"))
        out.append(
            TemplateConfigItem(
                desc=f"{_Keys.PRIORITY} [int] - unique priority for communication method (default: 1)"
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"{_Keys.SMTP_SERVER} [str] - server for outgoing emails."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"{_Keys.SMTP_USER} [str] - smtp auth user for sending emails."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"{_Keys.SMTP_PASS} [str] - smtp auth password for sending emails."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"{_Keys.ADDRESS_FROM} [str] - email from address, for example: 'no-reply@ltd',"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="may be overrited by Message class properties if set."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"{_Keys.ADDRESS_TO} [list] - destination list of emails,"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="may be overrited by Message class properties if set."
            )
        )
        out.append(TemplateConfigItem(varname=_Keys.PRIORITY, value=1))
        out.append(TemplateConfigItem(varname=_Keys.SMTP_SERVER))
        out.append(TemplateConfigItem(varname=_Keys.SMTP_USER))
        out.append(TemplateConfigItem(varname=_Keys.SMTP_PASS))
        out.append(TemplateConfigItem(varname=_Keys.ADDRESS_FROM))
        out.append(TemplateConfigItem(varname=_Keys.ADDRESS_TO))

        return out


# #[EOF]#######################################################################
