# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 01.12.2023

  Purpose:
"""

# ls *.py|grep -v -E '^_' | sed -e 's/\.py//'|sed -e 's/\(.*\)/from libs.db_models.mlms.\1 import */' >> __init__.py

from libs.db_models.mlms.assignments import *
from libs.db_models.mlms.cash import *
from libs.db_models.mlms.customercontacts import *
from libs.db_models.mlms.customers import *
from libs.db_models.mlms.nodeassignments import *
from libs.db_models.mlms.nodes import *
from libs.db_models.mlms.tariffs import *
