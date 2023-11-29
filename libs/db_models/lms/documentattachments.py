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


class DocumentAttachment(LmsBase):
    __tablename__ = "documentattachments"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `docid` int(11) NOT NULL,
    docid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `filename` varchar(255) COLLATE utf8_polish_ci NOT NULL,
    filename: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    # `contenttype` varchar(255) COLLATE utf8_polish_ci NOT NULL,
    contenttype: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    # `md5sum` varchar(32) COLLATE utf8_polish_ci NOT NULL,
    md5sum: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    # `main` smallint(6) NOT NULL DEFAULT '1',
    main: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=1)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `docid` (`docid`,`md5sum`),
    # KEY `md5sum` (`md5sum`),
    # CONSTRAINT `documentattachments_ibfk_1` FOREIGN KEY (`docid`) REFERENCES `documents` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"DocumentAttachment(id='{self.id}', "
            f"docid='{self.docid}', "
            f"filename='{self.filename}', "
            f"contenttype='{self.contenttype}', "
            f"md5sum='{self.md5sum}', "
            f"main='{self.main}' ) "
        )
