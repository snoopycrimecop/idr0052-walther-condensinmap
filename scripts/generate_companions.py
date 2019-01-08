#!/usr/bin/env python
# Generate companion files

import glob
import os
from os.path import dirname, join, abspath
from ome_model.experimental import Image, create_companion
import logging
import sys

DEBUG = int(os.environ.get("DEBUG", logging.INFO))
IMAGE_TYPES = {
    'raw': 'rawtif',
    'mask': 'masktif',
    'conc': 'conctif',
}

BASE_DIRECTORY = join(dirname(abspath(dirname(sys.argv[0]))), 'companions')
folders = [join(BASE_DIRECTORY, x) for x in os.listdir(BASE_DIRECTORY)]
folders = sorted(filter(os.path.isdir, folders))
logging.info("Found %g folders under %s" % (len(folders), BASE_DIRECTORY))

for folder in folders:
    logging.debug("Finding cells under %s" % folder)
    cells = [x for x in glob.glob(folder + "/*")
             if os.path.isdir(x) and not x.endswith("Calibration")]
    for cell in cells:
        images = []

        # Raw TIFFs
        rawtiffs = sorted(map(
            os.path.basename, glob.glob("%s/rawtif/*" % cell)))
        assert len(rawtiffs) == 40

        image = Image("Raw", 256, 256, 31, 3, 40, order="XYZCT", type="uint16")
        image.add_channel("POI", 0)
        image.add_channel("NUC", 0)
        image.add_channel("NEG_Dextran", 0)
        for i in range(40):
            image.add_tiff(
                '%s/rawtif/%s' % (os.path.basename(cell), rawtiffs[i]),
                c=0, z=0, t=i, ifd=0, planeCount=93)
        images.append(image)

        # Mask TIFFs
        masktiffs = sorted(map(
            os.path.basename, glob.glob("%s/masktif/*" % cell)))
        image = Image("Mask", 256, 256, 31, 1, 40, order="XYZCT", type="int8")
        image.add_channel("Mask", 0)
        for i in range(40):
            image.add_tiff(
                '%s/masktif/%s' % (os.path.basename(cell), masktiffs[i]),
                c=0, z=0, t=i, ifd=0, planeCount=31)
        images.append(image)

        conctiffs = sorted(map(
            os.path.basename, glob.glob("%s/conctif/*" % cell)))
        image = Image("FCS", 256, 256, 31, 1, 40, order="XYZCT", type="float")
        image.add_channel("Concentration", 0)
        for i in range(40):
            image.add_tiff(
                '%s/conctif/%s' % (os.path.basename(cell), conctiffs[i]),
                c=0, z=0, t=i, ifd=0, planeCount=31)
        images.append(image)

        create_companion(images=images, out=cell + '.companion.ome')
