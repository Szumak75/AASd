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


class NodeGroup(LmsBase):
    __tablename__ = "nodegroups"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    name: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `prio` int(11) NOT NULL DEFAULT '0',
    prio: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `description` text COLLATE utf8_polish_ci NOT NULL,
    description: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `name` (`name`)

    def __repr__(self):
        return (
            f"NodeGroup(id='{self.id}', "
            f"name='{self.name}', "
            f"prio='{self.prio}', "
            f"description='{self.description}' ) "
        )
