# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from fifoci.models import FifoTest, Result, Version, Type

import json
import os.path
import shutil
import subprocess
import zipfile


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
        obj = Version.objects.get(hash=rev['hash'])
    except Version.DoesNotExist:
        obj = Version()
        obj.hash = rev['hash']
        obj.name = rev['name']
        obj.submitted = rev['submitted']

        parent, parent_hash = find_first_parent(rev['parents'])
        obj.parent = parent
        obj.parent_hash = parent_hash

        obj.save()
    return obj, obj.parent


def import_result(type, ver, parent, zf, dff_short_name, result):
    """Imports a result to the database. Also exports the image files to
    MEDIA_ROOT.
    """
    try:
        dff = FifoTest.objects.get(shortname=dff_short_name)
    except FifoTest.DoesNotExist:
        print('DFF %r does not exist, skipping.' % dff_short_name)
        return

    try:
        t = Type.objects.get(type=type)
    except Type.DoesNotExist:
        t = Type()
        t.type = type

    try:
        r = Result.objects.get(dff=dff, ver=ver, type=t)
    except Result.DoesNotExist:
        r = Result()
        r.dff = dff
        r.ver = ver
        r.type = t

    if result['failure']:
        r.hashes = ''
    else:
        r.hashes = ','.join(result['hashes'])

    try:
        old_r = Result.objects.get(dff=dff, ver=parent, type=t)
        r.has_change = old_r.hashes != r.hashes
        r.first_result = False
    except Result.DoesNotExist:
        r.has_change = False
        r.first_result = True

    base_path = os.path.join(settings.MEDIA_ROOT, 'results')
    pngcrush = shutil.which('pngcrush') is not None
    for hash in result['hashes']:
        final_img_path = os.path.join(base_path, hash + '.png')
        if os.path.exists(final_img_path):
            continue

        if pngcrush:
            extracted_img_path = final_img_path + '.unopt'
        else:
            extracted_img_path = final_img_path
        zip_path = 'fifoci-result/%s.png' % hash
        open(extracted_img_path, 'wb').write(zf.read(zip_path))
        if pngcrush:
            if subprocess.call(['pngcrush', extracted_img_path,
                                            final_img_path]) == 0:
                os.unlink(extracted_img_path)
            else:
                os.rename(extracted_img_path, final_img_path)
        os.chmod(final_img_path, 0o644)

    r.save()


class Command(BaseCommand):
    help = 'Imports some result zip files into the database.'

    def add_arguments(self, parser):
        parser.add_argument('zip_file', nargs='+', type=str)

    def handle(self, *args, **options):
        for zip_file in options['zip_file']:
            if not os.path.exists(zip_file):
                raise CommandError('%r does not exist' % zip_file)
            with zipfile.ZipFile(zip_file) as zf:
                meta = zf.read('fifoci-result/meta.json').decode('utf-8')
                meta = json.loads(meta)

                ver, parent = get_or_create_ver(meta['rev'])
                for dff_short_name, result in meta['results'].items():
                    import_result(meta['type'], ver, parent, zf,
                                  dff_short_name, result)
