# -*- coding: UTF-8 -*-
"""
Created on 9 oct 2020

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


class UserAssignment(LmsBase):
    __tablename__ = "userassignments"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `usergroupid` int(11) NOT NULL,
    usergroupid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `userid` int(11) NOT NULL,
    userid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `userassignments_usergroupid_key` (`usergroupid`,`userid`),
    # KEY `userassignments_userid_idx` (`userid`),
    # CONSTRAINT `userassignments_ibfk_1` FOREIGN KEY (`usergroupid`) REFERENCES `usergroups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `userassignments_ibfk_2` FOREIGN KEY (`userid`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"UserAssignment(id='{self.id}', "
            f"usergroupid='{self.usergroupid}', "
            f"userid='{self.userid}' ) "
        )
