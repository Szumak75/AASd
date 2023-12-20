# -*- coding: UTF-8 -*-
"""
Created on 9 oct 2020

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


class Tax(LmsBase):
    __tablename__ = "taxes"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `value` decimal(4,2) NOT NULL DEFAULT '0.00',
    value: Mapped[float] = mapped_column(DECIMAL(9, 2), nullable=False, default=0.00)
    # `taxed` tinyint(4) NOT NULL DEFAULT '0',
    taxed: Mapped[int] = mapped_column(TINYINT(4), nullable=False, default=0)
    # `label` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    label: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="")
    # `validfrom` int(11) NOT NULL DEFAULT '0',
    validfrom: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `validto` int(11) NOT NULL DEFAULT '0',
    validto: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `reversecharge` tinyint(1) NOT NULL DEFAULT '0',
    reversecharge: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # PRIMARY KEY (`id`)

    def __repr__(self):
        return (
            f"Tax(id='{self.id}', "
            f"value='{self.value}', "
            f"taxed='{self.taxed}', "
            f"label='{self.label}', "
            f"validfrom='{self.validfrom}', "
            f"validto='{self.validto}', "
            f"reversecharge='{self.reversecharge}' ) "
        )
