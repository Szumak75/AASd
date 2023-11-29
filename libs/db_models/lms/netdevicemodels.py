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


class NetDeviceModel(LmsBase):
    __tablename__ = "netdevicemodels"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `netdeviceproducerid` int(11) NOT NULL,
    netdeviceproducerid: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False
    )
    # `name` varchar(255) COLLATE utf8_polish_ci NOT NULL,
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    # `alternative_name` varchar(255) COLLATE utf8_polish_ci DEFAULT NULL,
    alternative_name: Mapped[str] = mapped_column(VARCHAR(255), default=None)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `name` (`name`,`netdeviceproducerid`),
    # KEY `netdeviceproducerid` (`netdeviceproducerid`),
    # CONSTRAINT `netdevicemodels_ibfk_1` FOREIGN KEY (`netdeviceproducerid`) REFERENCES `netdeviceproducers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"NetDeviceModel(id='{self.id}', "
            f"netdeviceproducerid='{self.netdeviceproducerid}', "
            f"name='{self.name}', "
            f"alternative_name='{self.alternative_name}' ) "
        )
