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
KEYS = [
    "Assay Name", "Dataset Name", "Image File", "Comment [Image File Path]"]

with open(ASSAYS_FILE, 'r') as input_file:
    with open(ANNOTATION_FILE, 'w') as target_file:
        source_csv = csv.reader(input_file, delimiter='\t')
        source_headers = next(source_csv)
        index = {key: source_headers.index(key) for key in KEYS}

        # Write CSV headers
        target_csv = csv.writer(target_file, delimiter='\t')
        target_headers = ['Dataset Name', 'Image Name'] + source_headers
        target_csv.writerow(target_headers)
        for source_row in source_csv:
            # Ignore mask rows
            image_file_path = source_row[index["Comment [Image File Path]"]]
            if 'masktif' in image_file_path:
                continue
            if not source_row[index["Image File"]].endswith("T0001.tif"):
                continue

            assay_name = source_row[index["Assay Name"]]
            protein = get_protein(assay_name)
            date = get_date(assay_name)

            # Map dataset name and image name
            if 'conctif' in image_file_path:
                dataset_name = "%s %s conc" % (protein, date)
            else:
                dataset_name = "%s %s raw" % (protein, date)
            image_name = source_row[index["Dataset Name"]] + ".companion.ome"

            # Write CSV row
            target_row = [dataset_name, image_name] + source_row
            target_csv.writerow(target_row)
