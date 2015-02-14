# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

from django.core.management.base import BaseCommand, CommandError
from fifoci.models import FifoTest, Result, Version

class Command(BaseCommand):
    help = 'Fixes bad data in the database.'

    def handle(self, *args, **options):
        # Try to reparent changes if we have a hash but no ref.
        for ver in Version.objects.filter(parent__isnull=True):
            try:
                parent = Version.objects.get(hash=ver.parent_hash)
                print('Fixing %r: parent is %r' % (ver, parent))
                ver.parent = parent
                ver.save()
            except Version.DoesNotExist:
                continue

        # Look for first_result which are not actually first results.
        for res in Result.objects.select_related('ver', 'ver__parent').filter(
                first_result=True, ver__parent__isnull=False):
            try:
                prev_res = Result.objects.get(ver=res.ver.parent,
                                              type=res.type,
                                              dff=res.dff)
                print('Fixing %r: previous is %r' % (res, prev_res))
                res.has_change = res.hashes != prev_res.hashes
                res.first_result = False
                res.save()
            except Result.DoesNotExist:
                continue

        # Look for changes that are not really changes.
        for res in Result.objects.select_related('ver', 'ver__parent').filter(
                has_change=True, ver__parent__isnull=False):
            try:
                prev_res = Result.objects.get(ver=res.ver.parent,
                                              type=res.type,
                                              dff=res.dff)
                if res.hashes == prev_res.hashes:
                    print('Fixing %r: not really a change' % res)
                    res.has_change = False
                    res.save()
            except Result.DoesNotExist:
                continue
