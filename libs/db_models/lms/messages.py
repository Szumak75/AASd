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


class Message(LmsBase):
    __tablename__ = "messages"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `subject` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    subject: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `body` text COLLATE utf8_polish_ci NOT NULL,
    body: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `cdate` int(11) NOT NULL DEFAULT '0',
    cdate: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `type` smallint(6) NOT NULL DEFAULT '0',
    type: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=0)
    # `userid` int(11) DEFAULT NULL,
    userid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `sender` varchar(255) COLLATE utf8_polish_ci DEFAULT NULL,
    sender: Mapped[str] = mapped_column(VARCHAR(255), default=None)
    # PRIMARY KEY (`id`),
    # KEY `cdate` (`cdate`,`type`),
    # KEY `userid` (`userid`),
    # CONSTRAINT `messages_userid_fkey` FOREIGN KEY (`userid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"Message(id='{self.id}', "
            f"subject='{self.subject}', "
            f"body='{self.body}', "
            f"cdate='{self.cdate}', "
            f"type='{self.type}', "
            f"userid='{self.userid}', "
            f"sender='{self.sender}' ) "
        )
