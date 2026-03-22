#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 06.11.2023

  Purpose: AASd main project starting file.
"""

import sys
import os

from server.daemon import AASd

if __name__ == "__main__":
    # change current directory to main script location
    # to find modules correctly
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    server = AASd()
    server.run()
    sys.exit(0)


# #[EOF]#######################################################################
