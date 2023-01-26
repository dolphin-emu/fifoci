# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    # Examples:
    url(r"^$", views.home, name="home"),
    url(r"^dff/$", views.dffs_to_test),
    url(r"^dff/(?P<name>[a-zA-Z0-9-]+)/$", views.dff_view, name="dff-view"),
    url(r"^version/(?P<hash>[0-9a-f]{40})/$", views.version_view, name="version-view"),
    url(
        r"^version/(?P<hash>[0-9a-f]{40})/json/$",
        views.version_view_json,
        name="version-view-json",
    ),
    url(r"^result/(?P<id>\d+)/$", views.result_view, name="result-view"),
    url(
        r"^compare/(?P<curr_id>\d+)-(?P<old_id>\d+)/$",
        views.compare_view,
        name="compare-view",
    ),
    url(r"^about/$", views.about_view, name="about-view"),
    url(r"^existing-images/$", views.existing_images),
    url(r"^admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
