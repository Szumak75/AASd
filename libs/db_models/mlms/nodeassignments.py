# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 01.12.2023

  Purpose:
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from libs.db_models.lms.nodeassignments import NodeAssignment
from libs.db_models.mlms.assignments import MAssignment


class MNodeAssignment(NodeAssignment):
    """LMS nodeassignments table."""

    nodeid: Mapped[int] = mapped_column(ForeignKey("nodes.id"))
    assignmentid: Mapped[int] = mapped_column(ForeignKey("assignments.id"))
    assignment: Mapped["MAssignment"] = relationship(back_populates="nodeassignment")


# #[EOF]#######################################################################
