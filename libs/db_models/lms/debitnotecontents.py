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


class DebitNoteContent(LmsBase):
    __tablename__ = "debitnotecontents"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `docid` int(11) NOT NULL,
    docid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `itemid` smallint(6) NOT NULL DEFAULT '0',
    itemid: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=0)
    # `value` decimal(9,2) NOT NULL DEFAULT '0.00',
    value: Mapped[float] = mapped_column(DECIMAL(9, 2), nullable=False, default=0.00)
    # `description` text COLLATE utf8_polish_ci NOT NULL,
    description: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `docid` (`docid`,`itemid`),
    # CONSTRAINT `debitnotecontents_docid_fkey` FOREIGN KEY (`docid`) REFERENCES `documents` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"DebitNoteContent(id='{self.id}', "
            f"docid='{self.docid}', "
            f"itemid='{self.itemid}', "
            f"value='{self.value}', "
            f"description='{self.description}' ) "
        )
