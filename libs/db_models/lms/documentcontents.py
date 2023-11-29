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


class DocumentContent(LmsBase):
    __tablename__ = "documentcontents"

    # dummy primary key
    rowid: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    # `docid` int(11) NOT NULL,
    docid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `title` text COLLATE utf8_polish_ci NOT NULL,
    title: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `fromdate` int(11) NOT NULL DEFAULT '0',
    fromdate: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `todate` int(11) NOT NULL DEFAULT '0',
    todate: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `description` text COLLATE utf8_polish_ci NOT NULL,
    description: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # UNIQUE KEY `docid` (`docid`),
    # KEY `fromdate` (`fromdate`),
    # KEY `todate` (`todate`),
    # CONSTRAINT `documentcontents_ibfk_1` FOREIGN KEY (`docid`) REFERENCES `documents` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"DocumentContent(docid='{self.docid}', "
            f"title='{self.title}', "
            f"fromdate='{self.fromdate}', "
            f"todate='{self.todate}', "
            f"description='{self.description}' ) "
        )
