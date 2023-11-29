# -*- coding: UTF-8 -*-
"""
Created on 6 oct 2020

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


class Alias(LmsBase):
    __tablename__ = "aliases"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `login` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    login: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `domainid` int(11) NOT NULL,
    domainid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `login` (`login`,`domainid`),
    # KEY `aliases_domainid_fkey` (`domainid`),
    # CONSTRAINT `aliases_domainid_fkey` FOREIGN KEY (`domainid`) REFERENCES `domains` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"Alias(id='{self.id}', "
            f"login='{self.login}', "
            f"domainid='{self.domainid}' ) "
        )
