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


class DocNote(LmsBase):
    __tablename__ = "docnote"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `docid` int(11) NOT NULL,
    docid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `description` text COLLATE utf8_polish_ci NOT NULL,
    description: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # UNIQUE KEY `docnote_id` (`id`),
    # KEY `docnote_docid` (`docid`)

    def __repr__(self):
        return (
            f"DocNote(id='{self.id}', "
            f"docid='{self.docid}', "
            f"description='{self.description}' ) "
        )
