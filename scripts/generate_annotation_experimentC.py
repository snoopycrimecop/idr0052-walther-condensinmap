#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Generate annotation CSV from assays file

import csv
from experimentA import get_protein
import itertools
import logging
import os
from os.path import join, dirname, abspath
import sys

DEBUG = int(os.environ.get("DEBUG", logging.INFO))
EXPERIMENT_DIRECTORY = join(
    dirname(abspath(dirname(sys.argv[0]))), 'experimentC')
ASSAYS_FILE_SINGLE = join(
    EXPERIMENT_DIRECTORY, 'STED_single_colour_assay_file.txt')
ASSAYS_FILE_DOUBLE = join(
    EXPERIMENT_DIRECTORY, 'STED_double_colour_assay_file.txt')
ANNOTATION_FILE = join(
    EXPERIMENT_DIRECTORY, 'idr0052-experimentC-annotation.csv')
KEYS = ["Dataset Name", "Image File"]


with open(ANNOTATION_FILE, 'w') as target_file:
    target_csv = csv.writer(
        target_file, delimiter=',', lineterminator='\n')

    with open(ASSAYS_FILE_SINGLE, 'r') as assay_file:
        source_csv = csv.reader(assay_file, delimiter='\t')
        source_headers = next(source_csv)

        # Create index and write CSV headers
        index = {key: source_headers.index(key) for key in source_headers}
        columns_to_drop = sorted(
            [index["Dataset Name"], index["Image File"]], reverse=True)
        for i in columns_to_drop:
            del source_headers[i]
        target_headers = ['Dataset Name', 'Image Name'] + source_headers
        target_csv.writerow(target_headers)

        # Ensure all annotations are consistent pairwise
        for rows in itertools.izip_longest(*[source_csv] * 2):
            for i in range(len(rows[0])):
                if i != index["Image File"]:
                    assert rows[0][i] == rows[1][i], rows[0][i]

            # Write row in CSV file
            assay_name = rows[0][index["Dataset Name"]]
            dataset_name = get_protein(assay_name)
            image_name = rows[0][index["Assay Name"]] + ".companion.ome"
            for i in columns_to_drop:
                del rows[0][i]
            target_row = [dataset_name, image_name] + rows[0]
            target_csv.writerow(target_row)

    with open(ASSAYS_FILE_DOUBLE, 'r') as assay_file:
        source_csv = csv.reader(assay_file, delimiter='\t')
        source_headers = next(source_csv)

        # Create index and check CSV headers are identical
        index = {key: source_headers.index(key) for key in source_headers}
        columns_to_drop = sorted(
            [index["Dataset Name"], index["Image File"]], reverse=True)
        for i in columns_to_drop:
            del source_headers[i]
        assert (['Dataset Name', 'Image Name'] + source_headers ==
                target_headers)

        # Ensure all annotations are consistent pairwise
        for rows in itertools.izip_longest(*[source_csv] * 2):
            for i in range(len(rows[0])):
                if i != index["Image File"] and i != index["Dataset Name"]:
                    assert rows[0][i] == rows[1][i], rows[0][i]

            # Write row in CSV file
            dataset_name = "NCAPH2 NCAPH"
            image_name = rows[0][index["Assay Name"]] + ".companion.ome"
            for i in columns_to_drop:
                del rows[0][i]
            target_row = [dataset_name, image_name] + rows[0]
            target_csv.writerow(target_row)
