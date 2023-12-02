# -*- coding: UTF-8 -*-
"""
Created on 7 oct 2020

@author: szumak@virthost.pl
"""

from typing import Optional

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


class NodeAssignment(LmsBase):
    __tablename__ = "nodeassignments"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `nodeid` int(11) NOT NULL,
    # nodeid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `assignmentid` int(11) NOT NULL,
    # assignmentid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `nodeid` (`nodeid`,`assignmentid`),
    # KEY `assignmentid` (`assignmentid`),
    # CONSTRAINT `nodeassignments_ibfk_1` FOREIGN KEY (`nodeid`) REFERENCES `nodes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `nodeassignments_ibfk_2` FOREIGN KEY (`assignmentid`) REFERENCES `assignments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
    nodeid: Mapped[int] = mapped_column(ForeignKey("nodes.id"))
    assignmentid: Mapped[int] = mapped_column(ForeignKey("assignments.id"))
    assignment: Mapped["Assignment"] = relationship(
        back_populates="nodeassignment"
    )

    def __repr__(self):
        return (
            f"NodeAssignment(id='{self.id}', "
            f"nodeid='{self.nodeid}', "
            f"assignmentid='{self.assignmentid}', "
            f"assignment='{self.assignment}', "
            ") "
        )