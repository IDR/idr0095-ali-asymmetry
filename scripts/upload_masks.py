#! /usr/bin/env python

import argparse
impor glob
import logging
import omero.cli
import omero.gateway
from omero_upload import upload_ln_s
import os.path
import sys

NAMESPACE = 'openmicroscopy.org/idr/analysis/original'
MIMETYPE = 'image/tiff'

log = logging.getLogger()


def find_masks(project):
    mask_map = {}
    datasets = project.listChildren()
    for dataset in datasets:
        log.debug("Entering %s" % dataset.getName())
        images = dataset.listChildren()
        for image in images:
            log.debug("Finding mask for %s" % image.getName())
            client_paths = image.getImportedImageFilePaths()['client_paths']
            assert len(client_paths) == 1
            (base, extension) = os.path.splitext(client_paths[0])
            assert extension == '.nd2', "%s is not a ND2" % client_paths[0]
            mask_folder = os.path.join("/", base)

            mask_name = "%s-%03d-Mask.tif" % (
                os.path.basename(base), image.series + 1)
            mask_path = os.path.join(mask_folder, mask_name)
            if not os.path.exists(mask_path):
                log.error("%s does not exist" % mask_path)
            else:
                mask_map[image] = mask_path
    return mask_map


def check_unused_masks(mask_paths):
    tiff_files = set(glob.glob(
        '/uod/idr/filesets/idr0095-ali-asymmetry/20200831-ftp/**/*.tif'))
    missing_masks = tiff_files.difference(mask_paths))
    for f in missing_masks:
        log.error("%s is not associated with an image" % f)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--verbose', '-v', action='count', default=0,
        help='Increase the command verbosity')
    parser.add_argument(
        '--quiet', '-q', action='count', default=0,
        help='Decrease the command verbosity')
    args = parser.parse_args(argv)

    logging.basicConfig(
            level=logging.INFO - 10 * args.verbose + 10 * args.quiet)
    with omero.cli.cli_login() as c:
        conn = omero.gateway.BlitzGateway(client_obj=c.get_client())
        mask_map = {}
        for experiment in ['experimentA', 'experimentB', 'experimentC']:
            project = conn.getObject(
                'Project',
                attributes={'name': 'idr0095-ali-asymmetry/%s' % experiment})
            log.info("Entering %s" % project.getName())
            mask_map.update(find_masks(project))

    # Check all masks are associated with an image
    check_unused_masks(set(mask_map.values()))


if __name__ == "__main__":
    main(sys.argv[1:])
