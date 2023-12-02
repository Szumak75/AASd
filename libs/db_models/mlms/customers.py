# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 01.12.2023

  Purpose: extension for Custumer class
"""


from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, Text, String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from libs.db_models.lms.customers import Customer
from libs.db_models.mlms.cash import MCash
from libs.db_models.mlms.nodes import MNode
from libs.db_models.mlms.tariffs import MTariff
from libs.db_models.mlms.assignments import MAssignment
from libs.db_models.mlms.customercontacts import MCustomerContact
from libs.db_models.mlms.nodeassignments import MNodeAssignment


class MCustomer(Customer):
    """LMS customers table."""

    # time of debt creation
    __debt_time: int = 0
    __cash_warning: bool = False

    contacts: Mapped[List["MCustomerContact"]] = relationship(
        "MCustomerContact"
    )
    cash_operations: Mapped[List["MCash"]] = relationship("MCash")
    nodes: Mapped[List["MNode"]] = relationship("MNode")
    assignments: Mapped[List["MAssignment"]] = relationship("MAssignment")

    @hybrid_property
    def balance(self) -> int:
        """Returns balance of cash operations."""
        balance = 0
        for item in self.cash_operations:
            cash: MCash = item
            if cash.value < 0:
                if cash.docid is not None:
                    if balance >= 0:
                        self.__debt_time = cash.time
                    balance += cash.value
                else:
                    self.__cash_warning = True
            else:
                balance += cash.value
        return balance

    @property
    def dept_timestamp(self) -> int:
        """Returns time of debt creation."""
        return self.__debt_time

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