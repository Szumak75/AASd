# -*- coding: UTF-8 -*-
"""
Created on 17 nov 2020

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


class UpCustomer(LmsBase):
    __tablename__ = "up_customers"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `customerid` int(11) DEFAULT NULL,
    customerid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `lastlogindate` int(11) NOT NULL DEFAULT '0',
    lastlogindate: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `lastloginip` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    lastloginip: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="")
    # `failedlogindate` int(11) NOT NULL DEFAULT '0',
    failedlogindate: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `failedloginip` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    failedloginip: Mapped[str] = mapped_column(VARCHAR(11), nullable=False, default="")
    # `enabled` int(10) NOT NULL DEFAULT '0',
    enabled: Mapped[int] = mapped_column(INTEGER(10), nullable=False, default=0)

    def __repr__(self) -> str:
        return (
            f"UpCustomer(id='{self.id}', "
            f"customerid='{self.customerid}', "
            f"lastlogindate='{self.lastlogindate}', "
            f"lastloginip='{self.lastloginip}', "
            f"failedlogindate='{self.failedlogindate}', "
            f"failedloginip='{self.failedloginip}', "
            f"enabled='{self.enabled}' ) "
        )
