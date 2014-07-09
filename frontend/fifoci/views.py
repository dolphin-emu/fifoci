from django.contrib.staticfiles.views import serve as static_serve
from django.http import JsonResponse
from fifoci.models import FifoTest, Result

import os.path


def home(request):
    return static_serve(request, '/index.html')


def dffs_to_test(request):
    dffs = FifoTest.objects.filter(active=True)
    out = []
    for dff in dffs:
        url = dff.file.url
        filename = os.path.basename(url)
        out.append({'shortname': dff.shortname, 'filename': filename,
                    'url': url})
    return JsonResponse(out, safe=False)


def results_for_version(request, hash):
    results = Result.objects.filter(ver__hash=hash).select_related('dff')
    out = []
    for r in results:
        out.append({
            'type': r.type,
            'dff': {
                'name': r.dff.name,
                'filename': r.dff.filename,
                'shortname': r.dff.shortname,
                'active': r.dff.active,
                'description': r.dff.description,
            },
            'hashes': r.hashes.split(','),
        })
    return JsonResponse(out, safe=False)
