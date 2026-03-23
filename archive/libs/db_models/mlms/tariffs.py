# -*- coding: UTF-8 -*-
"""MLMS tariff model extension.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-12-01

Purpose: Extend the LMS tariff model with MLMS-specific relationships.
"""

from typing import List

from sqlalchemy.orm import Mapped, relationship
from libs.db_models.lms.tariffs import Tariff

# from libs.db_models.mlms.assignments import MAssignment


class MTariff(Tariff):
    """Represent the MLMS tariff ORM model."""

    assignments: Mapped[List["MAssignment"]] = relationship(back_populates="tariff") # type: ignore


# #[EOF]#######################################################################
