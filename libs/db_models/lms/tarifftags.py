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


class TariffTag(LmsBase):
    __tablename__ = "tarifftags"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` varchar(255) COLLATE utf8_polish_ci NOT NULL,
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # `description` text COLLATE utf8_polish_ci,
    description: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `name` (`name`)

    def __repr__(self):
        return (
            f"TariffTag(id='{self.id}', "
            f"name='{self.name}', "
            f"description='{self.description}' ) "
        )
