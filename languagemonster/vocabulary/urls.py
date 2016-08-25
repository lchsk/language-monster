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

    url(
        r'^study/(?P<language_slug>(\w+))/(?P<dataset_slug>([\w-]+))/?$',
        views.PlayView.as_view(),
        name='play',
    ),
]
