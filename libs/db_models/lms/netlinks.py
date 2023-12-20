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


class NetLink(LmsBase):
    __tablename__ = "netlinks"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `src` int(11) NOT NULL,
    src: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `dst` int(11) NOT NULL,
    dst: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `type` tinyint(1) NOT NULL DEFAULT '0',
    type: Mapped[int] = mapped_column(TINYINT(1), nullable=False, default=0)
    # `speed` int(11) NOT NULL DEFAULT '100000',
    speed: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=100000)
    # `technology` int(11) NOT NULL DEFAULT '0',
    technology: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `srcport` smallint(6) NOT NULL DEFAULT '0',
    srcport: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=0)
    # `dstport` smallint(6) NOT NULL DEFAULT '0',
    dstport: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=0)
    # `srcradiosector` int(11) DEFAULT NULL,
    srcradiosector: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `dstradiosector` int(11) DEFAULT NULL,
    dstradiosector: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `src` (`src`,`dst`),
    # KEY `srcradiosector` (`srcradiosector`),
    # KEY `dstradiosector` (`dstradiosector`),
    # KEY `netlinks_dst_fkey` (`dst`),
    # CONSTRAINT `netlinks_dst_fkey` FOREIGN KEY (`dst`) REFERENCES `netdevices` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `netlinks_ibfk_1` FOREIGN KEY (`srcradiosector`) REFERENCES `netradiosectors` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `netlinks_ibfk_2` FOREIGN KEY (`dstradiosector`) REFERENCES `netradiosectors` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `netlinks_src_fkey` FOREIGN KEY (`src`) REFERENCES `netdevices` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"NetLink(id='{self.id}', "
            f"src='{self.src}', "
            f"dst='{self.dst}', "
            f"type='{self.type}', "
            f"speed='{self.speed}', "
            f"technology='{self.technology}', "
            f"srcport='{self.srcport}', "
            f"dstport='{self.dstport}', "
            f"srcradiosector='{self.srcradiosector}', "
            f"dstradiosector='{self.dstradiosector}' ) "
        )
