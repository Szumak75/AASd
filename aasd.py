#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 06.11.2023

  Purpose: AASd main project starting file.
"""

import sys

from server.daemon import AASd

if __name__ == "__main__":
    server = AASd()
    server.run()
    sys.exit(0)


# #[EOF]#######################################################################
