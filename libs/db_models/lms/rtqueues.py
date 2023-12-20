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


class RtQueue(LmsBase):
    __tablename__ = "rtqueues"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # `email` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    email: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # `description` text COLLATE utf8_polish_ci NOT NULL,
    description: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `newticketsubject` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    newticketsubject: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `newticketbody` text COLLATE utf8_polish_ci NOT NULL,
    newticketbody: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `newmessagesubject` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    newmessagesubject: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `newmessagebody` text COLLATE utf8_polish_ci NOT NULL,
    newmessagebody: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `resolveticketsubject` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    resolveticketsubject: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `resolveticketbody` text COLLATE utf8_polish_ci NOT NULL,
    resolveticketbody: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `deleted` tinyint(1) NOT NULL DEFAULT '0',
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, default=0)
    # `deltime` int(11) NOT NULL DEFAULT '0',
    deltime: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `deluserid` int(11) DEFAULT NULL,
    deluserid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `name` (`name`),
    # KEY `rtqueues_deluserid_fkey` (`deluserid`),
    # CONSTRAINT `rtqueues_deluserid_fkey` FOREIGN KEY (`deluserid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"RtQueue(id='{self.id}', "
            f"name='{self.name}', "
            f"email='{self.email}', "
            f"description='{self.description}', "
            f"newticketsubject='{self.newticketsubject}', "
            f"newticketbody='{self.newticketbody}', "
            f"newmessagesubject='{self.newmessagesubject}', "
            f"newmessagebody='{self.newmessagebody}', "
            f"resolveticketsubject='{self.resolveticketsubject}', "
            f"resolveticketbody='{self.resolveticketbody}', "
            f"deleted='{self.deleted}', "
            f"deltime='{self.deltime}', "
            f"deluserid='{self.deluserid}' ) "
        )
