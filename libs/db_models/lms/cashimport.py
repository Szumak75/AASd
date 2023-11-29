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


class CashImport(LmsBase):
    __tablename__ = "cashimport"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `date` int(11) NOT NULL DEFAULT '0',
    date: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `value` decimal(9,2) NOT NULL DEFAULT '0.00',
    value: Mapped[float] = mapped_column(
        DECIMAL(9, 2), nullable=False, default=0.00
    )
    # `customer` text COLLATE utf8_polish_ci NOT NULL,
    customer: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `description` text COLLATE utf8_polish_ci NOT NULL,
    description: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `customerid` int(11) DEFAULT NULL,
    customerid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `hash` varchar(50) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    hash: Mapped[str] = mapped_column(
        VARCHAR(50), nullable=False, default=""
    )
    # `closed` tinyint(1) NOT NULL DEFAULT '0',
    closed: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # `sourcefileid` int(11) DEFAULT NULL,
    sourcefileid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `sourceid` int(11) DEFAULT NULL,
    sourceid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # PRIMARY KEY (`id`),
    # KEY `hash` (`hash`),
    # KEY `customerid` (`customerid`),
    # KEY `sourceid` (`sourceid`),
    # KEY `sourcefileid` (`sourcefileid`),
    # CONSTRAINT `cashimport_customerid_fkey` FOREIGN KEY (`customerid`) REFERENCES `customers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `cashimport_sourcefileid_fkey` FOREIGN KEY (`sourcefileid`) REFERENCES `sourcefiles` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `cashimport_sourceid_fkey` FOREIGN KEY (`sourceid`) REFERENCES `cashsources` (`id`) ON DELETE SET NULL ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"CashImport(id='{self.id}', "
            f"date='{self.date}', "
            f"value='{self.value}', "
            f"customer='{self.customer}', "
            f"description='{self.description}', "
            f"customerid='{self.customerid}', "
            f"hash='{self.hash}', "
            f"closed='{self.closed}', "
            f"sourcefileid='{self.sourcefileid}', "
            f"sourceid='{self.sourceid}' ) "
        )
