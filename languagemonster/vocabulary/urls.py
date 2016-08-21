from django.conf.urls import url
from vocabulary import views

urlpatterns = [
    url(
        r'^$',
        views.AddLanguageView.as_view(),
    ),
    url(
        r'^learn/?$',
        views.AddLanguageView.as_view(),
        name='add_language',
    ),
    url(
        r'^learn/(?P<slug>(\w+))/?$',
        views.DoSaveLanguage.as_view(),
        name='save_language',
    ),
    url(
        r'^study/(?P<slug>(\w+))/?$',
        views.StudyView.as_view(),
        name='study',
    ),

    # language slug, dataset slug (can contain -)
    url(r'^study/(\w+)/([\w-]+)/?$', views.play, name='play'),
    url(r'^error/?$', views.report_error, name='report_error'),
]
