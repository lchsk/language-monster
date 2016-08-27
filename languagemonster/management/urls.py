from django.conf.urls import patterns, url
import views
import management.impl.simple_dataset as simple_dataset
import management.impl.views_clean as views_clean
import management.impl.action_clean as action_clean

urlpatterns = [
    url(
        r'^$',
        views.IndexView.as_view(),
        name='index',
    ),
    url(
        r'^status/$',
        views.StatusView.as_view(),
        name='status',
    ),
    url(r'^sets/$', views.sets, name='sets'),
    url(r'^add_set/(.*)$', views.add_set, name='add_set'),
    url(r'^save_set_meta/(.*)$', views.save_set_meta, name='save_set_meta'),
    url(r'^save_diff/(.*)$', views.save_diff, name='save_diff'),

    url(r'^duplicates/(.*)$', views.duplicates, name='duplicates'),

    url(r'^set_list/$', views.set_list, name='set_list'),
    url(r'^edit_set/(.*)$', views.edit_set, name='edit_set'),
    url(r'^import_diff/(.*)$', views.import_diff, name='import_diff'),
    url(r'^view_import_set/?$', views.view_import_set, name='view_import_set'),
    url(r'^do_import_set/?$', views.do_import_set, name='do_import_set'),

    # url(r'^export_words/(.*)$', views.export_words, name='export_words'),
    url(r'^save_edit_form/(.*)$', views.save_edit_form, name='save_edit_form'),
    url(r'^clean/$', views.clean, name='clean'),

    url(r'^copy_and_reverse/(.*)$', views.copy_and_reverse, name='copy_and_reverse'),

    # Simple data set management
    url(r'^view_simple_dataset/(.*)$', simple_dataset.view_simple_dataset, name='view_simple_dataset'),
    url(r'^update_simple_dataset/(.*)?$', simple_dataset.update_simple_dataset, name='update_simple_dataset'),
    url(r'^view_simple_datasets/$', simple_dataset.view_simple_datasets, name='view_simple_datasets'),
    url(r'^simple_dataset_from/(.*)$', simple_dataset.simple_dataset_from, name='simple_dataset_from'),
    url(r'^generate_simple_dataset/(.*)$', simple_dataset.generate_simple_dataset, name='generate_simple_dataset'),
    url(r'^view_copy_words_from/(.*)$', simple_dataset.view_copy_words_from, name='view_copy_words_from'),
    url(r'^view_copy_words_to/(.*)$', simple_dataset.view_copy_words_to, name='view_copy_words_to'),
    url(r'^do_copy_words/(.*)$', simple_dataset.do_copy_words, name='do_copy_words'),

    # Cleaning tasks
    url(
        r'^view_dangling_word_pairs/?$',
        views_clean.view_dangling_word_pairs,
        name='view_dangling_word_pairs'
    ),
    url(
        r'^remove_dangling_words/?$',
        action_clean.remove_dangling_words,
        name='remove_dangling_words'
    ),
]
