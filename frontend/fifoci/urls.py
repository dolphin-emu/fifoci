from django.conf import settings
from django.conf.urls import patterns, include, static, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'fifoci.views.home', name='home'),
    url(r'^dff/$', 'fifoci.views.dffs_to_test'),
    url(r'^dff/(?P<name>[a-zA-Z0-9-]+)/$', 'fifoci.views.dff_view',
        name='dff-view'),
    url(r'version/(?P<hash>[0-9a-f]{40})/$', 'fifoci.views.version_view',
        name='version-view'),
    url(r'result/(?P<id>\d+)/$', 'fifoci.views.result_view',
        name='result-view'),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL,
                                 document_root=settings.MEDIA_ROOT)
