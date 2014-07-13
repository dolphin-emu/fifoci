from fifoci.models import Version, Result


def recent_changes(request):
    versions = Version.objects.order_by('-ts')[:5]
    recent_changes = [
        (ver, bool(Result.objects.filter(ver=ver, has_change=True)))
        for ver in versions]
    return {'recent_changes': recent_changes}
