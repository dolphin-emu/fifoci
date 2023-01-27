# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

from django.core.management.base import BaseCommand, CommandError
from fifoci.frontend import importer
from fifoci.frontend.models import FifoTest, Version, Type

import json
import logging
import os.path
import zipfile


class Command(BaseCommand):
    help = "Imports some result zip files into the database."

    def add_arguments(self, parser):
        parser.add_argument("zip_file", nargs="+", type=str)

    def handle(self, *args, **options):
        for zip_file in options["zip_file"]:
            if not os.path.exists(zip_file):
                raise CommandError("%r does not exist" % zip_file)

            with zipfile.ZipFile(zip_file) as zf:
                meta = zf.read("fifoci-result/meta.json").decode("utf-8")
                meta = json.loads(meta)

                type, _ = Type.objects.get_or_create(type=meta["type"])

                ver, parent = importer.get_or_create_ver(meta["rev"])
                for dff_short_name, result in meta["results"].items():
                    try:
                        dff = FifoTest.objects.get(shortname=dff_short_name)
                    except FifoTest.DoesNotExist:
                        logging.warning("Skipping unknown DFF %r", dff_short_name)
                        continue

                    images = {}
                    for h in result["hashes"]:
                        try:
                            images[h] = zf.open(
                                os.path.join("fifoci-result", f"{h}.png"), "r"
                            )
                        except KeyError:
                            continue

                    importer.import_result(dff, type, ver, parent, result, images)
