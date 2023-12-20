# -*- coding: UTF-8 -*-
"""
Created on 6 oct 2020

@author: szumak@virthost.pl
"""


from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import (
    DECIMAL,
    INTEGER,
    SMALLINT,
    TINYINT,
    VARCHAR,
)

from libs.db_models.base import LmsBase


class Assignment(LmsBase):
    __tablename__ = "assignments"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `tariffid` int(11) DEFAULT NULL,
    # tariffid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `liabilityid` int(11) DEFAULT NULL,
    liabilityid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `customerid` int(11) NOT NULL,
    # customerid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `period` smallint(6) NOT NULL DEFAULT '0',
    period: Mapped[int] = mapped_column(SMALLINT(6), nullable=False, default=0)
    # `at` int(11) NOT NULL DEFAULT '0',
    at: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `datefrom` int(11) NOT NULL DEFAULT '0',
    datefrom: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `dateto` int(11) NOT NULL DEFAULT '0',
    dateto: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `invoice` tinyint(1) NOT NULL DEFAULT '0',
    invoice: Mapped[int] = mapped_column(TINYINT(1), nullable=False, default=0)
    # `suspended` tinyint(1) NOT NULL DEFAULT '0',
    suspended: Mapped[int] = mapped_column(TINYINT(1), nullable=False, default=0)
    # `settlement` tinyint(1) NOT NULL DEFAULT '0',
    settlement: Mapped[int] = mapped_column(TINYINT(1), nullable=False, default=0)
    # `pdiscount` decimal(4,2) NOT NULL DEFAULT '0.00',
    pdiscount: Mapped[float] = mapped_column(
        DECIMAL(4, 2), nullable=False, default=0.00
    )
    # `vdiscount` decimal(9,2) NOT NULL DEFAULT '0.00',
    vdiscount: Mapped[float] = mapped_column(
        DECIMAL(9, 2), nullable=False, default=0.00
    )
    # `paytype` smallint(6) DEFAULT NULL,
    paytype: Mapped[int] = mapped_column(SMALLINT(6), default=None)
    # `numberplanid` int(11) DEFAULT NULL,
    numberplanid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `attribute` varchar(255) COLLATE utf8_polish_ci DEFAULT NULL,
    attribute: Mapped[str] = mapped_column(VARCHAR(255), default=None)
    # `recipient_address_id` int(11) DEFAULT NULL,
    recipient_address_id: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `docid` int(11) DEFAULT NULL,
    docid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `commited` tinyint(1) NOT NULL DEFAULT '1',
    commited: Mapped[int] = mapped_column(TINYINT(1), nullable=False, default=1)
    # `separatedocument` tinyint(1) NOT NULL DEFAULT '0',
    separatedocument: Mapped[int] = mapped_column(TINYINT(1), nullable=False, default=0)
    # PRIMARY KEY (`id`),
    # KEY `tariffid` (`tariffid`),
    # KEY `customerid` (`customerid`),
    # KEY `numberplanid` (`numberplanid`),
    # KEY `assignments_recipient_address_id_fkey` (`recipient_address_id`),
    # KEY `assignments_docid_fkey` (`docid`),
    # KEY `assignments_liabilityid_fkey` (`liabilityid`),
    # CONSTRAINT `assignments_customerid_fkey` FOREIGN KEY (`customerid`) REFERENCES `customers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `assignments_docid_fkey` FOREIGN KEY (`docid`) REFERENCES `documents` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `assignments_liabilityid_fkey` FOREIGN KEY (`liabilityid`) REFERENCES `liabilities` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `assignments_numberplanid` FOREIGN KEY (`numberplanid`) REFERENCES `numberplans` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `assignments_recipient_address_id_fkey` FOREIGN KEY (`recipient_address_id`) REFERENCES `addresses` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `assignments_tariffid_fkey` FOREIGN KEY (`tariffid`) REFERENCES `tariffs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"Assignment(id='{self.id}', "
            f"tariffid='{self.tariffid}', "
            f"liabilityid='{self.liabilityid}', "
            f"customerid='{self.customerid}', "
            f"period='{self.period}', "
            f"at='{self.at}', "
            f"datefrom='{self.datefrom}', "
            f"dateto='{self.dateto}', "
            f"invoice='{self.invoice}', "
            f"suspended='{self.suspended}', "
            f"settlement='{self.settlement}', "
            f"pdiscount='{self.pdiscount}', "
            f"vdiscount='{self.vdiscount}', "
            f"paytype='{self.paytype}', "
            f"numberplanid='{self.numberplanid}', "
            f"attribute='{self.attribute}', "
            f"recipient_address_id='{self.recipient_address_id}', "
            f"docid='{self.docid}', "
            f"commited='{self.commited}', "
            f"separatedocument='{self.separatedocument}' ) "
        )
