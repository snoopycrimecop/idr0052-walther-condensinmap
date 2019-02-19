#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Generate companion files for experimentA of the idr0052 study. This script
# assumes the following layout for the original data:
#
# <date>_<protein><suffix>/    Folder containing a protein
#   <cell>/                    Measurements for a cell
#     conctif/                 Concentration maps TIFFs (1C, 31Z, 40T)
#     masktif/                 Mask TIFFs (2C, 31Z, 40T)
#     rawtif/                  Raw TIFFs (2C, 31Z, 40T)

import glob
import os
from os.path import dirname, join, abspath, basename
import ome_model.experimental
import logging
import subprocess
import sys

DEBUG = int(os.environ.get("DEBUG", logging.INFO))
PROTEINS = ["SMC4", "NCAPD3", "NCAPD2", "NCAPDH2", "NCAPH"]
BASE_DIRECTORY = "/uod/idr/filesets/idr0052-walther-condensinmap/" \
    "20181113-ftp/MitoSys/"
METADATA_DIRECTORY = join(
    dirname(abspath(dirname(sys.argv[0]))), 'experimentA', 'companions')
FILEPATHS_TSV = join(
    dirname(abspath(dirname(sys.argv[0]))), 'experimentA',
    'idr0052-experimentA-filePaths.tsv')

# Find original folders
folders = [join(BASE_DIRECTORY, x) for x in os.listdir(BASE_DIRECTORY)]
folders = sorted(filter(os.path.isdir, folders))
logging.info("Found %g folders under %s" % (len(folders), BASE_DIRECTORY))


def create_companion(folder, channels, pixeltype):
    """Generate companion file for a given folder containing TIFFs"""
    SIZE_X = 256
    SIZE_Y = 256
    SIZE_Z = 31
    SIZE_T = 40

    tiffs = sorted(map(os.path.basename, glob.glob("%s/*" % folder)))
    assert len(tiffs) == SIZE_T

    # Generate OME Image object
    image = ome_model.experimental.Image(
        basename(folder), SIZE_X, SIZE_Y, SIZE_Z, len(channels), SIZE_T,
        order="XYZCT", type=pixeltype)
    for c in channels:
        image.add_channel(c[0], c[1])
    for i in range(SIZE_T):
        image.add_tiff(
            '%s/%s' % (os.path.basename(folder), tiffs[i]),
            c=0, z=0, t=i, ifd=0, planeCount=SIZE_Z * len(channels))
    # Populate pixel size (in microns)
    image.data['Pixels']['PhysicalSizeX'] = '0.2516'
    image.data['Pixels']['PhysicalSizeY'] = '0.2516'
    image.data['Pixels']['PhysicalSizeZ'] = '0.75'

    # Generate companion OME-XML file
    companion_file = folder + '.companion.ome'
    ome_model.experimental.create_companion(images=[image], out=companion_file)

    # Indent XML for readability
    proc = subprocess.Popen(
        ['xmllint', '--format', '-o', companion_file, companion_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    (output, error_output) = proc.communicate()
    logging.info("Created %s" % companion_file)


def to_iso8601(x):
    return "20" + x[:2] + "-" + x[2:4] + "-" + x[4:6]


if os.path.exists(FILEPATHS_TSV):
    os.remove(FILEPATHS_TSV)
if not os.path.exists(METADATA_DIRECTORY):
    os.mkdir(METADATA_DIRECTORY)
    logging.info("Created %s" % METADATA_DIRECTORY)

for folder in folders:
    # Create protein folder
    protein_folder = join(METADATA_DIRECTORY, basename(folder))
    if not os.path.exists(protein_folder):
        os.mkdir(protein_folder)
        logging.info("Created %s" % protein_folder)

    # Create sub-folders for raw images and concentration maps
    raw_folder = join(protein_folder, 'raw')
    if not os.path.exists(raw_folder):
        os.mkdir(raw_folder)
        logging.info("Created %s" % raw_folder)

    conc_folder = join(protein_folder, 'conc')
    if not os.path.exists(conc_folder):
        os.mkdir(conc_folder)
        logging.info("Created %s" % conc_folder)

    # Identify measured protein and create raw and concentration channels
    for protein in PROTEINS:
        if protein in os.path.basename(folder):
            logging.debug("Found protein %s" % protein)
            break
    raw_channels = [(protein, 16711935), ("DNA", 65535), ("NEG_Dextran", -1)]
    conc_channels = [(protein, -1)]

    cells = [x for x in glob.glob(folder + "/*")
             if os.path.isdir(x) and not x.endswith("Calibration")]
    logging.debug("Found %s cells" % len(cells))

    for cell in cells:
        # Raw images
        raw_cell_folder = join(raw_folder, basename(cell))
        if not os.path.exists(raw_cell_folder):
            os.symlink("%s/rawtif" % cell, raw_cell_folder)
        create_companion(raw_cell_folder, raw_channels, "uint16")

        # Concentration maps
        conc_cell_folder = join(conc_folder, basename(cell))
        if not os.path.exists(conc_cell_folder):
            os.symlink("%s/conctif" % cell, conc_cell_folder)
        create_companion(conc_cell_folder, conc_channels, "float")

    # Add raw and concentration folders to filePaths.tsv
    uod_metadata_folder = join(
        "/uod/idr/metadata/idr0052-walther-condensinmap", "experimentA",
        "companions", basename(folder))
    dataset_name = "%s %s" % (protein, to_iso8601(basename(folder)))
    with open(FILEPATHS_TSV, 'a') as f:
        f.write("Dataset:name:%s\t%s\n" % (
            dataset_name + " raw", join(uod_metadata_folder, "raw")))
        f.write("Dataset:name:%s\t%s\n" % (
            dataset_name + " conc", join(uod_metadata_folder, "conc")))
