# -*- coding: UTF-8 -*-
"""MLMS customer model extension.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-12-01

Purpose: Extend the LMS customer model with business-oriented relationships and helpers.
"""


from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, Text, String
from sqlalchemy.orm import Mapped, relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property

from libs.db_models.lms.customers import Customer
from libs.db_models.mlms.cash import MCash
from libs.db_models.mlms.nodes import MNode
from libs.db_models.mlms.tariffs import MTariff
from libs.db_models.mlms.assignments import MAssignment
from libs.db_models.mlms.customercontacts import MCustomerContact
from libs.db_models.mlms.nodeassignments import MNodeAssignment
from libs.db_models.mlms.documents import MDocument


class MCustomer(Customer):
    """Represent the MLMS customer ORM model."""

    # time of debt creation
    __debt_time: int = 0
    __pay_time: int = 0

    contacts: Mapped[List["MCustomerContact"]] = relationship("MCustomerContact")
    cash_operations: Mapped[List["MCash"]] = relationship("MCash", order_by=MCash.time)
    nodes: Mapped[List["MNode"]] = relationship("MNode")
    assignments: Mapped[List["MAssignment"]] = relationship("MAssignment")

    @hybrid_property
    def sum_cash(self) -> float:
        """Return the sum of all customer cash operations."""
        if self.cash_operations:
            return sum(cash.value for cash in self.cash_operations)
        return 0.0

    @hybrid_property
    def balance(self) -> float:
        """Return the current balance derived from cash operations."""
        balance: float = self.sum_cash
        if balance >= 0:
            return balance

        # detailed analysis
        balance = 0
        for cash in self.cash_operations:
            if cash.value < 0:
                if cash.docid is not None:
                    doc: Optional[MDocument] = cash.doc
                    if doc and balance >= 0 and (balance + cash.value) < 0:
                        # self.__debt_time = cash.time
                        self.__debt_time = doc.cdate
                        self.__pay_time = doc.paytime
            balance += cash.value
            if balance >= 0:
                self.__debt_time = 0
        return balance

    @property
    def debt_timestamp(self) -> int:
        """Return the timestamp when the outstanding debt started."""
        return self.__debt_time

    @property
    def pay_time(self) -> int:
        """Return the effective payment term in days."""
        if self.__pay_time > 0:
            return self.__pay_time
        return self.paytime

    @hybrid_property
    def has_active_node(self) -> Optional[bool]:
        """Check whether the customer has at least one active node.

        ### Returns:
        Optional[bool] - `True` when any node is active, `False` when nodes exist
        but all are inactive, or `None` when no nodes are assigned.
        """
        count = 0
        test = False
        for item in self.nodes:
            count += 1
            node: MNode = item
            if node.access:
                test = True
        if count > 0:
            return test
        return None

    @hybrid_property
    def tariffs(self) -> List[MTariff]:
        """Return the list of tariffs assigned to the customer."""
        out = []
        for item in self.assignments:
            assignment: MAssignment = item
            if assignment.tariff:
                out.append(assignment.tariff)
        return out


# #[EOF]#######################################################################
