# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from fifoci.models import FifoTest, Version, Result, Type

import os
import os.path


N_VERSIONS_TO_SHOW = 35

def home(request):
    data = {'recent_results': []}
    types = Type.objects.order_by('type')
    num_dff = FifoTest.objects.count()
    active_dff = FifoTest.objects.filter(active=True)
    for type in types:
        should_display = Q(results__has_change=True) | Q(results__first_result=True)
        versions = Version.objects.filter(
                      should_display,
                      submitted=True,
                      results__type=type,
                   ).distinct('ts','id').order_by('-ts')[:N_VERSIONS_TO_SHOW]
        recent_results = (Result.objects.select_related('ver', 'dff')
	                    .filter(ver__in=list(versions),
	                            dff__active=True,
	                            type=type))

        # For each FifoTest, get the list of all results, and insert Nones when
        # results are mising for a version.
        fifo_tests = {dff: {} for dff in active_dff}
        for res in recent_results:
            fifo_tests[res.dff][res.ver] = res
        fifo_tests_list = []
        for dff, test_results in fifo_tests.items():
            results = [test_results.get(v) for v in versions]
            results = zip(results, results[1:] + [None])
            fifo_tests_list.append((dff, results))
        fifo_tests_list.sort(key=lambda k: k[0].shortname)

        data['recent_results'].append((type, versions, fifo_tests_list))
    return render(request, 'index.html', context=data)


def dff_view(request, name):
    dff = get_object_or_404(FifoTest, shortname=name)

    should_display = Q(results__has_change=True) | Q(results__first_result=True)
    versions = Version.objects.filter(
                  should_display,
                  submitted=True,
                  results__dff=dff,
               ).distinct('ts','id').order_by('-ts')[:N_VERSIONS_TO_SHOW]
    recent_results = (Result.objects.select_related('ver', 'dff', 'type')
	                .filter(ver__in=list(versions),
	                        dff__active=True,
	                        dff=dff))

    types = {t[0]: {} for t in Type.objects.values_list('type')}
    for res in recent_results:
        types[res.type.type][res.ver] = res
    types_list = []
    for type, test_results in types.items():
        results = [test_results.get(v) for v in versions]
        results = zip(results, results[1:] + [None])
        types_list.append((type, results))
    types_list.sort(key=lambda k: k[0])

    data = {'dff': dff,
            'versions': versions,
            'types_list': types_list}
    return render(request, 'dff-view.html', context=data)


def get_version_results(ver, **cond):
    results = Result.objects.select_related('ver', 'dff', 'type').filter(
            ver=ver, **cond).order_by('type', 'dff__shortname')
    if ver.parent:
        parent_results_qs = Result.objects.select_related('ver', 'dff', 'type').filter(
                ver=ver.parent).order_by('type', 'dff__shortname')
        parent_results_dict = {}
        for res in parent_results_qs:
            parent_results_dict[(res.type, res.dff.shortname)] = res
        parent_results = [parent_results_dict.get((res.type,
                                                   res.dff.shortname), None)
                          for res in results]
    else:
        parent_results = [None] * len(results)
    return results, parent_results


def version_view(request, hash):
    ver = get_object_or_404(Version, hash=hash)
    results, parent_results = get_version_results(ver)
    rowspan = []
    i = 0
    while i < len(results):
        type = results[i].type
        count = 1
        while i + count < len(results) and results[i + count].type == type:
            count += 1
        rowspan += [count] + [0] * (count - 1)
        i += count
    data = {'ver': ver,
            'results': zip(results, rowspan, parent_results)}
    return render(request, 'version-view.html', context=data)


def version_view_json(request, hash):
    ver = get_object_or_404(Version, hash=hash)
    results, parent_results = get_version_results(ver, has_change=True)
    data = []
    for r, pr in zip(results, parent_results):
        data.append({'type': r.type, 'dff': r.dff.shortname,
                     'failure': not bool(r.hashes),
                     'url': reverse('compare-view', args=[r.id, pr.id])})
    return JsonResponse(data, safe=False)


def result_view(request, id):
    res = get_object_or_404(Result, pk=id)
    return render(request, 'result-view.html', context={'result': res})


def compare_view(request, curr_id, old_id):
    current = get_object_or_404(Result, pk=curr_id)
    old = get_object_or_404(Result, pk=old_id)
    data = {'current': current, 'old': old}
    return render(request, 'compare-view.html', context=data)


def about_view(request):
    return render(request, 'about-view.html')


def dffs_to_test(request):
    dffs = FifoTest.objects.filter(active=True)
    out = []
    for dff in dffs:
        url = dff.file.url
        filename = os.path.basename(url)
        out.append({'shortname': dff.shortname, 'filename': filename,
                    'url': url})
    return JsonResponse(out, safe=False)


def existing_images(request):
    img = os.listdir(os.path.join(settings.MEDIA_ROOT, 'results'))
    hashes = [i[:-4] for i in img if i.endswith('.png')]
    return JsonResponse(hashes, safe=False)
