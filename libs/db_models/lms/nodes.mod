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


class Node(LmsBase):
    __tablename__ = "nodes"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` varchar(32) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    name: Mapped[str] = mapped_column(
        VARCHAR(32), nullable=False, default=""
    )
    # `ipaddr` int(16) unsigned NOT NULL DEFAULT '0',
    ipaddr: Mapped[int] = mapped_column(
        INTEGER(16), nullable=False, default=0
    )
    # `ipaddr_pub` int(16) unsigned NOT NULL DEFAULT '0',
    ipaddr_pub: Mapped[int] = mapped_column(
        INTEGER(16), nullable=False, default=0
    )
    # `passwd` varchar(32) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    passwd: Mapped[str] = mapped_column(
        VARCHAR(32), nullable=False, default=""
    )
    # `ownerid` int(11) DEFAULT NULL,
    # ownerid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `creationdate` int(11) NOT NULL DEFAULT '0',
    creationdate: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `moddate` int(11) NOT NULL DEFAULT '0',
    moddate: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `creatorid` int(11) DEFAULT NULL,
    creatorid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `modid` int(11) DEFAULT NULL,
    modid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `netdev` int(11) DEFAULT NULL,
    netdev: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `linktype` tinyint(1) NOT NULL DEFAULT '0',
    linktype: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # `linkradiosector` int(11) DEFAULT NULL,
    linkradiosector: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `linkspeed` int(11) NOT NULL DEFAULT '100000',
    linkspeed: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=100000
    )
    # `linktechnology` int(11) NOT NULL DEFAULT '0',
    linktechnology: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `port` smallint(6) NOT NULL DEFAULT '0',
    port: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=0)
    # `access` tinyint(1) NOT NULL DEFAULT '1',
    access: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=1
    )
    # `warning` tinyint(1) NOT NULL DEFAULT '0',
    warning: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # `authtype` tinyint(1) NOT NULL DEFAULT '0',
    authtype: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # `chkmac` tinyint(1) NOT NULL DEFAULT '1',
    chkmac: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=1
    )
    # `halfduplex` tinyint(1) NOT NULL DEFAULT '0',
    halfduplex: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # `lastonline` int(11) NOT NULL DEFAULT '0',
    lastonline: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `info` text COLLATE utf8_polish_ci NOT NULL,
    info: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `nas` tinyint(1) NOT NULL DEFAULT '0',
    nas: Mapped[int] = mapped_column(TINYINT(1), nullable=False, default=0)
    # `longitude` decimal(10,6) DEFAULT NULL,
    longitude: Mapped[float] = mapped_column(DECIMAL(10, 6), default=None)
    # `latitude` decimal(10,6) DEFAULT NULL,
    latitude: Mapped[float] = mapped_column(DECIMAL(10, 6), default=None)
    # `netid` int(11) NOT NULL DEFAULT '0',
    netid: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `invprojectid` int(11) DEFAULT NULL,
    invprojectid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `address_id` int(11) DEFAULT NULL,
    address_id: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `name` (`name`),
    # UNIQUE KEY `ipaddr` (`ipaddr`,`netid`),
    # KEY `netdev` (`netdev`),
    # KEY `ownerid` (`ownerid`),
    # KEY `ipaddr_pub` (`ipaddr_pub`),
    # KEY `linkradiosector` (`linkradiosector`),
    # KEY `authtype` (`authtype`),
    # KEY `nodes_address_id_fkey` (`address_id`),
    # KEY `netid` (`netid`),
    # KEY `invprojectid` (`invprojectid`),
    # KEY `nodes_creatorid_fkey` (`creatorid`),
    # KEY `nodes_modid_fkey` (`modid`),
    # CONSTRAINT `nodes_address_id_fkey` FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `nodes_creatorid_fkey` FOREIGN KEY (`creatorid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `nodes_ibfk_1` FOREIGN KEY (`netid`) REFERENCES `networks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `nodes_ibfk_2` FOREIGN KEY (`invprojectid`) REFERENCES `invprojects` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `nodes_ibfk_3` FOREIGN KEY (`linkradiosector`) REFERENCES `netradiosectors` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `nodes_modid_fkey` FOREIGN KEY (`modid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `nodes_netdev_fkey` FOREIGN KEY (`netdev`) REFERENCES `netdevices` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `nodes_ownerid_fkey` FOREIGN KEY (`ownerid`) REFERENCES `customers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
    ownerid: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    nodeassignment: Mapped[int] = relationship("NodeAssignment")

    def __repr__(self):
        return (
            f"Node(id='{self.id}', "
            f"name='{self.name}', "
            f"ipaddr='{self.ipaddr}', "
            # f"ipaddr_pub='{self.ipaddr_pub}', "
            # f"passwd='{self.passwd}', "
            # f"ownerid='{self.ownerid}', "
            f"creationdate='{self.creationdate}', "
            f"moddate='{self.moddate}', "
            # f"creatorid='{self.creatorid}', "
            # f"modid='{self.modid}', "
            # f"netdev='{self.netdev}', "
            # f"linktype='{self.linktype}', "
            # f"linkradiosector='{self.linkradiosector}', "
            # f"linkspeed='{self.linkspeed}', "
            # f"linktechnology='{self.linktechnology}', "
            # f"port='{self.port}', "
            f"access='{self.access}', "
            f"warning='{self.warning}', "
            # f"authtype='{self.authtype}', "
            # f"chkmac='{self.chkmac}', "
            # f"halfduplex='{self.halfduplex}', "
            f"lastonline='{self.lastonline}', "
            f"info='{self.info}', "
            # f"nas='{self.nas}', "
            # f"longitude='{self.longitude}', "
            # f"latitude='{self.latitude}', "
            # f"netid='{self.netid}', "
            # f"invprojectid='{self.invprojectid}', "
            # f"address_id='{self.address_id}', "
            f"nodeassignment='{self.nodeassignment}', "
            ") "
        )
