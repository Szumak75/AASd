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
from libs.db_models.lms.location_street_types import LocationStreetType
from libs.db_models.lms.location_cities import LocationCity


class LocationStreet(LmsBase):
    __tablename__ = "location_streets"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` varchar(128) COLLATE utf8_polish_ci NOT NULL,
    name: Mapped[str] = mapped_column(VARCHAR(128), nullable=False)
    # `name2` varchar(128) COLLATE utf8_polish_ci DEFAULT NULL,
    name2: Mapped[str] = mapped_column(VARCHAR(128), default=None)
    # `ident` varchar(8) COLLATE utf8_polish_ci NOT NULL,
    ident: Mapped[str] = mapped_column(VARCHAR(8), nullable=False)
    # `typeid` int(11) DEFAULT NULL,
    typeid: Mapped[int] = mapped_column(
        ForeignKey("location_street_types.id")
    )
    # `cityid` int(11) NOT NULL,
    cityid: Mapped[int] = mapped_column(ForeignKey("location_cities.id"))
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `cityid` (`cityid`,`name`,`ident`),
    # KEY `typeid` (`typeid`),
    # CONSTRAINT `location_streets_ibfk_1` FOREIGN KEY (`typeid`) REFERENCES `location_street_types` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    street_type: Mapped["LocationStreetType"] = relationship(
        "LocationStreetType"
    )
    # CONSTRAINT `location_streets_ibfk_2` FOREIGN KEY (`cityid`) REFERENCES `location_cities` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
    city: Mapped["LocationCity"] = relationship("LocationCity")

    def __repr__(self):
        return (
            f"LocationStreet(id='{self.id}', "
            f"name='{self.name}', "
            f"name2='{self.name2}', "
            f"ident='{self.ident}', "
            f"typeid='{self.typeid}', "
            f"cityid='{self.cityid}', "
            f"street_type='{self.street_type}', "
            f"city='{self.city}' "
            ") "
        )
