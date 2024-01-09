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
from libs.db_models.lms.location_boroughs import LocationBorough


class LocationCity(LmsBase):
    __tablename__ = "location_cities"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `ident` varchar(8) COLLATE utf8_polish_ci NOT NULL,
    ident: Mapped[str] = mapped_column(VARCHAR(8), nullable=False)
    # `name` varchar(64) COLLATE utf8_polish_ci NOT NULL,
    name: Mapped[str] = mapped_column(VARCHAR(64), nullable=False)
    # `cityid` int(11) DEFAULT NULL,
    cityid: Mapped[int] = mapped_column(INTEGER(11), index=True, default=None)
    # `boroughid` int(11) DEFAULT NULL,
    boroughid: Mapped[int] = mapped_column(ForeignKey("location_boroughs.id"))
    # PRIMARY KEY (`id`),
    # KEY `cityid` (`cityid`),
    # KEY `boroughid` (`boroughid`,`name`),
    # CONSTRAINT `location_cities_ibfk_1` FOREIGN KEY (`boroughid`) REFERENCES `location_boroughs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
    borough: Mapped["LocationBorough"] = relationship("LocationBorough")

    def __repr__(self) -> str:
        return (
            f"LocationCity(id='{self.id}', "
            f"ident='{self.ident}', "
            f"name='{self.name}', "
            f"cityid='{self.cityid}', "
            f"boroughid='{self.boroughid}', "
            f"borough='{self.borough}' "
            ") "
        )
