from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.conf import settings
from core.views import (
    IndexView,
    InfoView,
    ErrorPage,
)
from django.conf.urls.static import static
import userprofile.views as userprofile

handler400 = ErrorPage.as_view(error=400)
handler404 = ErrorPage.as_view(error=404)
handler500 = ErrorPage.as_view(error=500)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^info/([a-z_]*?)$', InfoView.as_view(), name='info'),
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^monster/', include('core.urls', namespace='core')),
    url(r'^languages/', include('vocabulary.urls', namespace='vocabulary')),

    url(r'^profile/(.*?)$', userprofile.public_page, name='public_page'),
    url(r'^manage/', include('management.urls', namespace='management')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        url(r'^400/?$', ErrorPage.as_view(error=400)),
        url(r'^404/?$', ErrorPage.as_view(error=404)),
        url(r'^500/?$', ErrorPage.as_view(error=500)),
    ]

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [url(r'^rosetta/', include('rosetta.urls'))]
