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


class Cash(LmsBase):
    __tablename__ = "cash"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `time` int(11) NOT NULL DEFAULT '0',
    time: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `type` smallint(6) NOT NULL DEFAULT '0',
    type: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=0)
    # `userid` int(11) DEFAULT NULL,
    userid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `value` decimal(9,2) NOT NULL DEFAULT '0.00',
    value: Mapped[float] = mapped_column(
        DECIMAL(9, 2), nullable=False, default=0.00
    )
    # `taxid` int(11) DEFAULT NULL,
    taxid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `customerid` int(11) DEFAULT NULL,
    customerid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `comment` text COLLATE utf8_polish_ci NOT NULL,
    comment: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `docid` int(11) DEFAULT NULL,
    docid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `itemid` smallint(6) NOT NULL DEFAULT '0',
    itemid: Mapped[int] = mapped_column(
        SMALLINT(6), nullable=False, default=0
    )
    # `importid` int(11) DEFAULT NULL,
    importid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `sourceid` int(11) DEFAULT NULL,
    sourceid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # PRIMARY KEY (`id`),
    # KEY `customerid` (`customerid`),
    # KEY `docid` (`docid`),
    # KEY `time` (`time`),
    # KEY `importid` (`importid`),
    # KEY `sourceid` (`sourceid`),
    # KEY `cash_userid_fkey` (`userid`),
    # KEY `cash_taxid_fkey` (`taxid`),
    # CONSTRAINT `cash_customerid_fkey` FOREIGN KEY (`customerid`) REFERENCES `customers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `cash_docid_fkey` FOREIGN KEY (`docid`) REFERENCES `documents` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `cash_importid_fkey` FOREIGN KEY (`importid`) REFERENCES `cashimport` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `cash_sourceid_fkey` FOREIGN KEY (`sourceid`) REFERENCES `cashsources` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `cash_taxid_fkey` FOREIGN KEY (`taxid`) REFERENCES `taxes` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `cash_userid_fkey` FOREIGN KEY (`userid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"Cash(id='{self.id}', "
            f"time='{self.time}', "
            f"type='{self.type}', "
            f"userid='{self.userid}', "
            f"value='{self.value}', "
            f"taxid='{self.taxid}', "
            f"customerid='{self.customerid}', "
            f"comment='{self.comment}', "
            f"docid='{self.docid}', "
            f"itemid='{self.itemid}', "
            f"importid='{self.importid}', "
            f"sourceid='{self.sourceid}' ) "
        )
