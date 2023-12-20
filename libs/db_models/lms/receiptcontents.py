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


class ReceiptContent(LmsBase):
    __tablename__ = "receiptcontents"

    # `docid` int(11) NOT NULL,
    docid: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `itemid` tinyint(4) NOT NULL DEFAULT '0',
    itemid: Mapped[int] = mapped_column(
        TINYINT(4), primary_key=True, nullable=False, default=0
    )
    # `value` decimal(9,2) NOT NULL DEFAULT '0.00',
    value: Mapped[float] = mapped_column(DECIMAL(9, 2), nullable=False, default=0.00)
    # `description` text COLLATE utf8_polish_ci NOT NULL,
    description: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `regid` int(11) DEFAULT NULL,
    regid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # KEY `docid` (`docid`),
    # KEY `regid` (`regid`),
    # CONSTRAINT `receiptcontents_docid_fkey` FOREIGN KEY (`docid`) REFERENCES `documents` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `receiptcontents_regid_fkey` FOREIGN KEY (`regid`) REFERENCES `cashregs` (`id`) ON DELETE SET NULL ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"ReceiptContent(docid='{self.docid}', "
            f"itemid='{self.itemid}', "
            f"value='{self.value}', "
            f"description='{self.description}', "
            f"regid='{self.regid}' ) "
        )
