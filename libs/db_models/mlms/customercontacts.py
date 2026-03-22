# -*- coding: UTF-8 -*-
"""MLMS customer contact model extension.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-12-01

Purpose: Extend the LMS customer contact model with MLMS-specific mapping details.
"""


from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from libs.db_models.lms.customercontacts import CustomerContact


class MCustomerContact(CustomerContact):
    """Represent the MLMS customer contact ORM model."""

    customerid: Mapped[int] = mapped_column(ForeignKey("customers.id"))


# #[EOF]#######################################################################
