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


class NodeGroupAssignment(LmsBase):
    __tablename__ = "nodegroupassignments"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `nodegroupid` int(11) NOT NULL,
    nodegroupid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `nodeid` int(11) NOT NULL,
    nodeid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `nodeid` (`nodeid`,`nodegroupid`),
    # KEY `nodegroupassignments_nodegroupid_fkey` (`nodegroupid`),
    # CONSTRAINT `nodegroupassignments_nodegroupid_fkey` FOREIGN KEY (`nodegroupid`) REFERENCES `nodegroups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `nodegroupassignments_nodeid_fkey` FOREIGN KEY (`nodeid`) REFERENCES `nodes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"NodeGroupAssignment(id='{self.id}', "
            f"nodegroupid='{self.nodegroupid}', "
            f"nodeid='{self.nodeid}' ) "
        )
