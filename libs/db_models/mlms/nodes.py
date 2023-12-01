# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 01.12.2023

  Purpose:
"""

from typing import List, Optional

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
from libs.db_models.lms.nodes import Node
from libs.db_models.lms.tariffs import Tariff
from libs.db_models.lms.assignments import Assignment
from libs.db_models.lms.nodeassignments import NodeAssignment
from libs.db_models.lms.nodes import Node


class MNode(Node):
    """"""

    ownerid: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    nodeassignment: Mapped[int] = relationship("NodeAssignment")


# #[EOF]#######################################################################
