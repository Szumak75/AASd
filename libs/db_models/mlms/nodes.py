# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 01.12.2023

Purpose: Redefine the lms Node class.
"""


from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from libs.db_models.lms.nodes import Node
from libs.db_models.mlms.nodeassignments import MNodeAssignment


class MNode(Node):
    """LMS nodes table."""

    ownerid: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    nodeassignment: Mapped[int] = relationship("MNodeAssignment")


# #[EOF]#######################################################################
