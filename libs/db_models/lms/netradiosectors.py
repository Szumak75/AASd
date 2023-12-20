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


class NetRadioSector(LmsBase):
    __tablename__ = "netradiosectors"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` varchar(64) COLLATE utf8_polish_ci NOT NULL,
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    # `azimuth` decimal(9,2) NOT NULL DEFAULT '0.00',
    azimuth: Mapped[float] = mapped_column(DECIMAL(9, 2), nullable=False, default=0.00)
    # `width` decimal(9,2) NOT NULL DEFAULT '0.00',
    width: Mapped[float] = mapped_column(DECIMAL(9, 2), nullable=False, default=0.00)
    # `altitude` smallint(6) NOT NULL DEFAULT '0',
    altitude: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=0)
    # `rsrange` int(11) NOT NULL DEFAULT '0',
    rsrange: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `license` varchar(64) COLLATE utf8_polish_ci DEFAULT NULL,
    license: Mapped[str] = mapped_column(VARCHAR(64), default=None)
    # `technology` int(11) NOT NULL DEFAULT '0',
    technology: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `frequency` decimal(9,5) DEFAULT NULL,
    frequency: Mapped[float] = mapped_column(DECIMAL(9, 5), default=None)
    # `frequency2` decimal(9,5) DEFAULT NULL,
    frequency2: Mapped[float] = mapped_column(DECIMAL(9, 5), default=None)
    # `bandwidth` decimal(9,5) DEFAULT NULL,
    bandwidth: Mapped[float] = mapped_column(DECIMAL(9, 5), default=None)
    # `netdev` int(11) NOT NULL,
    netdev: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `name` (`name`,`netdev`),
    # KEY `netdev` (`netdev`),
    # CONSTRAINT `netradiosectors_ibfk_1` FOREIGN KEY (`netdev`) REFERENCES `netdevices` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"NetRadioSector(id='{self.id}', "
            f"name='{self.name}', "
            f"azimuth='{self.azimuth}', "
            f"width='{self.width}', "
            f"altitude='{self.altitude}', "
            f"rsrange='{self.rsrange}', "
            f"license='{self.license}', "
            f"technology='{self.technology}', "
            f"frequency='{self.frequency}', "
            f"frequency2='{self.frequency2}', "
            f"bandwidth='{self.bandwidth}', "
            f"netdev='{self.netdev}' ) "
        )
