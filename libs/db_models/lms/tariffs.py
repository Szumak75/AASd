# -*- coding: UTF-8 -*-
"""
Created on 9 oct 2020

@author: szumak@virthost.pl
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import (
    DECIMAL,
    INTEGER,
    SMALLINT,
    TEXT,
    TINYINT,
    VARCHAR,
)

from libs.db_models.base import LmsBase


class Tariff(LmsBase):
    __tablename__ = "tariffs"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # `type` tinyint(4) NOT NULL DEFAULT '1',
    type: Mapped[int] = mapped_column(TINYINT(4), nullable=False, default=1)
    # `value` decimal(9,2) NOT NULL DEFAULT '0.00',
    value: Mapped[float] = mapped_column(DECIMAL(9, 2), nullable=False, default=0.00)
    # `taxid` int(11) NOT NULL,
    taxid: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    # `numberplanid` int(11) DEFAULT NULL,
    numberplanid: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `period` smallint(6) DEFAULT NULL,
    period: Mapped[int] = mapped_column(SMALLINT(6), default=None)
    # `prodid` varchar(255) COLLATE utf8_polish_ci NOT NULL DEFAULT '',
    prodid: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, default="")
    # `uprate` int(11) NOT NULL DEFAULT '0',
    uprate: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `upceil` int(11) NOT NULL DEFAULT '0',
    upceil: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `downrate` int(11) NOT NULL DEFAULT '0',
    downrate: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `downceil` int(11) NOT NULL DEFAULT '0',
    downceil: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `climit` int(11) NOT NULL DEFAULT '0',
    climit: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `plimit` int(11) NOT NULL DEFAULT '0',
    plimit: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `dlimit` int(11) NOT NULL DEFAULT '0',
    dlimit: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `uprate_n` int(11) DEFAULT NULL,
    uprate_n: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `upceil_n` int(11) DEFAULT NULL,
    upceil_n: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `downrate_n` int(11) DEFAULT NULL,
    downrate_n: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `downceil_n` int(11) DEFAULT NULL,
    downceil_n: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `climit_n` int(11) DEFAULT NULL,
    climit_n: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `plimit_n` int(11) DEFAULT NULL,
    plimit_n: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `domain_limit` int(11) DEFAULT NULL,
    domain_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `alias_limit` int(11) DEFAULT NULL,
    alias_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `sh_limit` int(11) DEFAULT NULL,
    sh_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `www_limit` int(11) DEFAULT NULL,
    www_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `mail_limit` int(11) DEFAULT NULL,
    mail_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `ftp_limit` int(11) DEFAULT NULL,
    ftp_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `sql_limit` int(11) DEFAULT NULL,
    sql_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `cloud_limit` int(11) DEFAULT NULL,
    cloud_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `quota_sh_limit` int(11) DEFAULT NULL,
    quota_sh_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `quota_www_limit` int(11) DEFAULT NULL,
    quota_www_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `quota_mail_limit` int(11) DEFAULT NULL,
    quota_mail_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `quota_ftp_limit` int(11) DEFAULT NULL,
    quota_ftp_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `quota_sql_limit` int(11) DEFAULT NULL,
    quota_sql_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `quota_cloud_limit` int(11) DEFAULT NULL,
    quota_cloud_limit: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `description` text COLLATE utf8_polish_ci NOT NULL,
    description: Mapped[str] = mapped_column(TEXT(), nullable=False)
    # `disabled` tinyint(4) NOT NULL DEFAULT '0',
    disabled: Mapped[int] = mapped_column(TINYINT(4), nullable=False, default=0)
    # `voip_tariff_id` int(11) DEFAULT NULL,
    voip_tariff_id: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `voip_tariff_rule_id` int(11) DEFAULT NULL,
    voip_tariff_rule_id: Mapped[int] = mapped_column(INTEGER(11), default=None)
    # `datefrom` int(11) NOT NULL DEFAULT '0',
    datefrom: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `dateto` int(11) NOT NULL DEFAULT '0',
    dateto: Mapped[int] = mapped_column(INTEGER(11), nullable=False, default=0)
    # `authtype` tinyint(1) NOT NULL DEFAULT '0',
    authtype: Mapped[int] = mapped_column(TINYINT(1), nullable=False, default=0)
    # PRIMARY KEY (`id`),
    # UNIQUE KEY `name` (`name`,`value`,`period`),
    # KEY `type` (`type`),
    # KEY `numberplanid` (`numberplanid`),
    # KEY `voip_tariff_id` (`voip_tariff_id`),
    # KEY `voip_tariff_rule_id` (`voip_tariff_rule_id`),
    # KEY `tariffs_taxid_fkey` (`taxid`),
    # CONSTRAINT `tariffs_ibfk_1` FOREIGN KEY (`numberplanid`) REFERENCES `numberplans` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    # CONSTRAINT `tariffs_ibfk_2` FOREIGN KEY (`voip_tariff_id`) REFERENCES `voip_tariffs` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `tariffs_ibfk_3` FOREIGN KEY (`voip_tariff_rule_id`) REFERENCES `voip_rules` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    # CONSTRAINT `tariffs_taxid_fkey` FOREIGN KEY (`taxid`) REFERENCES `taxes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE

    def __repr__(self) -> str:
        return (
            f"Tariff(id='{self.id}', "
            f"name='{self.name}', "
            f"type='{self.type}', "
            f"value='{self.value}', "
            f"taxid='{self.taxid}', "
            f"numberplanid='{self.numberplanid}', "
            f"period='{self.period}', "
            f"prodid='{self.prodid}', "
            f"uprate='{self.uprate}', "
            f"upceil='{self.upceil}', "
            f"downrate='{self.downrate}', "
            f"downceil='{self.downceil}', "
            f"climit='{self.climit}', "
            f"plimit='{self.plimit}', "
            f"dlimit='{self.dlimit}', "
            f"uprate_n='{self.uprate_n}', "
            f"upceil_n='{self.upceil_n}', "
            f"downrate_n='{self.downrate_n}', "
            f"downceil_n='{self.downceil_n}', "
            f"climit_n='{self.climit_n}', "
            f"plimit_n='{self.plimit_n}', "
            f"domain_limit='{self.domain_limit}', "
            f"alias_limit='{self.alias_limit}', "
            f"sh_limit='{self.sh_limit}', "
            f"www_limit='{self.www_limit}', "
            f"mail_limit='{self.mail_limit}', "
            f"ftp_limit='{self.ftp_limit}', "
            f"sql_limit='{self.sql_limit}', "
            f"cloud_limit='{self.cloud_limit}', "
            f"quota_sh_limit='{self.quota_sh_limit}', "
            f"quota_www_limit='{self.quota_www_limit}', "
            f"quota_mail_limit='{self.quota_mail_limit}', "
            f"quota_ftp_limit='{self.quota_ftp_limit}', "
            f"quota_sql_limit='{self.quota_sql_limit}', "
            f"quota_cloud_limit='{self.quota_cloud_limit}', "
            f"description='{self.description}', "
            f"disabled='{self.disabled}', "
            f"voip_tariff_id='{self.voip_tariff_id}', "
            f"voip_tariff_rule_id='{self.voip_tariff_rule_id}', "
            f"datefrom='{self.datefrom}', "
            f"dateto='{self.dateto}', "
            f"authtype='{self.authtype}' ) "
        )
