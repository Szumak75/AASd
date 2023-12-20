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


class MessageItem(LmsBase):
    __tablename__ = "messageitems"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `messageid` int(11) NOT NULL,
    messageid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `customerid` int(11) DEFAULT NULL,
    customerid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `destination` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    destination: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # `lastdate` int(11) NOT NULL DEFAULT '0',
    lastdate: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `status` smallint(6) NOT NULL DEFAULT '0',
    status: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=0)
    # `error` text COLLATE utf8_polish_ci,
    error: Mapped[str] = mapped_column(TEXT())
    # `lastreaddate` int(11) NOT NULL DEFAULT '0',
    lastreaddate: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `externalmsgid` int(6) NOT NULL DEFAULT '0',
    externalmsgid: Mapped[int] = mapped_column(INTEGER(6), nullable=False, default=0)
    # PRIMARY KEY (`id`),
    # KEY `messageid` (`messageid`),
    # KEY `customerid` (`customerid`),
    # CONSTRAINT `messageitems_customerid_fkey` FOREIGN KEY (`customerid`) REFERENCES `customers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `messageitems_messageid_fkey` FOREIGN KEY (`messageid`) REFERENCES `messages` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"MessageItem(id='{self.id}', "
            f"messageid='{self.messageid}', "
            f"customerid='{self.customerid}', "
            f"destination='{self.destination}', "
            f"lastdate='{self.lastdate}', "
            f"status='{self.status}', "
            f"error='{self.error}', "
            f"lastreaddate='{self.lastreaddate}', "
            f"externalmsgid='{self.externalmsgid}' ) "
        )
