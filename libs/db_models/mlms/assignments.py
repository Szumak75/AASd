# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 01.12.2023

Purpose: Redefine lms Assignment class.
"""

from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from libs.db_models.mlms.tariffs import MTariff
from libs.db_models.mlms.nodeassignments import MNodeAssignment
from libs.db_models.lms.assignments import Assignment


class MAssignment(Assignment):
    """LMS assignments table."""

    tariffid: Mapped[int] = mapped_column(ForeignKey("tariffs.id"))
    customerid: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    tariff: Mapped[Optional["MTariff"]] = relationship(back_populates="assignments")
    nodeassignment: Mapped[Optional["MNodeAssignment"]] = relationship(
        back_populates="assignment"
    )


# #[EOF]#######################################################################
