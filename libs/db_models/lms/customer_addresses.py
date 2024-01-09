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


class CustomerAddress(LmsBase):
    __tablename__ = "customer_addresses"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `customer_id` int(11) DEFAULT NULL,
    customer_id: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `address_id` int(11) DEFAULT NULL,
    address_id: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `type` smallint(6) DEFAULT NULL,
    type: Mapped[int] = mapped_column(SMALLINT(6), default=None)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `customer_id` (`customer_id`,`address_id`),
    # KEY `customer_addresses_address_id_fk` (`address_id`),
    # CONSTRAINT `customer_addresses_address_id_fk` FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `customer_addresses_customer_id_fkey` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self) -> str:
        return (
            f"CustomerAddress(id='{self.id}', "
            f"customer_id='{self.customer_id}', "
            f"address_id='{self.address_id}', "
            f"type='{self.type}' ) "
        )
