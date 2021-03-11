#!/usr/bin/env python3
"""
Polyglot v3 node server Volumio Media Server control.
Copyright (C) 2021 Robert Paauwe
"""
import udi_interface
import sys
from nodes import controller

LOGGER = udi_interface.LOGGER

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()
        controller.Controller(polyglot, "controller", "controller", "Volumio")
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

