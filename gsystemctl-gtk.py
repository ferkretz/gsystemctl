#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys

if __package__ is None:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(CURRENT_DIR, './src'))
    __package__ = os.path.basename(CURRENT_DIR)

from gsystemctl.ui.gtk4.application import run

if __name__ == '__main__':
    run()
