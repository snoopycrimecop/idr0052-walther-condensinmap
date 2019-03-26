#!/usr/bin/env python

# WARNING: This script will use your current OMERO login session if one
# exists. If you want to use a different login ensure you logout first.

import os
import omero.clients
import omero.cli
from omero_upload import upload_ln_s

DRYRUN = False
OMERO_DATA_DIR = '/data/OMERO'
NAMESPACE = 'openmicroscopy.org/idr/analysis/original'


def get_mask_files(im):
    raw_paths = sorted(
        p for p in im.getImportedImageFilePaths()['client_paths']
        if not p.endswith('.companion.ome'))
    raw_dir = set(os.path.dirname(p) for p in raw_paths)
    assert len(raw_dir) == 1, raw_dir
    raw_dir = '/' + raw_dir.pop()
    filenames = sorted(os.path.basename(p) for p in raw_paths)

    raw_dir = os.path.realpath(raw_dir)
    mask_dir = raw_dir.replace('/raw', '/mask')
    # print(raw_dir, mask_dir)

    mask_files = [os.path.join(mask_dir, f) for f in filenames]
    for f in mask_files:
        assert os.path.exists(f), f
    return mask_files, filenames


def get_label_files_in_t_order(im, filenames, check=True):
    maskfile_map = {}
    for ann in im.listAnnotations():
        try:
            f = ann.getFile()
            filename = f.name
            if filename in filenames:
                maskfile_map[filename] = os.path.join(f.path, f.name)
        except AttributeError:
            continue
    if check:
        assert len(maskfile_map) == im.getSizeT()
    return [maskfile_map[k] for k in sorted(maskfile_map)]


def get_images(conn):
    for pname in (
        'idr0052-walther-condensinmap/experimentA',
    ):
        project = conn.getObject('Project', attributes={'name': pname})
        for dataset in project.listChildren():
            if not dataset.name.endswith(' raw'):
                continue
            for image in dataset.listChildren():
                yield image


def main(conn):
    for im in get_images(conn):
        print('Image: %d' % im.id)
        mask_files, filenames = get_mask_files(im)
        attached = set(get_label_files_in_t_order(im, filenames, check=False))
        for mf in mask_files:
            if mf in attached:
                continue

            print('Uploading: %s' % mf)
            if not DRYRUN:
                fo = upload_ln_s(conn.c, mf, OMERO_DATA_DIR, 'image/tiff')
                fa = omero.model.FileAnnotationI()
                fa.setFile(fo._obj)
                fa.setNs(omero.rtypes.rstring(NAMESPACE))
                fa = conn.getUpdateService().saveAndReturnObject(fa)
                fa = omero.gateway.FileAnnotationWrapper(conn, fa)
                im.linkAnnotation(fa)


if __name__ == '__main__':
    with omero.cli.cli_login() as c:
        conn = omero.gateway.BlitzGateway(client_obj=c.get_client())
        main(conn)
