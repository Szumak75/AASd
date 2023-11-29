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


class TariffAssignment(LmsBase):
    __tablename__ = "tariffassignments"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `tariffid` int(11) NOT NULL,
    tariffid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `tarifftagid` int(11) NOT NULL,
    tarifftagid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `tariffid_tarifftagid_idx` (`tariffid`,`tarifftagid`),
    # KEY `tarifftagid_idx` (`tarifftagid`),
    # CONSTRAINT `tariffassignments_tariffid_key` FOREIGN KEY (`tariffid`) REFERENCES `tariffs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `tariffassignments_tarifftagid_key` FOREIGN KEY (`tarifftagid`) REFERENCES `tarifftags` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"TariffAssignment(id='{self.id}', "
            f"tariffid='{self.tariffid}', "
            f"tarifftagid='{self.tarifftagid}' ) "
        )
