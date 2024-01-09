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


class NodeLock(LmsBase):
    __tablename__ = "nodelocks"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `nodeid` int(11) NOT NULL,
    nodeid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `days` smallint(6) NOT NULL DEFAULT '0',
    days: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=0)
    # `fromsec` int(11) NOT NULL DEFAULT '0',
    fromsec: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `tosec` int(11) NOT NULL DEFAULT '0',
    tosec: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # PRIMARY KEY (`id`),
    # KEY `nodeid` (`nodeid`),
    # CONSTRAINT `nodelocks_ibfk_1` FOREIGN KEY (`nodeid`) REFERENCES `nodes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self) -> str:
        return (
            f"NodeLock(id='{self.id}', "
            f"nodeid='{self.nodeid}', "
            f"days='{self.days}', "
            f"fromsec='{self.fromsec}', "
            f"tosec='{self.tosec}' ) "
        )
