from django.conf.urls import url
import (
    views,
    views_get,
    views_post,
)

urlpatterns = [

    ####################################################
    #                                                  #
    #                        GET                       #
    #                                                  #
    ####################################################

    url(
        r'^languages/?$',
        views_get.Languages.as_view(),
        name='languages',
    ),
    url(
        r'^ping/?$',
        views_get.Ping.as_view(),
        name='ping',
    ),
    url(
        r'^languages/available/?$',
        views_get.LanguagesToLearn.as_view(),
        name='available_langs',
    ),
    url(
        r'^datasets/(?P<lang_pair>\w{2}_\w{2})/?$',
        views_get.AvailableDatasets.as_view(),
        name='datasets',
    ),
    url(
        r'^words/(?P<dataset_id>\d+)/?$',
        views_get.GetWords.as_view(),
        name='words',
    ),
    url(
        r'^local/words/(?P<dataset_id>\d+)/(?P<email>.+)/?$',
        views_get.LocalGetWords.as_view(),
        name='local_words',
    ),
    url(
        r'^users/stats/?$',
        views_get.UserStats.as_view(),
        name='user_stats',
    ),

    ####################################################
    #                                                  #
    #                       POST                       #
    #                                                  #
    ####################################################

    url(
        r'^users/begin/?$',
        views_post.StartLearningLanguage.as_view(),
        name='learn_language',
    ),
    url(
        r'^users/results/?$',
        views_post.SaveResults.as_view(),
        name='results',
    ),
    url(
        r'^local/users/results/?$',
        views_post.LocalSaveResults.as_view(),
        name='local_results',
    ),
    url(
        r'^auth/login/?$',
        views.UserLogin.as_view(),
        name='login',
    ),
    url(
        r'^auth/register/?$',
        views.UserRegistration.as_view(),
        name='register',
    ),
]
