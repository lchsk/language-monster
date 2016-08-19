from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.conf import settings
from core.views import IndexView, InfoView
from django.conf.urls.static import static
import userprofile.views as userprofile

handler400 = 'core.views.handler400'
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'

# urlpatterns = patterns('',
urlpatterns = [

    # url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^info/([a-z_]*?)$', InfoView.as_view(), name='info'),
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^monster/', include('core.urls', namespace='core')),
    url(r'^languages/', include('vocabulary.urls', namespace='vocabulary')),

    # User Profile
    url(r'^profile/(.*?)$', userprofile.public_page, name='public_page'),
    # url(r'^profile/', include('userprofile.urls', namespace='profile')),

    # Management links
    # url(r'^status/?$', status, name='status'),
    url(r'^manage/', include('management.urls', namespace='management')),
    # url(r'^manage/?$', manage, name='manage'),
]
# )

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if 'rosetta' in settings.INSTALLED_APPS:
    # urlpatterns += patterns('',
    #     url(r'^rosetta/', include('rosetta.urls')),
    # )
    urlpatterns += [url(r'^rosetta/', include('rosetta.urls'))]

    # print urlpatterns
