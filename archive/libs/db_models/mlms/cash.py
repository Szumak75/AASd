# -*- coding: UTF-8 -*-
"""MLMS cash model extension.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-12-01

Purpose: Extend the LMS cash model with MLMS-specific relationships.
"""

from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from libs.db_models.lms.cash import Cash
from libs.db_models.mlms.documents import MDocument


class MCash(Cash):
    """Represent the MLMS cash ORM model."""

    customerid: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    docid: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    doc: Mapped[Optional["MDocument"]] = relationship("MDocument")


# #[EOF]#######################################################################
