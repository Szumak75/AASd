# -*- coding: UTF-8 -*-
"""
Created on 7 oct 2020

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


class RtTicket(LmsBase):
    __tablename__ = "rttickets"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `queueid` int(11) NOT NULL,
    queueid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `requestor` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    requestor: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `requestor_mail` varchar(255) COLLATE utf8_polish_ci DEFAULT NULL,
    requestor_mail: Mapped[str] = mapped_column(VARCHAR(255), default=None)
    # `requestor_phone` varchar(32) COLLATE utf8_polish_ci DEFAULT NULL,
    requestor_phone: Mapped[str] = mapped_column(VARCHAR(32), default=None)
    # `requestor_userid` int(11) DEFAULT NULL,
    requestor_userid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `subject` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    subject: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, default=""
    )
    # `state` tinyint(4) NOT NULL DEFAULT '0',
    state: Mapped[int] = mapped_column(TINYINT(4), nullable=False, default=0)
    # `cause` tinyint(4) NOT NULL DEFAULT '0',
    cause: Mapped[int] = mapped_column(TINYINT(4), nullable=False, default=0)
    # `owner` int(11) DEFAULT NULL,
    owner: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `customerid` int(11) DEFAULT NULL,
    customerid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `creatorid` int(11) DEFAULT NULL,
    creatorid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `createtime` int(11) NOT NULL DEFAULT '0',
    createtime: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `resolvetime` int(11) NOT NULL DEFAULT '0',
    resolvetime: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `source` tinyint(4) NOT NULL DEFAULT '0',
    source: Mapped[int] = mapped_column(
        TINYINT(4), nullable=False, default=0
    )
    # `priority` tinyint(4) NOT NULL DEFAULT '0',
    priority: Mapped[int] = mapped_column(
        TINYINT(4), nullable=False, default=0
    )
    # `deleted` tinyint(1) NOT NULL DEFAULT '0',
    deleted: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, default=0
    )
    # `deltime` int(11) NOT NULL DEFAULT '0',
    deltime: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, default=0
    )
    # `deluserid` int(11) DEFAULT NULL,
    deluserid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `address_id` int(11) DEFAULT NULL,
    address_id: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `nodeid` int(11) DEFAULT NULL,
    nodeid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `netnodeid` int(11) DEFAULT NULL,
    netnodeid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # PRIMARY KEY (`id`),
    # KEY `queueid` (`queueid`),
    # KEY `customerid` (`customerid`),
    # KEY `creatorid` (`creatorid`),
    # KEY `createtime` (`createtime`),
    # KEY `rttickets_address_id_fkey` (`address_id`),
    # KEY `rttickets_nodeid_fkey` (`nodeid`),
    # KEY `rttickets_deluserid_fkey` (`deluserid`),
    # KEY `rttickets_owner_fkey` (`owner`),
    # KEY `rttickets_requestor_userid_fkey` (`requestor_userid`),
    # CONSTRAINT `rttickets_address_id_fkey` FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `rttickets_creatorid_fkey` FOREIGN KEY (`creatorid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `rttickets_customerid_fkey` FOREIGN KEY (`customerid`) REFERENCES `customers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `rttickets_deluserid_fkey` FOREIGN KEY (`deluserid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `rttickets_nodeid_fkey` FOREIGN KEY (`nodeid`) REFERENCES `nodes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `rttickets_owner_fkey` FOREIGN KEY (`owner`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `rttickets_queueid_fkey` FOREIGN KEY (`queueid`) REFERENCES `rtqueues` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `rttickets_requestor_userid_fkey` FOREIGN KEY (`requestor_userid`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE

    def __repr__(self):
        return (
            f"RtTicket(id='{self.id}', "
            f"queueid='{self.queueid}', "
            f"requestor='{self.requestor}', "
            f"requestor_mail='{self.requestor_mail}', "
            f"requestor_phone='{self.requestor_phone}', "
            f"requestor_userid='{self.requestor_userid}', "
            f"subject='{self.subject}', "
            f"state='{self.state}', "
            f"cause='{self.cause}', "
            f"owner='{self.owner}', "
            f"customerid='{self.customerid}', "
            f"creatorid='{self.creatorid}', "
            f"createtime='{self.createtime}', "
            f"resolvetime='{self.resolvetime}', "
            f"source='{self.source}', "
            f"priority='{self.priority}', "
            f"deleted='{self.deleted}', "
            f"deltime='{self.deltime}', "
            f"deluserid='{self.deluserid}', "
            f"address_id='{self.address_id}', "
            f"nodeid='{self.nodeid}', "
            f"netnodeid='{self.netnodeid}' ) "
        )
