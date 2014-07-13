from django.http import JsonResponse
from django.shortcuts import render
from fifoci.models import FifoTest, Version, Result

import os.path


N_VERSIONS_TO_SHOW = 20


def home(request):
    data = {'recent_results': []}
    types = list(sorted(Result.objects.values_list('type').distinct()))
    for (type,) in types:
        # Upper bound of results to select to get N versions.
        n_results = N_VERSIONS_TO_SHOW * FifoTest.objects.count()

        recent_results = (Result.objects.select_related('ver')
                                        .filter(type=type, has_change=True)
                                        .order_by('-ver__ts')
                                        [:n_results])

        # Get the list of all versions
        versions_set = set()
        versions = []
        for res in recent_results:
            if res.ver.hash not in versions_set:
                versions.append(res.ver)
                versions_set.add(res.ver)
        versions = versions[:N_VERSIONS_TO_SHOW]

        # For each FifoTest, get the list of all results, and insert Nones when
        # results are mising for a version.
        fifo_tests = {dff: {} for dff in FifoTest.objects.filter(active=True)}
        for res in recent_results:
            fifo_tests[res.dff][res.ver] = res
        fifo_tests_list = []
        for dff, test_results in fifo_tests.items():
            fifo_tests_list.append(
                    (dff, [test_results.get(v) for v in versions]))
        fifo_tests_list.sort(key=lambda k: k[0].shortname)

        data['recent_results'].append((type, versions, fifo_tests_list))
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
