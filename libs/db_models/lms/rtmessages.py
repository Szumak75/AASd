# -*- coding: UTF-8 -*-
"""
Created on 7 oct 2020

@author: szumak@virthost.pl
"""

from sqlalchemy import ForeignKey, Integer, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import (
    DECIMAL,
    INTEGER,
    MEDIUMTEXT,
    SMALLINT,
    TEXT,
    TINYINT,
    VARCHAR,
)

from libs.db_models.base import LmsBase


class RtMessage(LmsBase):
    __tablename__ = "rtmessages"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `ticketid` int(11) NOT NULL,
    ticketid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `userid` int(11) DEFAULT NULL,
    userid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `customerid` int(11) DEFAULT NULL,
    customerid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `phonefrom` varchar(20) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    phonefrom: Mapped[str] = mapped_column(
        VARCHAR(20), nullable=False, default=""
    )
    # `mailfrom` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    mailfrom: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `subject` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    subject: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `messageid` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    messageid: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `inreplyto` int(11) DEFAULT NULL,
    inreplyto: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `replyto` text COLLATE utf8_polish_ci NOT NULL,
    replyto: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `headers` text COLLATE utf8_polish_ci NOT NULL,
    headers: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `body` mediumtext COLLATE utf8_polish_ci NOT NULL,
    body: Mapped[str] = mapped_column(MEDIUMTEXT(), nullable=False)
    # `createtime` int(11) NOT NULL DEFAULT '0',
    createtime: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `type` smallint(6) NOT NULL DEFAULT '0',
    type: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=0)
    # `deleted` tinyint(1) NOT NULL DEFAULT '0',
    deleted: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # `deltime` int(11) NOT NULL DEFAULT '0',
    deltime: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `deluserid` int(11) DEFAULT NULL,
    deluserid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # PRIMARY KEY (`id`),
    # KEY `ticketid` (`ticketid`),
    # KEY `rtmessages_customerid_fkey` (`customerid`),
    # KEY `rtmessages_userid_fkey` (`userid`),
    # KEY `rtmessages_deluserid_fkey` (`deluserid`),
    # KEY `rtmessages_inreplyto_fkey` (`inreplyto`),
    # CONSTRAINT `rtmessages_customerid_fkey` FOREIGN KEY (`customerid`) REFERENCES `customers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `rtmessages_deluserid_fkey` FOREIGN KEY (`deluserid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `rtmessages_inreplyto_fkey` FOREIGN KEY (`inreplyto`) REFERENCES `rtmessages` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `rtmessages_ticketid_fkey` FOREIGN KEY (`ticketid`) REFERENCES `rttickets` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `rtmessages_userid_fkey` FOREIGN KEY (`userid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"RtMessage(id='{self.id}', "
            f"ticketid='{self.ticketid}', "
            f"userid='{self.userid}', "
            f"customerid='{self.customerid}', "
            f"phonefrom='{self.phonefrom}', "
            f"mailfrom='{self.mailfrom}', "
            f"subject='{self.subject}', "
            f"messageid='{self.messageid}', "
            f"inreplyto='{self.inreplyto}', "
            f"replyto='{self.replyto}', "
            f"headers='{self.headers}', "
            f"body='{self.body}', "
            f"createtime='{self.createtime}', "
            f"type='{self.type}', "
            f"deleted='{self.deleted}', "
            f"deltime='{self.deltime}', "
            f"deluserid='{self.deluserid}' ) "
        )
