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
from libs.db_models.lms.location_districts import LocationDistrict


class LocationBorough(LmsBase):
    __tablename__ = "location_boroughs"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` varchar(64) COLLATE utf8_polish_ci NOT NULL,
    name: Mapped[str] = mapped_column(VARCHAR(64), nullable=False)
    # `ident` varchar(8) COLLATE utf8_polish_ci NOT NULL,
    ident: Mapped[str] = mapped_column(VARCHAR(8), nullable=False)
    # `districtid` int(11) NOT NULL,
    districtid: Mapped[int] = mapped_column(
        ForeignKey("location_districts.id")
    )
    # `type` smallint(6) NOT NULL,
    type: Mapped[int] = mapped_column(SMALLINT(6), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `districtid` (`districtid`,`name`,`type`),
    # CONSTRAINT `location_boroughs_ibfk_1` FOREIGN KEY (`districtid`) REFERENCES `location_districts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
    district: Mapped["LocationDistrict"] = relationship("LocationDistrict")

    def __repr__(self):
        return (
            f"LocationBorough(id='{self.id}', "
            f"name='{self.name}', "
            f"ident='{self.ident}', "
            f"districtid='{self.districtid}', "
            f"type='{self.type}', "
            f"district='{self.district}' "
            ") "
        )
