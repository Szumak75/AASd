# -*- coding: UTF-8 -*-
"""MLMS node assignment model extension.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-12-01

Purpose: Extend the LMS node assignment model with MLMS-specific relationships.
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from libs.db_models.lms.nodeassignments import NodeAssignment

# from libs.db_models.mlms.assignments import MAssignment


class MNodeAssignment(NodeAssignment):
    """Represent the MLMS node assignment ORM model."""

    nodeid: Mapped[int] = mapped_column(ForeignKey("nodes.id"))
    assignmentid: Mapped[int] = mapped_column(ForeignKey("assignments.id"))
    assignment: Mapped["MAssignment"] = relationship(back_populates="nodeassignment") # type: ignore


# #[EOF]#######################################################################
