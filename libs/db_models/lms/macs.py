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


class Mac(LmsBase):
    __tablename__ = "macs"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `mac` varchar(17) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    mac: Mapped[str] = mapped_column(VARCHAR(17), nullable=False, default="")
    # `nodeid` int(11) NOT NULL,
    nodeid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `mac` (`mac`,`nodeid`),
    # KEY `nodeid` (`nodeid`),
    # CONSTRAINT `macs_ibfk_1` FOREIGN KEY (`nodeid`) REFERENCES `nodes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self) -> str:
        return (
            f"Mac(id='{self.id}', " f"mac='{self.mac}', " f"nodeid='{self.nodeid}' ) "
        )
