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


class Network(LmsBase):
    __tablename__ = "networks"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` varchar(128) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    name: Mapped[str] = mapped_column(VARCHAR(128), nullable=False, default="")
    # `address` int(16) unsigned NOT NULL DEFAULT '0',
    address: Mapped[int] = mapped_column(
        INTEGER(16, unsigned=True), nullable=False, default=0
    )
    # `mask` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    mask: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="")
    # `gateway` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    gateway: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="")
    # `interface` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    interface: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="")
    # `dns` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    dns: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="")
    # `dns2` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    dns2: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="")
    # `domain` varchar(64) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    domain: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, default="")
    # `wins` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    wins: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="")
    # `dhcpstart` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    dhcpstart: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="")
    # `dhcpend` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    dhcpend: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="")
    # `disabled` tinyint(1) NOT NULL DEFAULT '0',
    disabled: Mapped[int] = mapped_column(TINYINT(1), nullable=False, default=0)
    # `notes` text COLLATE utf8_polish_ci NOT NULL,
    notes: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `vlanid` smallint(6) DEFAULT NULL,
    vlanid: Mapped[int] = mapped_column(SMALLINT(6), default=None)
    # `hostid` int(11) DEFAULT NULL,
    hostid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `authtype` tinyint(1) NOT NULL DEFAULT '0',
    authtype: Mapped[int] = mapped_column(TINYINT(1), nullable=False, default=0)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `name` (`name`),
    # UNIQUE KEY `address` (`address`,`hostid`),
    # KEY `hostid` (`hostid`),
    # CONSTRAINT `networks_ibfk_1` FOREIGN KEY (`hostid`) REFERENCES `hosts` (`id`) ON DELETE SET NULL ON UPDATE CASCADE

    def __repr__(self) -> str:
        return (
            f"Network(id='{self.id}', "
            f"name='{self.name}', "
            f"address='{self.address}', "
            f"mask='{self.mask}', "
            f"gateway='{self.gateway}', "
            f"interface='{self.interface}', "
            f"dns='{self.dns}', "
            f"dns2='{self.dns2}', "
            f"domain='{self.domain}', "
            f"wins='{self.wins}', "
            f"dhcpstart='{self.dhcpstart}', "
            f"dhcpend='{self.dhcpend}', "
            f"disabled='{self.disabled}', "
            f"notes='{self.notes}', "
            f"vlanid='{self.vlanid}', "
            f"hostid='{self.hostid}', "
            f"authtype='{self.authtype}' ) "
        )
