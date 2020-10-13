#! /usr/bin/env python3

import argparse
import logging
import omero.cli
import omero.gateway
import re
import sys

PATTERN = re.compile(r"^(?P<name>\w+) \[.*\.nd2 \(series (?P<series>\d+)\)\]$")

log = logging.getLogger()


def rename_images(conn, name):
    project = conn.getObject('Project', attributes={'name': name})
    log.debug("Entering %s" % project.getName())
    datasets = project.listChildren()
    for dataset in datasets:
        log.debug("Entering %s" % dataset.getName())
        images = dataset.listChildren()
        for image in images:
            image_name = image.getName()
            m = PATTERN.match(image_name)
            if not m:
                log.error(f"Could not parse {image_name}")
                continue
            new_name = "%s [%s]" % (m.group("name"), m.group("series"))
            log.debug(f"Renaming {image_name} as {new_name}")


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--verbose', '-v', action='count', default=0,
        help='Increase the command verbosity')
    parser.add_argument(
        '--quiet', '-q', action='count', default=0,
        help='Decrease the command verbosity')
    args = parser.parse_args(argv)

    default_level = logging.INFO - 10 * args.verbose + 10 * args.quiet
    logging.basicConfig(level=default_level)
    with omero.cli.cli_login() as c:
        conn = omero.gateway.BlitzGateway(client_obj=c.get_client())
        for experiment in ['experimentA', 'experimentB', 'experimentC']:
            rename_images(conn, 'idr0095-ali-asymmetry/%s' % experiment)


if __name__ == "__main__":
    main(sys.argv[1:])
