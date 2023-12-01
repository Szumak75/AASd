# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 01.12.2023

  Purpose:
"""


from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from libs.db_models.lms.nodes import Node
from libs.db_models.mlms.nodeassignments import MNodeAssignment


class MNode(Node):
    """"""

    ownerid: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    nodeassignment: Mapped[int] = relationship("MNodeAssignment")


# #[EOF]#######################################################################
