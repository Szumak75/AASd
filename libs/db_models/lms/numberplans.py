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


class NumberPlan(LmsBase):
    __tablename__ = "numberplans"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `template` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    template: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `period` smallint(6) NOT NULL DEFAULT '0',
    period: Mapped[int] = mapped_column(
        SMALLINT(6), nullable=False, default=0
    )
    # `doctype` int(11) NOT NULL DEFAULT '0',
    doctype: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `isdefault` tinyint(1) NOT NULL DEFAULT '0',
    isdefault: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # PRIMARY KEY (`id`)

    def __repr__(self):
        return (
            f"NumberPlan(id='{self.id}', "
            f"template='{self.template}', "
            f"period='{self.period}', "
            f"doctype='{self.doctype}', "
            f"isdefault='{self.isdefault}' ) "
        )
