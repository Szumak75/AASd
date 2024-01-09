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


class Liability(LmsBase):
    __tablename__ = "liabilities"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `value` decimal(9,2) NOT NULL DEFAULT '0.00',
    value: Mapped[float] = mapped_column(DECIMAL(9, 2), nullable=False, default=0.00)
    # `name` text NOT NULL,
    name: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `taxid` int(11) NOT NULL
    taxid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `prodid` varchar(255) NOT NULL DEFAULT '',
    prodid: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # PRIMARY KEY (`id`)
    # KEY `liabilities_taxid_fkey` (`taxid`),
    # CONSTRAINT `liabilities_taxid_fkey` FOREIGN KEY (`taxid`) REFERENCES `taxes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self) -> str:
        return (
            f"Liability(id='{self.id}', "
            f"value='{self.value}', "
            f"name='{self.name}', "
            f"taxid='{self.taxid}', "
            f"prodid='{self.prodid}' ) "
        )
