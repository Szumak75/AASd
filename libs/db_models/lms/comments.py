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


class Comment(LmsBase):
    __tablename__ = "comments"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `domain_id` int(11) NOT NULL,
    domain_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `name` varchar(255) COLLATE utf8_polish_ci NOT NULL,
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    # `type` varchar(10) COLLATE utf8_polish_ci NOT NULL,
    type: Mapped[str] = mapped_column(VARCHAR(10), nullable=False)
    # `modified_at` int(11) NOT NULL,
    modified_at: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `account` varchar(40) CHARACTER SET utf8 DEFAULT NULL,
    account: Mapped[str] = mapped_column(VARCHAR(40), default=None)
    # `comment` text COLLATE utf8_polish_ci NOT NULL,
    comment: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # PRIMARY KEY (`id`),
    # KEY `domain_id` (`domain_id`),
    # KEY `name` (`name`,`type`),
    # KEY `modified_at` (`domain_id`,`modified_at`),
    # CONSTRAINT `comments_domain_id_fkey` FOREIGN KEY (`domain_id`) REFERENCES `domains` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"Comment(id='{self.id}', "
            f"domain_id='{self.domain_id}', "
            f"name='{self.name}', "
            f"type='{self.type}', "
            f"modified_at='{self.modified_at}', "
            f"account='{self.account}', "
            f"comment='{self.comment}' ) "
        )
