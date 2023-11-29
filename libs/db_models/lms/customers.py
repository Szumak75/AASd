# -*- coding: UTF-8 -*-
"""
Created on 6 oct 2020

@author: szumak@virthost.pl
"""

from typing import List
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
from sqlalchemy.ext.hybrid import hybrid_property

from libs.db_models.base import LmsBase
from libs.db_models.lms.customercontacts import CustomerContact
from libs.db_models.lms.cash import Cash


class Customer(LmsBase):
    __tablename__ = "customers"

    # time of debt creation
    __debt_time: int = 0

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `extid` varchar(32) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    extid: Mapped[str] = mapped_column(
        VARCHAR(32), nullable=False, default=""
    )
    # `lastname` varchar(128) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    lastname: Mapped[str] = mapped_column(
        VARCHAR(128), nullable=False, default=""
    )
    # `name` varchar(128) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    name: Mapped[str] = mapped_column(
        VARCHAR(128), nullable=False, default=""
    )
    # `status` smallint(6) NOT NULL DEFAULT '0',
    status: Mapped[int] = mapped_column(
        SMALLINT(6), nullable=False, default=0
    )
    # `type` smallint(6) NOT NULL DEFAULT '0',
    type: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=0)
    # `ten` varchar(16) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    ten: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, default="")
    # `ssn` varchar(11) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    ssn: Mapped[str] = mapped_column(VARCHAR(11), nullable=False, default="")
    # `regon` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    regon: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `rbe` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    rbe: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `icn` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    icn: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `rbename` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    rbename: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `info` text COLLATE utf8_polish_ci NOT NULL,
    info: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `creationdate` int(11) NOT NULL DEFAULT '0',
    creationdate: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `moddate` int(11) NOT NULL DEFAULT '0',
    moddate: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `notes` text COLLATE utf8_polish_ci NOT NULL,
    notes: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `creatorid` int(11) DEFAULT NULL,
    creatorid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `modid` int(11) DEFAULT NULL,
    modid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `deleted` tinyint(1) NOT NULL DEFAULT '0',
    deleted: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # `message` text COLLATE utf8_polish_ci NOT NULL,
    message: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `cutoffstop` int(11) NOT NULL DEFAULT '0',
    # timestamp dnia zawieszenia blokad
    cutoffstop: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `consentdate` int(11) NOT NULL DEFAULT '0',
    consentdate: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `pin` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '0',
    pin: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default="0"
    )
    # `invoicenotice` tinyint(1) DEFAULT NULL,
    invoicenotice: Mapped[int] = mapped_column(TINYINT(1), default=None)
    # `einvoice` tinyint(1) DEFAULT NULL,
    einvoice: Mapped[int] = mapped_column(TINYINT(1), default=None)
    # `divisionid` int(11) DEFAULT NULL,
    divisionid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `mailingnotice` tinyint(1) DEFAULT NULL,
    mailingnotice: Mapped[int] = mapped_column(TINYINT(1), default=None)
    # `paytype` smallint(6) DEFAULT NULL,
    paytype: Mapped[int] = mapped_column(SMALLINT(6), default=None)
    # `paytime` smallint(6) NOT NULL DEFAULT '-1',
    paytime: Mapped[int] = mapped_column(
        SMALLINT(6), nullable=False, default=-1
    )
    # PRIMARY KEY (`id`),
    # KEY `name` (`lastname`,`name`),
    # KEY `customers_creatorid_fkey` (`creatorid`),
    # KEY `customers_modid_fkey` (`modid`),
    # KEY `customers_divisionid_fkey` (`divisionid`),
    # CONSTRAINT `customers_creatorid_fkey` FOREIGN KEY (`creatorid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `customers_divisionid_fkey` FOREIGN KEY (`divisionid`) REFERENCES `divisions` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `customers_modid_fkey` FOREIGN KEY (`modid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
    contacts: Mapped[List["CustomerContact"]] = relationship(
        "CustomerContact"
    )
    cash_operations: Mapped[List["Cash"]] = relationship("Cash")

    @hybrid_property
    def balance(self) -> int:
        """Returns balance of cash operations."""
        balance = 0
        for item in self.cash_operations:
            cash: Cash = item
            if cash.value < 0 and balance >= 0:
                self.__debt_time = cash.time
            balance += cash.value
        return balance

    @property
    def dept_timestamp(self) -> int:
        """Returns time of debt creation."""
        return self.__debt_time

    def __repr__(self):
        return (
            f"Customer(id='{self.id}', "
            f"extid='{self.extid}', "
            f"lastname='{self.lastname}', "
            f"name='{self.name}', "
            f"status='{self.status}', "
            f"type='{self.type}', "
            f"ten='{self.ten}', "
            f"ssn='{self.ssn}', "
            f"regon='{self.regon}', "
            f"rbe='{self.rbe}', "
            f"icn='{self.icn}', "
            f"rbename='{self.rbename}', "
            # f"info='{self.info}', "
            f"creationdate='{self.creationdate}', "
            f"moddate='{self.moddate}', "
            # f"notes='{self.notes}', "
            # f"creatorid='{self.creatorid}', "
            f"modid='{self.modid}', "
            f"deleted='{self.deleted}', "
            # f"message='{self.message}', "
            f"cutoffstop='{self.cutoffstop}', "
            f"consentdate='{self.consentdate}', "
            f"pin='{self.pin}', "
            f"invoicenotice='{self.invoicenotice}', "
            f"einvoice='{self.einvoice}', "
            f"divisionid='{self.divisionid}', "
            f"mailingnotice='{self.mailingnotice}', "
            f"paytype='{self.paytype}', "
            f"paytime='{self.paytime}', "
            f"contacts='{self.contacts}', "
            # f"cash_operations='{self.cash_operations}', "
            f" ) "
        )
