from django.conf.urls import url

import views

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
        r'^add-set/(?P<path>[\w\/\.\-_]+)$',
        views.AddNewSetView.as_view(),
        name='add_set',
    ),
    url(
        r'^save-set-meta/(?P<path>[\w\/\.\-_]+)$',
        views.DoSaveNewSet.as_view(),
        name='save_set_meta',
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
        r'^remove-dataset/(?P<dataset_id>\d+)$',
        views.DoRemoveDataset.as_view(),
        name='remove_dataset',
    ),
    url(
        r'^set-action/(?P<dataset_id>\d+)$',
        views.SetActionDispatch.as_view(),
        name='save_edit_form',
    ),

    url(
        r'^view-import-set/?$',
        views.ImportSetView.as_view(),
        name='view_import_set',
    ),
    url(
        r'^do-import-set/?$',
        views.DoImportSet.as_view(),
        name='do_import_set',
    ),
    url(
        r'^do-export-all-sets/?$',
        views.DoExportAllSets.as_view(),
        name='do_export_all_sets',
    ),
    url(r'^save-diff/(.*)$', views.save_diff, name='save_diff'),

    url(
        r'^duplicates/(?P<dataset_id>\d+)$',
        views.DuplicatesView.as_view(),
        name='duplicates',
    ),

    url(r'^import-diff/(.*)$', views.import_diff, name='import_diff'),

    # url(r'^export_words/(.*)$', views.export_words, name='export_words'),

    url(
        r'^copy-and-reverse/(?P<dataset_id>\d+)$',
        views.DoCopyAndReverse.as_view(),
        name='copy_and_reverse',
    ),

    # Simple data set management

    url(
        r'^view-simple-datasets/$',
        views.SimpleDatasetsView.as_view(),
        name='view_simple_datasets',
    ),

    url(
        r'^view-simple-dataset/(?P<id>\d*)$',
        views.SingleSimpleDatasetView.as_view(),
        name='view_simple_dataset',
    ),
    url(
        r'^update-simple-dataset/(?P<id>\d+)?$',
        views.DoSaveSimpleDataset.as_view(),
        name='update_simple_dataset',
    ),

    url(
        r'^simple-dataset-from/(?P<id>\d+)$',
        views.SimpleDatasetFromView.as_view(),
        name='simple_dataset_from',
    ),
    url(
        r'^generate-simple-dataset/(?P<id>\d+)$',
        views.DoSaveAutoGeneratedSimpleDataset.as_view(),
        name='generate_simple_dataset',
    ),

    # Cleaning tasks
    url(
        r'^view-dangling-word-pairs/?$',
        views.DanglingWordPairsView.as_view(),
        name='view_dangling_word_pairs',
    ),
    url(
        r'^remove-dangling-words/?$',
        views.DoRemoveDanglingWords.as_view(),
        name='remove_dangling_words',
    ),

    # Words copying
    url(
        r'^view-copy-words-from/(?P<dataset_id>\d+)$',
        views.CopyWordsFromView.as_view(),
        name='view_copy_words_from',
    ),
    url(
        r'^view-copy-words-to/(?P<dataset_id>\d+)$',
        views.CopyWordsToView.as_view(),
        name='view_copy_words_to',
    ),
    url(
        r'^do-copy-words/(?P<dataset_id>\d+)$',
        views.DoCopyWords.as_view(),
        name='do_copy_words',
    ),
]
