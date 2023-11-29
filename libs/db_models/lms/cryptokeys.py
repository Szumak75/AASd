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


class CryptoKey(LmsBase):
    __tablename__ = "cryptokeys"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `domain_id` int(11) NOT NULL,
    domain_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `flags` int(11) NOT NULL,
    flags: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `active` tinyint(1) DEFAULT NULL,
    active: Mapped[int] = mapped_column(TINYINT(11), default=None)
    # `content` text COLLATE utf8_polish_ci,
    content: Mapped[str] = mapped_column(TEXT())
    # PRIMARY KEY (`id`),
    # KEY `domain_id` (`domain_id`),
    # CONSTRAINT `cryptokeys_domain_id_fkey` FOREIGN KEY (`domain_id`) REFERENCES `domains` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"CryptoKey(id='{self.id}', "
            f"domain_id='{self.domain_id}', "
            f"flags='{self.flags}', "
            f"active='{self.active}', "
            f"content='{self.content}' ) "
        )
