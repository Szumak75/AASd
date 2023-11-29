# -*- coding: UTF-8 -*-
"""
Created on 6 oct 2020

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


class CustomerAssignment(LmsBase):
    __tablename__ = "customerassignments"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `customergroupid` int(11) NOT NULL,
    customergroupid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `customerid` int(11) NOT NULL,
    customerid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `customerassignment` (`customergroupid`,`customerid`),
    # KEY `customerid` (`customerid`),
    # CONSTRAINT `customerassignments_customergroupid_fkey` FOREIGN KEY (`customergroupid`) REFERENCES `customergroups` (`id`) ON DELETE CASCADE ON UPDATE CASCAD
    # CONSTRAINT `customerassignments_customerid_fkey` FOREIGN KEY (`customerid`) REFERENCES `customers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"CustomerAssignment(id='{self.id}', "
            f"customergroupid='{self.customergroupid}', "
            f"customerid='{self.customerid}' ) "
        )
