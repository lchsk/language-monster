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
    url(
        r'^add-new-set-from-file/$',
        views.AddNewSetFromFileView.as_view(),
        name='add_new_set_from_file',
    ),
    url(
        r'^add_set/(?P<path>[\w\/\.\-_]+)$',
        views.AddNewSetView.as_view(),
        name='add_set',
    ),
    url(
        r'^sets/$',
        views.SetsView.as_view(),
        name='sets',
    ),
    url(
        r'^edit-set/(?P<dataset_id>\d+)$',
        views.EditSetView.as_view(),
        name='edit_set',
    ),
    url(
        r'^set-action/(?P<dataset_id>\d+)$',
        views.SetActionDispatch.as_view(),
        name='save_edit_form',
    ),

    url(
        r'^view_import_set/?$',
        views.ImportSetView.as_view(),
        name='view_import_set',
    ),
    url(
        r'^do_import_set/?$',
        views.DoImportSet.as_view(),
        name='do_import_set',
    ),

    url(r'^save_set_meta/(.*)$', views.save_set_meta, name='save_set_meta'),
    url(r'^save_diff/(.*)$', views.save_diff, name='save_diff'),

    url(r'^duplicates/(.*)$', views.duplicates, name='duplicates'),

    url(r'^import_diff/(.*)$', views.import_diff, name='import_diff'),

    # url(r'^export_words/(.*)$', views.export_words, name='export_words'),

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
