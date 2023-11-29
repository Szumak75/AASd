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
from libs.db_models.lms.addresses import Address


class Division(LmsBase):
    __tablename__ = "divisions"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `shortname` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    shortname: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `name` text COLLATE utf8_polish_ci NOT NULL,
    name: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `ten` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    ten: Mapped[str] = mapped_column(
        VARCHAR(128), nullable=False, default=""
    )
    # `regon` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    regon: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `rbe` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    rbe: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `rbename` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    rbename: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `telecomnumber` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    telecomnumber: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `account` varchar(48) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    account: Mapped[str] = mapped_column(
        VARCHAR(48), nullable=False, default=""
    )
    # `inv_header` text COLLATE utf8_polish_ci NOT NULL,
    inv_header: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `inv_footer` text COLLATE utf8_polish_ci NOT NULL,
    inv_footer: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `inv_author` text COLLATE utf8_polish_ci NOT NULL,
    inv_author: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `inv_paytime` smallint(6) DEFAULT NULL,
    inv_paytime: Mapped[int] = mapped_column(SMALLINT(6), default=None)
    # `inv_paytype` smallint(6) DEFAULT NULL,
    inv_paytype: Mapped[int] = mapped_column(SMALLINT(6), default=None)
    # `description` text COLLATE utf8_polish_ci NOT NULL,
    description: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `status` tinyint(1) NOT NULL DEFAULT '0',
    status: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # `tax_office_code` varchar(8) COLLATE utf8_polish_ci DEFAULT NULL,
    tax_office_code: Mapped[str] = mapped_column(VARCHAR(8), default=None)
    # `address_id` int(11) DEFAULT NULL,
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    # `inv_cplace` text COLLATE utf8_polish_ci NOT NULL,
    inv_cplace: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `shortname` (`shortname`),
    # KEY `divisions_address_id_fk` (`address_id`),
    # CONSTRAINT `divisions_address_id_fk` FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
    address: Mapped["Address"] = relationship("Address")

    def __repr__(self):
        return (
            f"Division(id='{self.id}', "
            f"shortname='{self.shortname}', "
            f"name='{self.name}', "
            f"ten='{self.ten}', "
            f"regon='{self.regon}', "
            f"rbe='{self.rbe}', "
            f"rbename='{self.rbename}', "
            f"telecomnumber='{self.telecomnumber}', "
            f"account='{self.account}', "
            f"inv_header='{self.inv_header}', "
            f"inv_footer='{self.inv_footer}', "
            f"inv_author='{self.inv_author}', "
            f"inv_paytime='{self.inv_paytime}', "
            f"inv_paytype='{self.inv_paytype}', "
            f"description='{self.description}', "
            f"status='{self.status}', "
            f"tax_office_code='{self.tax_office_code}', "
            f"address_id='{self.address_id}', "
            f"inv_cplace='{self.inv_cplace}', "
            f"address='{self.address}' "
            ") "
        )
