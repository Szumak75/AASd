# -*- coding: UTF-8 -*-
"""
Created on 6 oct 2020

@author: szumak@virthost.pl
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import (
    INTEGER,
    VARCHAR,
)

from libs.db_models.base import LmsBase


class CustomerContact(LmsBase):
    __tablename__ = "customercontacts"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `customerid` int(11) NOT NULL,
    # customerid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `name` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # `contact` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    contact: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # `type` int(11) DEFAULT NULL,
    type: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # PRIMARY KEY (`id`),
    # KEY `customerid` (`customerid`),
    # KEY `contact` (`contact`),
    # CONSTRAINT `customercontacts_customerid_fkey` FOREIGN KEY (`customerid`) REFERENCES `customers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self) -> str:
        return (
            f"CustomerContact(id='{self.id}', "
            # f"customerid='{self.customerid}', "
            f"name='{self.name}', "
            f"contact='{self.contact}', "
            f"type='{self.type}' ) "
        )
