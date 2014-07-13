from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from fifoci.models import FifoTest, Version, Result

import os.path


N_VERSIONS_TO_SHOW = 20


def _get_recent_results(n, res_per_vers, **cond):
    recent_results = (Result.objects.select_related('ver')
                                    .filter(has_change=True, **cond)
                                    .order_by('-ver__ts')
                                    [:n * res_per_vers])
    versions_set = set()
    versions = []
    for res in recent_results:
        if res.ver not in versions_set:
            versions.append(res.ver)
            versions_set.add(res.ver)
    return versions[:n], recent_results


def home(request):
    data = {'recent_results': []}
    types = list(sorted(Result.objects.values_list('type').distinct()))
    for (type,) in types:
        versions, recent_results = _get_recent_results(N_VERSIONS_TO_SHOW,
                FifoTest.objects.count(), type=type)

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


def dff_view(request, name):
    dff = get_object_or_404(FifoTest, shortname=name)
    versions, recent_results = _get_recent_results(N_VERSIONS_TO_SHOW,
            10, dff=dff)
    types = {t[0]: {} for t in Result.objects.values_list('type')}
    for res in recent_results:
        types[res.type][res.ver] = res
    types_list = []
    for type, test_results in types.items():
        types_list.append((type, [test_results.get(v) for v in versions]))
    types_list.sort(key=lambda k: k[0])

    data = {'dff': dff,
            'versions': versions,
            'types_list': types_list}
    return render(request, 'dff-view.html', dictionary=data)


def version_view(request, hash):
    ver = get_object_or_404(Version, hash=hash)
    results = Result.objects.filter(ver=ver).order_by('type', 'dff__shortname')
    colspan = []
    i = 0
    while i < len(results):
        type = results[i].type
        count = 1
        while i + count < len(results) and results[i + count].type == type:
            count += 1
        colspan += [count] + [0] * count
        i += count
    data = {'ver': ver,
            'results': zip(results, colspan)}
    return render(request, 'version-view.html', dictionary=data)


def dffs_to_test(request):
    dffs = FifoTest.objects.filter(active=True)
    out = []
    for dff in dffs:
        url = dff.file.url
        filename = os.path.basename(url)
        out.append({'shortname': dff.shortname, 'filename': filename,
                    'url': url})
    return JsonResponse(out, safe=False)
