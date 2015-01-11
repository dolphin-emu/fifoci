# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

from fifoci.models import Version, Result


def recent_changes(request):
    versions = Version.objects.order_by('-ts')[:10]
    recent_changes = [
        (ver, bool(Result.objects.filter(ver=ver, has_change=True)))
        for ver in versions]
    return {'recent_changes': recent_changes}
