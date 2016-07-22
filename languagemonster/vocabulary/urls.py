from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.add_language),
    url(r'^learn/?$', views.add_language, name='add_language'),
    url(r'^learn/(\w+)/?$', views.save_language, name='save_language'),
    url(r'^study/(\w+)/?$', views.study, name='study'),

    # language slug, dataset slug (can contain -)
    url(r'^study/(\w+)/([\w-]+)/?$', views.play, name='play'),
    url(r'^error/?$', views.report_error, name='report_error'),
]
