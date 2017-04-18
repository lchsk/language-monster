from django.conf.urls import url

from article import views

urlpatterns = [
    url(
        r'^read/(?P<article_id>\d+)/(.*?)/?$',
        views.ArticleView.as_view(),
        name='article_view',
    ),
    url(
        r'^list/(?P<target_lang>\w+)/(?P<page>\d+)?/?$',
        views.ArticlesView.as_view(),
        name='articles_view',
    ),
]
