# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

from .models import Version, Result


def recent_changes(request):
    versions = Version.objects.order_by("-ts")[:10]
    versions_with_diff = set(
        res.ver
        for res in Result.objects.select_related("ver").filter(
            ver__in=versions, has_change=True
        )
    )
    recent_changes = [(ver, ver in versions_with_diff) for ver in versions]
    return {"recent_changes": recent_changes}
