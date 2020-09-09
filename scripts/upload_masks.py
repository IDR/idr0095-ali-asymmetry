#! /usr/bin/env python

import argparse
import glob
import logging
import omero.cli
import omero.gateway
from omero_upload import upload_ln_s
from omero.model import FileAnnotationI, ImageI
from omero_rois import masks_from_label_image
import os.path
from skimage.io import imread
import sys

OMERO_DATA_DIR = "/data/OMERO"
NAMESPACE = 'openmicroscopy.org/idr/analysis/original'
MIMETYPE = 'image/tiff'

# Most masks can easily be associated to the corresponding nd2 file as the
# name of the directory/file prefix matches the nd2 filename. The mapping
# below handles the cases where there is a mismatch in the uploaded data.
MASK_MAPPING = {
    "AO1TO1-Trial1/HG/HG": "AO1TO1-Trial1/HG/HG105",
    "AO1TO2-Trial1/HG/HG": "AO1TO2-Trial1/HG/HG105",
    "AO1TOid-Trial1/HG/HG": "AO1TOid-Trial1/HG/HG105",
    "AO1TOid-Trial2/HG105/HG105": "AO1TOid-Trial2/HG/HG",
    "DAStag_Trial2/DAS/DAS": "DAStag_Trial2/B/B",
    "DAStag_Trial2/DASnoO1V1/DASnoO1V1": "DAStag_Trial2/no/no",
    "Notag_Trial2/ATnoO1V1/ATnoO1V1": "Notag_Trial2/no/no",
    "Notag_Trial3/ATnoO1V1/ATnoO1V1": "Notag_Trial3/no/no",
}

log = logging.getLogger()


def upload_and_link(conn, attachment, image):
    fa = image.getAnnotation(ns=NAMESPACE)
    if fa is not None:
        log.warning("Found file annotation. Skipping upload")
        return
    log.info("Uploading and linking %s to %s" % (attachment, image.getName()))
    fo = upload_ln_s(conn.c, attachment, OMERO_DATA_DIR, MIMETYPE)
    fa = FileAnnotationI()
    fa.setFile(fo._obj)
    fa.setNs(omero.rtypes.rstring(NAMESPACE))
    fa = conn.getUpdateService().saveAndReturnObject(fa)
    fa = omero.gateway.FileAnnotationWrapper(conn, fa)
    image.linkAnnotation(fa)


def link_masks(conn, name):
    mask_paths = []
    project = conn.getObject('Project', attributes={'name': name})
    log.info("Entering %s" % project.getName())
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

            # Handle mismatching repositories
            for source, dest in MASK_MAPPING.items():
                mask_path = mask_path.replace(source, dest)

            if not os.path.exists(mask_path):
                log.error("%s does not exist" % mask_path)
            else:
                mask_paths.append(mask_path)
                upload_and_link(conn, mask_path, image)
                rois = create_rois(mask_path)
                save_rois(conn, image, rois)
    return mask_paths


def create_rois(mask_path):
    masks = masks_from_label_image(
        imread(mask_path), rgba=(255, 255, 255, 128))

    rois = []
    log.debug('Creating %d ROIs' % len(masks))
    for mask in masks:
        roi = omero.model.RoiI()
        roi.addShape(mask)
        rois.append(roi)
    return rois


def save_rois(conn, image, rois):
    log.info('Creating %d ROIs for image %s' % (len(rois), image.name))
    us = conn.getUpdateService()
    for roi in rois:
        roi.setImage(ImageI(image.id, False))
        roi1 = us.saveAndReturnObject(roi)
        assert roi1


def check_unused_masks(mask_paths):
    tiff_files = set(glob.glob(
        '/uod/idr/filesets/idr0095-ali-asymmetry/20200831-ftp/**/**/*.tif'))
    missing_masks = tiff_files.difference(mask_paths)
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
        mask_paths = []
        for experiment in ['experimentA', 'experimentB', 'experimentC']:
            p = link_masks(conn, 'idr0095-ali-asymmetry/%s' % experiment)
            mask_paths.extend(p)

        # Check all masks are associated with an image
        check_unused_masks(set(mask_paths))


if __name__ == "__main__":
    main(sys.argv[1:])
