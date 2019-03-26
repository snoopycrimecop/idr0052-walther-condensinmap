#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Generate annotation CSV from assays file

import csv
from experimentA import get_protein, get_date, EXPERIMENT_DIRECTORY
import logging
import os
from os.path import join

DEBUG = int(os.environ.get("DEBUG", logging.INFO))
ASSAYS_FILE = join(EXPERIMENT_DIRECTORY, 'MitoSys_assay_file.txt')
ANNOTATION_FILE = join(
    EXPERIMENT_DIRECTORY, 'idr0052-experimentA-annotation.csv')
KEYS = ["Dataset Name", "Image File"]


with open(ASSAYS_FILE, 'r') as input_file:
    with open(ANNOTATION_FILE, 'w') as target_file:
        # Read original assay file
        source_csv = csv.reader(input_file, delimiter='\t')
        source_headers = next(source_csv)

        # Create index
        index = {key: source_headers.index(key) for key in source_headers}
        columns_to_drop = sorted([index["Dataset Name"], index["Image File"]],
                                 reverse=True)
        # Write CSV headers
        target_csv = csv.writer(
            target_file, delimiter=',', lineterminator='\n')
        for i in columns_to_drop:
            del source_headers[i]
        target_headers = ['Dataset Name', 'Image Name'] + source_headers
        target_csv.writerow(target_headers)

        last_row = []
        for source_row in source_csv:
            # Ignore mask rows
            image_file_path = source_row[index["Comment [Image File Path]"]]
            if 'masktif' in image_file_path:
                continue

            # Ensure all annotations are consistent for all timepoints
            if not source_row[index["Image File"]].endswith("T0001.tif"):
                for i in range(len(source_row)):
                    if i != index["Image File"]:
                        assert source_row[i] == last_row[i]
                continue
            last_row = list(source_row)

            # Generate imported dataset and image names from
            assay_name = source_row[index["Assay Name"]]
            protein = get_protein(assay_name)
            date = get_date(assay_name)
            if 'conctif' in image_file_path:
                dataset_name = "%s %s conc" % (protein, date)
            else:
                dataset_name = "%s %s raw" % (protein, date)
            image_name = source_row[index["Dataset Name"]] + ".companion.ome"

            # Write row in CSV file
            for i in columns_to_drop:
                del source_row[i]
            target_row = [dataset_name, image_name] + source_row
            target_csv.writerow(target_row)
