# -*- coding: UTF-8 -*-
"""
Created on 6 oct 2020

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


class AliasAssignment(LmsBase):
    __tablename__ = "aliasassignments"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `aliasid` int(11) NOT NULL,
    aliasid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `accountid` int(11) DEFAULT NULL,
    accountid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `mail_forward` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    mail_forward: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `aliasid` (`aliasid`,`accountid`,`mail_forward`),
    # KEY `aliasassignments_accountid_fkey` (`accountid`),
    # CONSTRAINT `aliasassignments_accountid_fkey` FOREIGN KEY (`accountid`) REFERENCES `passwd` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `aliasassignments_aliasid_fkey` FOREIGN KEY (`aliasid`) REFERENCES `aliases` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"AliasAssignment(id='{self.id}', "
            f"aliasid='{self.aliasid}', "
            f"accountid='{self.accountid}', "
            f"mail_forward='{self.mail_forward}' ) "
        )
