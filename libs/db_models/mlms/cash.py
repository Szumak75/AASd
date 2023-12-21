# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 01.12.2023

  Purpose: Redefine the lms Cash class.
"""

from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from libs.db_models.lms.cash import Cash
from libs.db_models.mlms.documents import MDocument


class MCash(Cash):
    """LMS cash table."""

    customerid: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    docid: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    doc: Mapped[Optional["MDocument"]] = relationship("MDocument")


# #[EOF]#######################################################################
