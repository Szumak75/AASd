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


class HistoryNode(LmsBase):
    __tablename__ = "history_nodes"

    # `id` int(11) NOT NULL,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `nodeid` int(11) NOT NULL,
    nodeid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `ipaddr` int(11) NOT NULL,
    ipaddr: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `ownerid` int(11) NOT NULL,
    ownerid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `changedate` int(11) NOT NULL,
    changedate: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `messages` text COLLATE utf8_polish_ci NOT NULL
    messages: Mapped[str] = mapped_column(TEXT(), nullable=False)

    def __repr__(self):
        return (
            f"HistoryNode(id='{self.id}', "
            f"nodeid='{self.nodeid}', "
            f"ipaddr='{self.ipaddr}', "
            f"ownerid='{self.ownerid}', "
            f"changedate='{self.changedate}', "
            f"messages='{self.messages}' ) "
        )
