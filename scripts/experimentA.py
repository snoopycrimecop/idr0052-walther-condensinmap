#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Utility functions shared between experimentA scripts

import os
from os.path import basename
import logging

PROTEINS = ["SMC4", "NCAPD3", "NCAPD2", "NCAPDH2", "NCAPH"]


def get_date(folder):
    """Return folder date in ISO 8601 format"""
    x = basename(folder)
    return "20" + x[:2] + "-" + x[2:4] + "-" + x[4:6]


def get_protein(folder):
    """Return folder protein"""
    for protein in PROTEINS:
        if protein in os.path.basename(folder):
            logging.debug("Found protein %s" % protein)
            break
