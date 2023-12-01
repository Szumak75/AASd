# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 01.12.2023

  Purpose:
"""


from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from libs.db_models.lms.cash import Cash


class MCash(Cash):
    """"""

    customerid: Mapped[int] = mapped_column(ForeignKey("customers.id"))


# #[EOF]#######################################################################
