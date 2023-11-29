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


class LocationState(LmsBase):
    __tablename__ = "location_states"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `ident` varchar(8) COLLATE utf8_polish_ci NOT NULL,
    ident: Mapped[str] = mapped_column(VARCHAR(8), nullable=False)
    # `name` varchar(64) COLLATE utf8_polish_ci NOT NULL,
    name: Mapped[str] = mapped_column(
        VARCHAR(64), unique=True, nullable=False
    )
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `name` (`name`)

    def __repr__(self):
        return (
            f"LocationState(id='{self.id}', "
            f"ident='{self.ident}', "
            f"name='{self.name}' "
            ") "
        )
