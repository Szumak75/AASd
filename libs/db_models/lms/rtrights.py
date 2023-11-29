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


class RtRight(LmsBase):
    __tablename__ = "rtrights"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `userid` int(11) NOT NULL,
    userid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `queueid` int(11) NOT NULL,
    queueid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `rights` int(11) NOT NULL DEFAULT '0',
    rights: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `userid` (`userid`,`queueid`),
    # KEY `queueid` (`queueid`),
    # CONSTRAINT `rtrights_ibfk_1` FOREIGN KEY (`queueid`) REFERENCES `rtqueues` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `rtrights_userid_fkey` FOREIGN KEY (`userid`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"RtRight(id='{self.id}', "
            f"userid='{self.userid}', "
            f"queueid='{self.queueid}', "
            f"rights='{self.rights}' ) "
        )
