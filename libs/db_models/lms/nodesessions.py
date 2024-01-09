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
    BIGINT,
)

from libs.db_models.base import LmsBase


class NodeSession(LmsBase):
    __tablename__ = "nodesessions"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `customerid` int(11) DEFAULT NULL,
    customerid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `nodeid` int(11) DEFAULT NULL,
    nodeid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `ipaddr` int(16) unsigned NOT NULL DEFAULT '0',
    ipaddr: Mapped[int] = mapped_column(
        INTEGER(16, unsigned=True), nullable=False, default=0
    )
    # `mac` varchar(17) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    mac: Mapped[str] = mapped_column(VARCHAR(17), nullable=False, default="")
    # `start` int(11) NOT NULL DEFAULT '0',
    start: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `stop` int(11) NOT NULL DEFAULT '0',
    stop: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `download` bigint(20) DEFAULT '0',
    download: Mapped[int] = mapped_column(BIGINT(20), default=0)
    # `upload` bigint(20) DEFAULT '0',
    upload: Mapped[int] = mapped_column(BIGINT(20), default=0)
    # `tag` varchar(32) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    tag: Mapped[str] = mapped_column(VARCHAR(32), nullable=False, default="")
    # `terminatecause` varchar(32) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    terminatecause: Mapped[str] = mapped_column(VARCHAR(32), nullable=False, default="")
    # `type` smallint(6) NOT NULL DEFAULT '0',
    type: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=0)
    # PRIMARY KEY (`id`),
    # KEY `customerid` (`customerid`),
    # KEY `nodeid` (`nodeid`),
    # KEY `tag` (`tag`),
    # CONSTRAINT `nodesessions_customerid_fkey` FOREIGN KEY (`customerid`) REFERENCES `customers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `nodesessions_nodeid_fkey` FOREIGN KEY (`nodeid`) REFERENCES `nodes` (`id`) ON DELETE SET NULL ON UPDATE CASCADE

    def __repr__(self) -> str:
        return (
            f"NodeSession(id='{self.id}', "
            f"customerid='{self.customerid}', "
            f"nodeid='{self.nodeid}', "
            f"ipaddr='{self.ipaddr}', "
            f"mac='{self.mac}', "
            f"start='{self.start}', "
            f"stop='{self.stop}', "
            f"download='{self.download}', "
            f"upload='{self.upload}', "
            f"tag='{self.tag}', "
            f"terminatecause='{self.terminatecause}', "
            f"type='{self.type}' ) "
        )
