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


class InvoiceContent(LmsBase):
    __tablename__ = "invoicecontents"

    # dummy primary key
    # rowid: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    # `docid` int(11) NOT NULL,
    docid: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `itemid` smallint(6) NOT NULL DEFAULT '0',
    itemid: Mapped[int] = mapped_column(
        SMALLINT(6), primary_key=True, nullable=False, default=0
    )
    # `value` decimal(12,5) NOT NULL DEFAULT '0.00000',
    value: Mapped[float] = mapped_column(
        DECIMAL(12, 5), nullable=False, default=0.00000
    )
    # `pdiscount` decimal(4,2) NOT NULL DEFAULT '0.00',
    pdiscount: Mapped[float] = mapped_column(
        DECIMAL(4, 2), nullable=False, default=0.00
    )
    # `vdiscount` decimal(9,2) NOT NULL DEFAULT '0.00',
    vdiscount: Mapped[float] = mapped_column(
        DECIMAL(9, 2), nullable=False, default=0.00
    )
    # `taxid` int(11) NOT NULL,
    taxid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `prodid` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    prodid: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # `content` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    content: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="")
    # `count` decimal(9,2) NOT NULL DEFAULT '0.00',
    count: Mapped[float] = mapped_column(DECIMAL(9, 2), nullable=False, default=0.00)
    # `description` text COLLATE utf8_polish_ci NOT NULL,
    description: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `tariffid` int(11) DEFAULT NULL,
    tariffid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # KEY `docid` (`docid`),
    # KEY `invoicecontents_taxid_fkey` (`taxid`),
    # KEY `invoicecontents_tariffid_fkey` (`tariffid`),
    # CONSTRAINT `invoicecontents_docid_fkey` FOREIGN KEY (`docid`) REFERENCES `documents` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `invoicecontents_tariffid_fkey` FOREIGN KEY (`tariffid`) REFERENCES `tariffs` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `invoicecontents_taxid_fkey` FOREIGN KEY (`taxid`) REFERENCES `taxes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self) -> str:
        return (
            f"InvoiceContent(docid='{self.docid}', "
            f"itemid='{self.itemid}', "
            f"value='{self.value}', "
            f"pdiscount='{self.pdiscount}', "
            f"vdiscount='{self.vdiscount}', "
            f"taxid='{self.taxid}', "
            f"prodid='{self.prodid}', "
            f"content='{self.content}', "
            f"count='{self.count}', "
            f"description='{self.description}', "
            f"tariffid='{self.tariffid}' ) "
        )
