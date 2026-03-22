# -*- coding: UTF-8 -*-
"""MLMS node model extension.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-12-01

Purpose: Extend the LMS node model with MLMS-specific relationships.
"""


from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from libs.db_models.lms.nodes import Node
from libs.db_models.mlms.nodeassignments import MNodeAssignment


class MNode(Node):
    """Represent the MLMS node ORM model."""

    ownerid: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    nodeassignment: Mapped[int] = relationship("MNodeAssignment")


# #[EOF]#######################################################################
