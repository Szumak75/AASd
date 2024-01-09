# -*- coding: UTF-8 -*-
"""
Created on 16 oct 2020

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


class LocationStreetType(LmsBase):
    __tablename__ = "location_street_types"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` varchar(8) COLLATE utf8_polish_ci NOT NULL,
    name: Mapped[str] = mapped_column(VARCHAR(8), nullable=False)
    # PRIMARY KEY (`id`)

    def __repr__(self) -> str:
        return f"LocationStreetType(id='{self.id}', " f"name='{self.name}' ) "
