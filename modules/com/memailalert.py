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

from jsktoolbox.basetool.threads import ThBaseObject
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.stringtool.crypto import SimpleCrypto
from jsktoolbox.datetool import Timestamp

from libs.base.classes import BModule
from libs.interfaces.modules import IComModule
from libs.base.classes import BModuleConfig
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart
from libs.tools.datetool import MDateTime
from libs.app import AppName

# https://realpython.com/python-send-email/
# https://docs.python.org/3/library/email.examples.html#email-examples
# https://www.tutorialspoint.com/python_network_programming/python_email_messages.htm


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    ADDRESS_FROM: str = "address_from"
    ADDRESS_TO: str = "address_to"
    DEBUG_BCC: str = "debug_bcc"
    SMTP_PASS: str = "smtp_pass"
    SMTP_PORT: str = "smtp_port"
    SMTP_SERVER: str = "smtp_server"
    SMTP_USER: str = "smtp_user"


class _ModuleConf(BModuleConfig):
    """Module Config private class."""

    @property
    def smtp_server(self) -> Optional[str]:
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
    def smtp_user(self) -> Optional[str]:
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
    def smtp_pass(self) -> Optional[str]:
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
    def address_from(self) -> Optional[str]:
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
    def address_to(self) -> Optional[Union[List, str]]:
        """Return address_to var."""
        var = self._get(varname=_Keys.ADDRESS_TO)
        if var is not None and not isinstance(var, (str, List)):
            raise Raise.error(
                "Expected str or list type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def debug_bcc(self) -> Optional[Union[List, str]]:
        """Return debug_bcc var."""
        var = self._get(varname=_Keys.DEBUG_BCC)
        if var is not None and not isinstance(var, (str, List)):
            raise Raise.error(
                "Expected str or list type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var


class MEmailalert(Thread, ThBaseObject, BModule, IComModule):
    """Email alert module."""

    def __init__(
        self,
        app_name: AppName,
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
        self.application = app_name
        self._section = self._c_name
        self._cfh = conf
        self._module_conf = _ModuleConf(self._cfh, self._section)
        self._set_data(key=_Keys.SMTP_PORT, value=None, set_default_type=Optional[int])

        # logging level
        self._bm_debug = debug
        self._verbose = verbose

        # logger client initialization
        self.logs = LoggerClient(queue=qlog, name=self._c_name)

    def _apply_config(self) -> bool:
        """Apply config from module_conf"""
        if self.module_conf is None:
            return False
        try:
            if self.module_conf.sleep_period is not None:
                self.sleep_period = self.module_conf.sleep_period
            # channel
            if self.module_conf.channel is None:
                self.logs.message_critical = (
                    f"'{_ModuleConf.Keys.CHANNEL}' not set, exiting..."
                )
                self.stop()
            # smtp_server
            if not self.module_conf.smtp_server:
                self.logs.message_critical = (
                    f"'{_Keys.SMTP_SERVER}' not set, exiting..."
                )
                self.stop()
            # smtp_user
            if not self.module_conf.smtp_user:
                self.logs.message_warning = f"'{_Keys.SMTP_USER}' not set, it doesn't have to be a mistake, but check..."
            # smtp_pass
            if not self.module_conf.smtp_pass:
                self.logs.message_warning = f"'{_Keys.SMTP_PASS}' not set, it doesn't have to be a mistake, but check..."
            # address_from
            if not self.module_conf.address_from:
                self.logs.message_critical = (
                    f"'{_Keys.ADDRESS_FROM}' not set, exiting..."
                )
                self.stop()
            # address_to
            if not self.module_conf.address_to:
                self.logs.message_critical = f"'{_Keys.ADDRESS_TO}' not set, exiting..."
                self.stop()
            # debug_bcc
            if not self.module_conf.debug_bcc:
                self.logs.message_notice = f"'{_Keys.DEBUG_BCC}' is not set."
            else:
                self.logs.message_notice = f"'{_Keys.DEBUG_BCC}' is set."

        except Exception as ex:
            self.logs.message_critical = f"[{self._f_name}] {ex}"
            return False
        if self.debug:
            self.logs.message_debug = "configuration processing complete"
        return True

    def __init_smtp(self) -> Optional[Union[smtplib.SMTP, smtplib.SMTP_SSL]]:
        """Try to connect."""
        if self.module_conf is None or self.module_conf.smtp_server is None:
            return None
        smtp = None
        if self._get_data(key=_Keys.SMTP_PORT) is None:
            ports: List[int] = [587, 465, 25]
        else:
            ports = [self._get_data(key=_Keys.SMTP_PORT)]  # type: ignore

        for port in ports:
            if port == 465:
                try:
                    smtp = smtplib.SMTP_SSL(
                        host=self.module_conf.smtp_server,
                        port=port,
                        context=ssl.create_default_context(),
                    )
                    self._set_data(key=_Keys.SMTP_PORT, value=port)
                    break
                except ConnectionRefusedError:
                    continue
                except smtplib.SMTPConnectError:
                    continue
                except Exception as ex:
                    self.logs.message_debug = f"smtp ssl connection error: {ex}"
            else:
                try:
                    smtp = smtplib.SMTP(host=self.module_conf.smtp_server, port=port)
                    self._set_data(key=_Keys.SMTP_PORT, value=port)
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
        if (
            self.module_conf is None
            or self.module_conf.address_from is None
            or self._cfh is None
            or self._cfh.main_section_name is None
            or self.module_conf.smtp_pass is None
            or self.module_conf.smtp_user is None
        ):
            return False
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
            cc: List[str] = []
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
                cc: List[str] = []
                for item in self.module_conf.address_to:
                    if test:
                        cc.append(item)
                    else:
                        msg.add_header("To", item)
                        test = True
                if cc:
                    msg.add_header("Cc", ", ".join(cc))
            else:
                self.logs.message_critical = (
                    f'cannot build address to: "{self.module_conf.address_to}"'
                )
                return out

        # add debug emails if configured
        if self.module_conf.debug_bcc:
            if isinstance(self.module_conf.debug_bcc, str):
                msg.add_header("Bcc", self.module_conf.debug_bcc)
            elif isinstance(self.module_conf.debug_bcc, list):
                bcc: List[str] = []
                for item in self.module_conf.debug_bcc:
                    bcc.append(item)
                msg.add_header("Bcc", ", ".join(bcc))

        msg.add_header("Message-Id", make_msgid())
        msg.add_header("Date", MDateTime.email_date())

        # add email content
        if message.mmessages is not None:
            if Multipart.PLAIN in message.mmessages:
                tmp: str = ""
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
                if message.footer:
                    tmp += "\n-- \n" + message.footer + "\n"
                msg.set_content(tmp, subtype="plain", charset="utf-8")
            if Multipart.HTML in message.mmessages:
                tmp: str = ""
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
            tmp: str = ""
            if isinstance(message.messages, List):
                for line in message.messages:
                    tmp += f"{line}\n"
                if message.footer:
                    tmp += "\n-- \n" + message.footer + "\n"
            else:
                self.logs.message_critical = f"the message format cannot be recognize"
                return out
            # self.logs.message_debug = tmp
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
            if self._get_data(key=_Keys.SMTP_PORT) == 587:
                smtp.ehlo()
                smtp.starttls()
            if self._get_data(key=_Keys.SMTP_PORT) != 25:
                salt = self._cfh.get(self._cfh.main_section_name, "salt")
                if salt is not None:
                    password: str = SimpleCrypto.multiple_decrypt(
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

            # logs notice
            notice: List = []
            if msg.get("To") is not None:
                notice.append(msg.get("To"))
            if msg.get("Cc") is not None:
                notice.append(msg.get("Cc"))
            self.logs.message_notice = f"message was send to: {', '.join(notice)}"
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
        deferred_shift: int = 15 * 60  # 15 minutes
        deferred = deferred_shift + Timestamp.now()
        deferred_count: int = 7 * 24 * 4  # 7 days every 15 minutes
        deferred_queue = Queue(maxsize=1500)

        self.logs.message_notice = "starting..."

        # initialization variables from config file
        if not self._apply_config():
            self.logs.message_error = "configuration error"
            return

        # starting module loop
        if self.debug:
            self.logs.message_debug = "entering to the main loop"

        if self.qcom is None:
            return None

        while not self._stopped:
            # read from deferred queue
            if deferred < Timestamp.now():
                tmp: List[Message] = []
                while not self._stopped:
                    try:
                        message: Message = deferred_queue.get_nowait()
                        if message is None:
                            break
                        if self.debug:
                            self.logs.message_debug = "found deferred message"
                        # try to send for deferred_count times
                        if (
                            not self.__send_message(message)
                            and message.counter < deferred_count
                        ):
                            if self.debug:
                                self.logs.message_debug = (
                                    "deferred message not sent, retry..."
                                )
                            tmp.append(message)

                    except Empty:
                        break
                    except Exception as ex:
                        self.logs.message_critical = (
                            f"error while processing deferred queue: {ex}"
                        )
                        break
                deferred = Timestamp.now() + deferred_shift
                for item in tmp:
                    if not deferred_queue.full():
                        deferred_queue.put(item)

            # read from queue, process message if received
            if self.debug and self.verbose:
                self.logs.message_debug = "check comms queue"
            try:
                message: Message = self.qcom.get(block=True, timeout=0.1)
                if message is None:
                    if self.debug and self.verbose:
                        self.logs.message_debug = "comms queue timeout, continue"
                else:
                    # try to process message
                    self.qcom.task_done()
                    if self.debug:
                        self.logs.message_debug = "received message for sending"
                    try:
                        if not self.__send_message(message):
                            if self.debug:
                                self.logs.message_debug = "deferred message"
                            if not deferred_queue.full():
                                deferred_queue.put(message)
                        else:
                            continue
                    except Exception as ex:
                        self.logs.message_warning = "error processing message"
                        if self.debug:
                            self.logs.message_debug = f"[{self._f_name}] {ex}"
            except Empty:
                pass
            except Exception as ex:
                self.logs.message_critical = f'error while processing message: "{ex}"'

            self.sleep()

        # exiting from loop
        self.logs.message_notice = "exit"

    def sleep(self) -> None:
        """Sleep interval for main loop."""
        sleep_break: float = Timestamp.now() + self.sleep_period
        while not self._stopped and sleep_break > Timestamp.now():
            time.sleep(0.2)

    def stop(self) -> None:
        """Set stop event."""
        if self.debug:
            self.logs.message_debug = "stop signal received"
        if self._stop_event:
            self._stop_event.set()

    @property
    def debug(self) -> bool:
        """Return debug flag."""
        if self._bm_debug is not None:
            return self._bm_debug
        return False

    @property
    def verbose(self) -> bool:
        """Return verbose flag."""
        return self._verbose

    @property
    def _stopped(self) -> bool:
        """Return stop flag."""
        if self._stop_event:
            return self._stop_event.is_set()
        return True

    @property
    def module_stopped(self) -> bool:
        """Return stop flag."""
        return self._is_stopped  # type: ignore

    @property
    def module_conf(self) -> Optional[_ModuleConf]:
        """Return module conf object."""
        return self._module_conf  # type: ignore

    @classmethod
    def template_module_name(cls) -> str:
        """Return module name for configuration builder."""
        return cls.__name__.lower()

    @classmethod
    def template_module_variables(cls) -> List[TemplateConfigItem]:
        """Return configuration variables template."""
        out: List[TemplateConfigItem] = []
        # item format:
        # TemplateConfigItem()
        out.append(TemplateConfigItem(desc="Email alert configuration module."))
        out.append(TemplateConfigItem(desc="Variables:"))
        out.append(
            TemplateConfigItem(
                desc=f"{_ModuleConf.Keys.CHANNEL} [int] - unique channel for communication method (default: 1)"
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
                desc="can be overridden by properties of the Message class if set."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"{_Keys.ADDRESS_TO} [list] - destination list of emails,"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="can be overridden by properties of the Message class if set."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"{_Keys.DEBUG_BCC} [list] - target debug email list added as BCC,"
            )
        )

        out.append(TemplateConfigItem(varname=_ModuleConf.Keys.CHANNEL, value=1))
        out.append(TemplateConfigItem(varname=_Keys.SMTP_SERVER))
        out.append(TemplateConfigItem(varname=_Keys.SMTP_USER))
        out.append(TemplateConfigItem(varname=_Keys.SMTP_PASS))
        out.append(TemplateConfigItem(varname=_Keys.ADDRESS_FROM))
        out.append(TemplateConfigItem(varname=_Keys.ADDRESS_TO, value=[]))
        out.append(TemplateConfigItem(varname=_Keys.DEBUG_BCC, value=None))
        return out


# #[EOF]#######################################################################
