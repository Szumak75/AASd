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


class User(LmsBase):
    __tablename__ = "users"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `login` varchar(32) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    login: Mapped[str] = mapped_column(
        VARCHAR(32), nullable=False, default=""
    )
    # `firstname` varchar(64) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    firstname: Mapped[str] = mapped_column(
        VARCHAR(64), nullable=False, default=""
    )
    # `lastname` varchar(64) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    lastname: Mapped[str] = mapped_column(
        VARCHAR(64), nullable=False, default=""
    )
    # `email` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    email: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `phone` varchar(32) COLLATE utf8_polish_ci DEFAULT NULL,
    phone: Mapped[str] = mapped_column(
        VARCHAR(32), nullable=False, default=""
    )
    # `position` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    position: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `rights` text COLLATE utf8_polish_ci NOT NULL,
    rights: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `hosts` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    hosts: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `passwd` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    passwd: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `ntype` smallint(6) DEFAULT NULL,
    ntype: Mapped[int] = mapped_column(SMALLINT(6), default=None)
    # `lastlogindate` int(11) NOT NULL DEFAULT '0',
    lastlogindate: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `lastloginip` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    lastloginip: Mapped[str] = mapped_column(
        VARCHAR(16), nullable=False, default=""
    )
    # `failedlogindate` int(11) NOT NULL DEFAULT '0',
    failedlogindate: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `failedloginip` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    failedloginip: Mapped[str] = mapped_column(
        VARCHAR(16), nullable=False, default=""
    )
    # `deleted` tinyint(1) NOT NULL DEFAULT '0',
    deleted: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # `passwdexpiration` int(11) NOT NULL DEFAULT '0',
    passwdexpiration: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `passwdlastchange` int(11) NOT NULL DEFAULT '0',
    passwdlastchange: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `access` tinyint(1) NOT NULL DEFAULT '1',
    access: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=1
    )
    # `accessfrom` int(11) NOT NULL DEFAULT '0',
    accessfrom: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `accessto` int(11) NOT NULL DEFAULT '0',
    accessto: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `settings` mediumtext COLLATE utf8_polish_ci NOT NULL,
    settings: Mapped[str] = mapped_column(MEDIUMTEXT(), nullable=False)
    # `persistentsettings` mediumtext COLLATE utf8_polish_ci NOT NULL,
    persistentsettings: Mapped[str] = mapped_column(
        MEDIUMTEXT(), nullable=False
    )
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `login` (`login`)

    def __repr__(self):
        return (
            f"User(id='{self.id}', "
            f"login='{self.login}', "
            f"firstname='{self.firstname}', "
            f"lastname='{self.lastname}', "
            f"email='{self.email}', "
            f"phone='{self.phone}', "
            f"position='{self.position}', "
            f"rights='{self.rights}', "
            f"hosts='{self.hosts}', "
            f"passwd='{self.passwd}', "
            f"ntype='{self.ntype}', "
            f"lastlogindate='{self.lastlogindate}', "
            f"lastloginip='{self.lastloginip}', "
            f"failedlogindate='{self.failedlogindate}', "
            f"failedloginip='{self.failedloginip}', "
            f"deleted='{self.deleted}', "
            f"passwdexpiration='{self.passwdexpiration}', "
            f"passwdlastchange='{self.passwdlastchange}', "
            f"access='{self.access}', "
            f"accessfrom='{self.accessfrom}', "
            f"accessto='{self.accessto}', "
            f"settings='{self.settings}', "
            f"persistentsettings='{self.persistentsettings}' ) "
        )
