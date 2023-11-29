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
from libs.db_models.lms.location_states import LocationState


class LocationDistrict(LmsBase):
    __tablename__ = "location_districts"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` varchar(64) COLLATE utf8_polish_ci NOT NULL,
    name: Mapped[str] = mapped_column(VARCHAR(64), nullable=False)
    # `ident` varchar(8) COLLATE utf8_polish_ci NOT NULL,
    ident: Mapped[str] = mapped_column(VARCHAR(8), nullable=False)
    # `stateid` int(11) NOT NULL,
    stateid: Mapped[int] = mapped_column(ForeignKey("location_states.id"))
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `stateid` (`stateid`,`name`),
    # CONSTRAINT `location_districts_ibfk_1` FOREIGN KEY (`stateid`) REFERENCES `location_states` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
    state: Mapped["LocationState"] = relationship("LocationState")

    def __repr__(self):
        return (
            f"LocationDistrict(id='{self.id}', "
            f"name='{self.name}', "
            f"ident='{self.ident}', "
            f"stateid='{self.stateid}', "
            f"state='{self.state}' "
            ") "
        )
