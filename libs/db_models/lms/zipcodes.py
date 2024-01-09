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


class ZipCode(LmsBase):
    __tablename__ = "zipcodes"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `zip` varchar(10) NOT NULL DEFAULT '',
    zip: Mapped[str] = mapped_column(VARCHAR(10), nullable=False, default="")
    # `stateid` int(11) DEFAULT NULL,
    stateid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `zip` (`zip`),
    # KEY `stateid` (`stateid`),
    # CONSTRAINT `zipcodes_stateid_fkey` FOREIGN KEY (`stateid`) REFERENCES `states` (`id`) ON DELETE SET NULL ON UPDATE CASCADE

    def __repr__(self) -> str:
        return (
            f"ZipCode(id='{self.id}', "
            f"zip='{self.zip}', "
            f"stateid='{self.stateid}' ) "
        )
