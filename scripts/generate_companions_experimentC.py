#!/usr/bin/env python
# Generate companion files

import glob
import os
from os.path import dirname, join, abspath
from ome_model.experimental import Image, create_companion
import logging
import sys

DEBUG = int(os.environ.get("DEBUG", logging.INFO))


BASE_DIRECTORY = join(
    dirname(abspath(dirname(sys.argv[0]))), 'experimentC', 'companions')
folders = [join(BASE_DIRECTORY, x) for x in os.listdir(BASE_DIRECTORY)]
folders = sorted(filter(os.path.isdir, folders))
logging.info("Found %g folders under %s" % (len(folders), BASE_DIRECTORY))

for folder in folders:
    logging.debug("Finding cells under %s" % folder)
    cells = [x for x in glob.glob(folder + "/*") if os.path.isdir(x)]
    for cell in cells:
        rawtiffs = sorted(map(
            os.path.basename, glob.glob("%s/*.tif" % cell)))
        # Each folder contains 2 multi-page TIFFs, one for each channel
        assert len(rawtiffs) == 2

        # Image Dimensions
        # TODO: use pylibtiff to determine sizeX and sizeY using e.g. Hoechst
        SIZE_X = 142
        SIZE_Y = 236
        SIZE_Z = 29

        # Create 2-channel image
        image = Image(
            cell, SIZE_X, SIZE_Y, SIZE_Z, 2, 1, order="XYZCT", type="uint16")
        image.add_channel("Hoechst", -1)
        image.add_channel("Condensin", -1)

        for i in range(len(rawtiffs)):
            image.add_tiff("%s/%s" % (
                os.path.basename(cell), rawtiffs[i]), c=i, z=0, t=0, ifd=0,
                planeCount=SIZE_Z)
        create_companion(images=[image], out=cell + '.companion.ome')
