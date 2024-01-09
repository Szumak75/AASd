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


class RtAttachment(LmsBase):
    __tablename__ = "rtattachments"

    # dummy primary key
    rowid: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    # `messageid` int(11) NOT NULL,
    messageid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `filename` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    filename: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # `contenttype` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    contenttype: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # KEY `messageid` (`messageid`),
    # CONSTRAINT `rtattachments_ibfk_1` FOREIGN KEY (`messageid`) REFERENCES `rtmessages` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self) -> str:
        return (
            f"RtAttachment(messageid='{self.messageid}', "
            f"filename='{self.filename}', "
            f"contenttype='{self.contenttype}' ) "
        )
