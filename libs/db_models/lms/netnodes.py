# -*- coding: UTF-8 -*-
"""
Created on 7 oct 2020.

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
from libs.db_models.lms.addresses import Address
from libs.db_models.lms.divisions import Division


class NetNode(LmsBase):
    __tablename__ = "netnodes"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` varchar(255) COLLATE utf8_polish_ci NOT NULL,
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    # `type` tinyint(4) DEFAULT '0',
    type: Mapped[int] = mapped_column(TINYINT(4), default=0)
    # `invprojectid` int(11) DEFAULT NULL,
    invprojectid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `status` tinyint(4) DEFAULT '0',
    status: Mapped[int] = mapped_column(TINYINT(4), default=0)
    # `longitude` decimal(10,6) DEFAULT NULL,
    longitude: Mapped[float] = mapped_column(DECIMAL(10, 6), default=None)
    # `latitude` decimal(10,6) DEFAULT NULL,
    latitude: Mapped[float] = mapped_column(DECIMAL(10, 6), default=None)
    # `ownership` tinyint(1) DEFAULT '0',
    ownership: Mapped[int] = mapped_column(TINYINT(1), default=0)
    # `coowner` varchar(255) COLLATE utf8_polish_ci DEFAULT '',
    coowner: Mapped[str] = mapped_column(VARCHAR(255), default="")
    # `uip` tinyint(1) DEFAULT '0',
    uip: Mapped[int] = mapped_column(TINYINT(1), default=0)
    # `miar` tinyint(1) DEFAULT '0',
    miar: Mapped[int] = mapped_column(TINYINT(1), default=0)
    # `createtime` int(11) DEFAULT NULL,
    createtime: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `lastinspectiontime` int(11) DEFAULT NULL,
    lastinspectiontime: Mapped[int] = mapped_column(
        INTEGER(11), default=None
    )
    # `admcontact` text COLLATE utf8_polish_ci,
    admcontact: Mapped[str] = mapped_column(TEXT())
    # `divisionid` int(11) DEFAULT NULL,
    divisionid: Mapped[int] = mapped_column(ForeignKey("divisions.id"))
    # `address_id` int(11) DEFAULT NULL,
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    # `info` text COLLATE utf8_polish_ci,
    info: Mapped[str] = mapped_column(TEXT())
    # PRIMARY KEY (`id`),
    # KEY `netnodes_address_id_fkey` (`address_id`),
    # KEY `invprojectid` (`invprojectid`),
    # KEY `divisionid` (`divisionid`),
    # CONSTRAINT `netnodes_address_id_fkey` FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    address: Mapped["Address"] = relationship("Address")
    # CONSTRAINT `netnodes_ibfk_1` FOREIGN KEY (`invprojectid`) REFERENCES `invprojects` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `netnodes_ibfk_2` FOREIGN KEY (`divisionid`) REFERENCES `divisions` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
    division: Mapped["Division"] = relationship("Division")

    def __repr__(self):
        return (
            f"NetNode(id='{self.id}', "
            f"name='{self.name}', "
            f"type='{self.type}', "
            f"invprojectid='{self.invprojectid}', "
            f"status='{self.status}', "
            f"longitude='{self.longitude}', "
            f"latitude='{self.latitude}', "
            f"ownership='{self.ownership}', "
            f"coowner='{self.coowner}', "
            f"uip='{self.uip}', "
            f"miar='{self.miar}', "
            f"createtime='{self.createtime}', "
            f"lastinspectiontime='{self.lastinspectiontime}', "
            f"admcontact='{self.admcontact}', "
            f"divisionid='{self.divisionid}', "
            f"address_id='{self.address_id}', "
            f"info='{self.info}', "
            f"address='{self.address}', "
            f"division='{self.division}'"
            ")"
        )
