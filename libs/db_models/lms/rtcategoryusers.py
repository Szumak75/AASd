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


class RtCategoryUser(LmsBase):
    __tablename__ = "rtcategoryusers"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `userid` int(11) NOT NULL,
    userid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `categoryid` int(11) NOT NULL,
    categoryid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `userid` (`userid`,`categoryid`),
    # KEY `categoryid` (`categoryid`),
    # CONSTRAINT `rtcategoryusers_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `rtcategoryusers_ibfk_2` FOREIGN KEY (`categoryid`) REFERENCES `rtcategories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"RtCategoryUser(id='{self.id}', "
            f"userid='{self.userid}', "
            f"categoryid='{self.categoryid}' ) "
        )
