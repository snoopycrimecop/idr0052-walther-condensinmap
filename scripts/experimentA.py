#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Utility functions shared between experimentA scripts

import logging
from os.path import basename, dirname, join, abspath
import sys

PROTEINS = ["SMC4", "NCAPD3", "NCAPD2", "NCAPH2", "NCAPH"]
EXPERIMENT_DIRECTORY = join(
    dirname(abspath(dirname(sys.argv[0]))), 'experimentA')


def get_date(folder):
    """Return folder date in ISO 8601 format"""
    x = basename(folder)
    return "20" + x[:2] + "-" + x[2:4] + "-" + x[4:6]


def get_protein(folder):
    """Return folder protein"""
    for protein in PROTEINS:
        if protein in basename(folder):
            logging.debug("Found protein %s" % protein)
            return protein
