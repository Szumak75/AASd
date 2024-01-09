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


class NumberPlanAssignment(LmsBase):
    __tablename__ = "numberplanassignments"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `planid` int(11) NOT NULL,
    planid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `divisionid` int(11) NOT NULL,
    divisionid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `planid` (`planid`,`divisionid`),
    # KEY `divisionid` (`divisionid`),
    # CONSTRAINT `numberplanassignments_divisionid_fkey` FOREIGN KEY (`divisionid`) REFERENCES `divisions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `numberplanassignments_planid_fkey` FOREIGN KEY (`planid`) REFERENCES `numberplans` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self) -> str:
        return (
            f"NumberPlanAssignment(id='{self.id}', "
            f"planid='{self.planid}', "
            f"divisionid='{self.divisionid}' ) "
        )
