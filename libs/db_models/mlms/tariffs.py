# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 01.12.2023

  Purpose:
"""

from typing import List

from sqlalchemy.orm import Mapped, relationship
from libs.db_models.lms.tariffs import Tariff

# from libs.db_models.mlms.assignments import MAssignment


class MTariff(Tariff):
    """"""

    assignments: Mapped[List["MAssignment"]] = relationship(
        back_populates="tariff"
    )


# #[EOF]#######################################################################
