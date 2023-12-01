# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 01.12.2023

  Purpose: extension for Custumer class
"""


from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import (
    DECIMAL,
    INTEGER,
    MEDIUMTEXT,
    SMALLINT,
    TEXT,
    TINYINT,
    VARCHAR,
)
from sqlalchemy.ext.hybrid import hybrid_property

from libs.db_models.base import LmsBase
from libs.db_models.lms.customercontacts import CustomerContact
from libs.db_models.lms.cash import Cash
from libs.db_models.lms.nodes import Node
from libs.db_models.lms.tariffs import Tariff
from libs.db_models.lms.assignments import Assignment
from libs.db_models.lms.nodeassignments import NodeAssignment
from libs.db_models.lms.customers import Customer


class MCustomer(Customer):
    """"""

    # time of debt creation
    __debt_time: int = 0
    __cash_warning: bool = False

    contacts: Mapped[List["CustomerContact"]] = relationship(
        "CustomerContact"
    )
    cash_operations: Mapped[List["Cash"]] = relationship("Cash")
    nodes: Mapped[List["Node"]] = relationship("Node")
    assignments: Mapped[List["Assignment"]] = relationship("Assignment")

    @hybrid_property
    def balance(self) -> int:
        """Returns balance of cash operations."""
        balance = 0
        for item in self.cash_operations:
            cash: Cash = item
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
            node: Node = item
            if node.access:
                test = True
        if count > 0:
            return test
        return None

    @hybrid_property
    def tariffs(self) -> List[Tariff]:
        """Return list of Tariffs."""
        out = []
        for item in self.assignments:
            assignment: Assignment = item
            if assignment.tariff:
                out.append(assignment.tariff)
        # for item in self.nodes:
        # node: Node = item
        # if node.nodeassignment:
        # for item2 in node.nodeassignment:
        # nas: NodeAssignment = item2
        # if nas.assignment:
        # asign: Assignment = nas.assignment
        # if asign.tariff:
        # out.append(asign.tariff)
        return out


# #[EOF]#######################################################################
