# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 07.11.2023

  Purpose: Test
"""

import time
from typing import Dict, List, Optional, Any
from threading import Thread, Event

from libs.base.classes import BModule
from libs.interfaces.modules import IRunModule
from jsktoolbox.libs.base_th import ThBaseObject


class Run_Test(Thread, ThBaseObject, BModule, IRunModule):
    """Test module."""

    def __init__(self) -> None:
        """Constructor."""
        Thread.__init__(self, name=self.c_name)
        self._stop_event = Event()
        self.daemon = True
        self.sleep_period = 5.0

    def run(self) -> None:
        """Main loop."""

        while not self.stopped:
            # someting
            time.sleep(self.sleep_period)

    def stop(self) -> None:
        """Set stop event."""
        self._stop_event.set()

    @property
    def stopped(self) -> bool:
        """Return stop flag."""
        return self._stop_event.is_set()


# #[EOF]#######################################################################
