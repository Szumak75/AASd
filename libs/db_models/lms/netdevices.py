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


class NetDevice(LmsBase):
    __tablename__ = "netdevices"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` varchar(32) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # `description` text COLLATE utf8_polish_ci NOT NULL,
    description: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `producer` varchar(64) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    producer: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, default="")
    # `model` varchar(32) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    model: Mapped[str] = mapped_column(VARCHAR(32), nullable=False, default="")
    # `serialnumber` varchar(32) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    serialnumber: Mapped[str] = mapped_column(VARCHAR(32), nullable=False, default="")
    # `ports` int(11) NOT NULL DEFAULT '0',
    ports: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `purchasetime` int(11) NOT NULL DEFAULT '0',
    purchasetime: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `guaranteeperiod` tinyint(3) unsigned DEFAULT '0',
    guaranteeperiod: Mapped[int] = mapped_column(TINYINT(3), nullable=False, default=0)
    # `shortname` varchar(32) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    shortname: Mapped[str] = mapped_column(VARCHAR(32), nullable=False, default="")
    # `nastype` int(11) NOT NULL DEFAULT '0',
    nastype: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `clients` int(11) NOT NULL DEFAULT '0',
    clients: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `secret` varchar(60) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    secret: Mapped[str] = mapped_column(VARCHAR(60), nullable=False, default="")
    # `community` varchar(50) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    community: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, default="")
    # `channelid` int(11) DEFAULT NULL,
    channelid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `longitude` decimal(10,6) DEFAULT NULL,
    longitude: Mapped[float] = mapped_column(DECIMAL(10, 6), default=None)
    # `latitude` decimal(10,6) DEFAULT NULL,
    latitude: Mapped[float] = mapped_column(DECIMAL(10, 6), default=None)
    # `netnodeid` int(11) DEFAULT NULL,
    netnodeid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `invprojectid` int(11) DEFAULT NULL,
    invprojectid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `status` tinyint(4) DEFAULT '0',
    status: Mapped[int] = mapped_column(TINYINT(4), default=0)
    # `netdevicemodelid` int(11) DEFAULT NULL,
    netdevicemodelid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `address_id` int(11) DEFAULT NULL,
    address_id: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `ownerid` int(11) DEFAULT NULL,
    ownerid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # PRIMARY KEY (`id`),
    # KEY `channelid` (`channelid`),
    # KEY `netdevices_address_id_fk` (`address_id`),
    # KEY `netnodeid` (`netnodeid`),
    # KEY `invprojectid` (`invprojectid`),
    # KEY `netdevicemodelid` (`netdevicemodelid`),
    # KEY `netdevices_ownerid_fkey` (`ownerid`),
    # CONSTRAINT `netdevices_address_id_fk` FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `netdevices_ibfk_1` FOREIGN KEY (`channelid`) REFERENCES `ewx_channels` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `netdevices_ibfk_2` FOREIGN KEY (`netnodeid`) REFERENCES `netnodes` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `netdevices_ibfk_3` FOREIGN KEY (`invprojectid`) REFERENCES `invprojects` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `netdevices_ibfk_4` FOREIGN KEY (`netdevicemodelid`) REFERENCES `netdevicemodels` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `netdevices_ownerid_fkey` FOREIGN KEY (`ownerid`) REFERENCES `customers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"NetDevice(id='{self.id}', "
            f"name='{self.name}', "
            f"description='{self.description}', "
            f"producer='{self.producer}', "
            f"model='{self.model}', "
            f"serialnumber='{self.serialnumber}', "
            f"ports='{self.ports}', "
            f"purchasetime='{self.purchasetime}', "
            f"guaranteeperiod='{self.guaranteeperiod}', "
            f"shortname='{self.shortname}', "
            f"nastype='{self.nastype}', "
            f"clients='{self.clients}', "
            f"secret='{self.secret}', "
            f"community='{self.community}', "
            f"channelid='{self.channelid}', "
            f"longitude='{self.longitude}', "
            f"netnodeid='{self.netnodeid}', "
            f"invprojectid='{self.invprojectid}', "
            f"status='{self.status}', "
            f"netdevicemodelid='{self.netdevicemodelid}', "
            f"address_id='{self.address_id}', "
            f"ownerid='{self.ownerid}' ) "
        )
