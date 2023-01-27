# This file is part of the FifoCI project.
# Copyright (c) 2023 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

from django.conf import settings
from django.core.files.storage import default_storage
from django.db.utils import IntegrityError
from .models import FifoTest, Result, Version, Type

import contextlib
import logging
import os.path
import subprocess
import tempfile


def find_first_parent(parents):
    """Takes a sorted list of parents of a revision and returns the first
    existing one.
    """
    versions = Version.objects.filter(hash__in=parents)
    existing = {v.hash: v for v in versions}
    for parent_hash in parents:
        if parent_hash in existing:
            return existing[parent_hash], parent_hash
    return None, parents[0]


def get_or_create_ver(rev):
    """Tries to either get an existing Version object for a given revision, or
    creates a new one and fills up all the required information.
    """
    try:
        obj = Version.objects.get(hash=rev["hash"])
    except Version.DoesNotExist:
        obj = Version()
        obj.hash = rev["hash"]
        obj.name = rev["name"]
        obj.submitted = rev["submitted"]

        parent, parent_hash = find_first_parent(rev["parents"])
        obj.parent = parent
        obj.parent_hash = parent_hash

        try:
            obj.save()
        except IntegrityError:
            obj = Version.objects.get(hash=rev["hash"])
    return obj, obj.parent


@contextlib.contextmanager
def pngcrushed(fp):
    if settings.PNGCRUSH_CMD is None:
        yield fp
    else:
        with tempfile.TemporaryDirectory(prefix="fifoci-import") as td:
            unopt_fn = os.path.join(td, "unopt.png")
            opt_fn = os.path.join(td, "opt.png")

            with open(unopt_fn, "wb") as unopt_fp:
                unopt_fp.write(fp.read())

            ret = subprocess.run(
                [settings.PNGCRUSH_CMD, unopt_fn, opt_fn], capture_output=True
            )
            if ret.returncode != 0:
                logging.warning("failed to pngcrush, invalid PNG file?")

            if os.path.exists(opt_fn):
                with open(opt_fn, "rb") as fp:
                    yield fp
            else:
                with open(unopt_fn, "rb") as fp:
                    yield fp


def import_result(dff, type, ver, parent, result_meta, images):
    """Imports a result to the database. Also exports the image files to
    media storage if not yet present.
    """
    try:
        r = Result.objects.get(dff=dff, type=type, ver=ver)
    except Result.DoesNotExist:
        r = Result()
        r.dff = dff
        r.type = type
        r.ver = ver

    if result_meta["failure"]:
        r.hashes = ""
    else:
        r.hashes = ",".join(result_meta["hashes"])

    try:
        old_r = Result.objects.get(dff=dff, type=type, ver=parent)
        r.has_change = old_r.hashes != r.hashes
        r.first_result = False
    except Result.DoesNotExist:
        r.has_change = False
        r.first_result = True

    base_path = os.path.join(settings.MEDIA_ROOT, "results")
    for hash in result_meta["hashes"]:
        img_path = os.path.join(base_path, f"{hash}.png")
        if default_storage.exists(img_path):
            continue

        with pngcrushed(images[hash]) as ifp:
            with default_storage.open(img_path, "wb") as ofp:
                ofp.write(ifp.read())

    r.save()
    return r
