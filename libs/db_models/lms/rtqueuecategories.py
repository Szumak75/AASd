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


class RtQueueCategory(LmsBase):
    __tablename__ = "rtqueuecategories"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `queueid` int(11) NOT NULL,
    queueid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `categoryid` int(11) NOT NULL,
    categoryid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # PRIMARY KEY (`id`),
    # KEY `queueid` (`queueid`),
    # KEY `categoryid` (`categoryid`),
    # CONSTRAINT `rtqueuecategories_ibfk_1` FOREIGN KEY (`queueid`) REFERENCES `rtqueues` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `rtqueuecategories_ibfk_2` FOREIGN KEY (`categoryid`) REFERENCES `rtcategories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self) -> str:
        return (
            f"RtQueueCategory(id='{self.id}', "
            f"queueid='{self.queueid}', "
            f"categoryid='{self.categoryid}' ) "
        )
