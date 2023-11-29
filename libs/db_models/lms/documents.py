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


class Document(LmsBase):
    __tablename__ = "documents"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `type` tinyint(4) NOT NULL DEFAULT '0',
    type: Mapped[int] = mapped_column(TINYINT(4), nullable=False, default=0)
    # `number` int(11) NOT NULL DEFAULT '0',
    number: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `numberplanid` int(11) DEFAULT NULL,
    numberplanid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `extnumber` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    extnumber: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `cdate` int(11) NOT NULL DEFAULT '0',
    cdate: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `sdate` int(11) NOT NULL DEFAULT '0',
    sdate: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `customerid` int(11) DEFAULT NULL,
    customerid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `userid` int(11) DEFAULT NULL,
    userid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `divisionid` int(11) DEFAULT NULL,
    divisionid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `name` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    name: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `address` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    address: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `zip` varchar(10) COLLATE utf8_polish_ci DEFAULT NULL,
    zip: Mapped[str] = mapped_column(VARCHAR(10), default=None)
    # `city` varchar(32) COLLATE utf8_polish_ci DEFAULT NULL,
    city: Mapped[str] = mapped_column(VARCHAR(32), default=None)
    # `countryid` int(11) DEFAULT NULL,
    countryid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `ten` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    ten: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="")
    # `ssn` varchar(11) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    ssn: Mapped[str] = mapped_column(VARCHAR(11), nullable=False, default="")
    # `paytime` smallint(6) NOT NULL DEFAULT '0',
    paytime: Mapped[int] = mapped_column(
        SMALLINT(6), nullable=False, default=0
    )
    # `paytype` smallint(6) DEFAULT NULL,
    paytype: Mapped[int] = mapped_column(SMALLINT(6), default=None)
    # `closed` tinyint(1) NOT NULL DEFAULT '0',
    closed: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # `reference` int(11) DEFAULT NULL,
    reference: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `reason` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    reason: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `div_name` text COLLATE utf8_polish_ci NOT NULL,
    div_name: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `div_shortname` text COLLATE utf8_polish_ci NOT NULL,
    div_shortname: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `div_address` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    div_address: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `div_city` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    div_city: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `div_zip` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    div_zip: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `div_countryid` int(11) DEFAULT NULL,
    div_countryid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `div_ten` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    div_ten: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `div_regon` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    div_regon: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `div_account` varchar(48) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    div_account: Mapped[str] = mapped_column(
        VARCHAR(48), nullable=False, default=""
    )
    # `div_inv_header` text COLLATE utf8_polish_ci NOT NULL,
    div_inv_header: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `div_inv_footer` text COLLATE utf8_polish_ci NOT NULL,
    div_inv_footer: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `div_inv_author` text COLLATE utf8_polish_ci NOT NULL,
    div_inv_author: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `div_inv_cplace` text COLLATE utf8_polish_ci NOT NULL,
    div_inv_cplace: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `fullnumber` varchar(50) COLLATE utf8_polish_ci DEFAULT NULL,
    fullnumber: Mapped[str] = mapped_column(VARCHAR(50), default=None)
    # `cancelled` smallint(6) NOT NULL DEFAULT '0',
    cancelled: Mapped[int] = mapped_column(
        SMALLINT(6), nullable=False, default=0
    )
    # `published` tinyint(1) NOT NULL DEFAULT '0',
    published: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # `cuserid` int(11) DEFAULT NULL,
    cuserid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `recipient_address_id` int(11) DEFAULT NULL,
    recipient_address_id: Mapped[int] = mapped_column(
        INTEGER(11), default=None
    )
    # `post_address_id` int(11) DEFAULT NULL,
    post_address_id: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `template` varchar(255) COLLATE utf8_polish_ci DEFAULT NULL,
    template: Mapped[str] = mapped_column(VARCHAR(255), default=None)
    # `commitflags` tinyint(1) NOT NULL DEFAULT '0',
    commitflags: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # PRIMARY KEY (`id`),
    # KEY `cdate` (`cdate`),
    # KEY `numberplanid` (`numberplanid`),
    # KEY `customerid` (`customerid`),
    # KEY `closed` (`closed`),
    # KEY `reference` (`reference`),
    # KEY `documents_recipient_address_id_fkey` (`recipient_address_id`),
    # KEY `documents_post_address_id_fkey` (`post_address_id`),
    # KEY `documents_userid_fkey` (`userid`),
    # KEY `documents_cuserid_fkey` (`cuserid`),
    # KEY `documents_divisionid_fkey` (`divisionid`),
    # KEY `documents_countryid_fkey` (`countryid`),
    # KEY `documents_div_countryid_fkey` (`div_countryid`),
    # CONSTRAINT `documents_countryid_fkey` FOREIGN KEY (`countryid`) REFERENCES `countries` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `documents_cuserid_fkey` FOREIGN KEY (`cuserid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `documents_customerid_fkey` FOREIGN KEY (`customerid`) REFERENCES `customers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `documents_div_countryid_fkey` FOREIGN KEY (`div_countryid`) REFERENCES `countries` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `documents_divisionid_fkey` FOREIGN KEY (`divisionid`) REFERENCES `divisions` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `documents_numberplanid_fkey` FOREIGN KEY (`numberplanid`) REFERENCES `numberplans` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `documents_post_address_id_fkey` FOREIGN KEY (`post_address_id`) REFERENCES `addresses` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `documents_recipient_address_id_fkey` FOREIGN KEY (`recipient_address_id`) REFERENCES `addresses` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `documents_reference_fkey` FOREIGN KEY (`reference`) REFERENCES `documents` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `documents_userid_fkey` FOREIGN KEY (`userid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"Document(id='{self.id}', "
            f"type='{self.type}', "
            f"number='{self.number}', "
            f"numberplanid='{self.numberplanid}', "
            f"extnumber='{self.extnumber}', "
            f"cdate='{self.cdate}', "
            f"sdate='{self.sdate}', "
            f"customerid='{self.customerid}', "
            f"userid='{self.userid}', "
            f"divisionid='{self.divisionid}', "
            f"name='{self.name}', "
            f"address='{self.address}', "
            f"zip='{self.zip}', "
            f"city='{self.city}', "
            f"countryid='{self.countryid}', "
            f"ten='{self.ten}', "
            f"ssn='{self.ssn}', "
            f"paytime='{self.paytime}', "
            f"paytype='{self.paytype}', "
            f"closed='{self.closed}', "
            f"reference='{self.reference}', "
            f"reason='{self.reason}', "
            f"div_name='{self.div_name}', "
            f"div_shortname='{self.div_shortname}', "
            f"div_address='{self.div_address}', "
            f"div_city='{self.div_city}', "
            f"div_zip='{self.div_zip}', "
            f"div_countryid='{self.div_countryid}', "
            f"div_ten='{self.div_ten}', "
            f"div_regon='{self.div_regon}', "
            f"div_account='{self.div_account}', "
            f"div_inv_header='{self.div_inv_header}', "
            f"div_inv_footer='{self.div_inv_footer}', "
            f"div_inv_author='{self.div_inv_author}', "
            f"div_inv_cplace='{self.div_inv_cplace}', "
            f"fullnumber='{self.fullnumber}', "
            f"cancelled='{self.cancelled}', "
            f"published='{self.published}', "
            f"cuserid='{self.cuserid}', "
            f"recipient_address_id='{self.recipient_address_id}', "
            f"post_address_id='{self.post_address_id}', "
            f"template='{self.template}', "
            f"commitflags='{self.commitflags}' ) "
        )
