from django.http import JsonResponse
from django.shortcuts import render
from fifoci.models import FifoTest, Result

import os.path


def home(request):
    # TODO(delroth): This is fake data for testing.
    data = {
        'recent_results': [
            ('linux-opengl', [
            ]),
            ('linux-software', [
            ]),
            ('windows-d3d', [
            ]),
        ],
    }
    return render(request, 'index.html', dictionary=data)


def dffs_to_test(request):
    dffs = FifoTest.objects.filter(active=True)
    out = []
    for dff in dffs:
        url = dff.file.url
        filename = os.path.basename(url)
        out.append({'shortname': dff.shortname, 'filename': filename,
                    'url': url})
    return JsonResponse(out, safe=False)
