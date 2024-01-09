# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 01.12.2023

  Purpose: extension for Customer class
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
    """LMS customers table."""

    # time of debt creation
    __debt_time: int = 0
    __pay_time: int = 0

    contacts: Mapped[List["MCustomerContact"]] = relationship("MCustomerContact")
    cash_operations: Mapped[List["MCash"]] = relationship("MCash", order_by=MCash.time)
    nodes: Mapped[List["MNode"]] = relationship("MNode")
    assignments: Mapped[List["MAssignment"]] = relationship("MAssignment")

    @hybrid_property
    def balance(self) -> float:
        """Returns balance of cash operations."""
        balance = 0
        for item in self.cash_operations:
            cash: MCash = item
            if cash.value < 0:
                if cash.docid is not None:
                    doc: Optional[MDocument] = cash.doc
                    if doc and balance >= 0:
                        # self.__debt_time = cash.time
                        self.__debt_time = doc.cdate
                        self.__pay_time = doc.paytime
            balance += cash.value
        return balance

    @property
    def debt_timestamp(self) -> int:
        """Returns time of debt creation."""
        return self.__debt_time

    @property
    def pay_time(self) -> int:
        """Returns pay time as number of deys."""
        if self.__pay_time > 0:
            return self.__pay_time
        return self.paytime

    @hybrid_property
    def has_active_node(self) -> Optional[bool]:
        """Checks active nodes.

        Returns:
        - True, if at last one node is active,
        - False, if no node is active,
        - None, if there are no nodes,
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
        """Return list of Tariffs."""
        out = []
        for item in self.assignments:
            assignment: MAssignment = item
            if assignment.tariff:
                out.append(assignment.tariff)
        # for item in self.nodes:
        # node: MNode = item
        # if node.nodeassignment:
        # for item2 in node.nodeassignment:
        # nas: MNodeAssignment = item2
        # if nas.assignment:
        # asign: MAssignment = nas.assignment
        # if asign.tariff:
        # out.append(asign.tariff)
        return out


# #[EOF]#######################################################################
