from django.conf.urls import url

from api.views.misc import Ping

from api.views.language import (
    Languages,
    LanguagesToLearn,
    StartLearningLanguage,
)

from api.views.data import (
    AvailableDatasets,
    GetWords,
    LocalGetWords,
    LocalGetToStudy,
)

from api.views.user import UserStats

from api.views.results import (
    SaveResults,
    LocalSaveResults,
)

from api.views.auth import (
    UserLogin,
    UserRegistration,
)

urlpatterns = [

    ####################################################
    #                                                  #
    #                        GET                       #
    #                                                  #
    ####################################################

    url(
        r'^languages/?$',
        Languages.as_view(),
        name='languages',
    ),
    url(
        r'^ping/?$',
        Ping.as_view(),
        name='ping',
    ),
    url(
        r'^languages/available/?$',
        LanguagesToLearn.as_view(),
        name='available_langs',
    ),
    url(
        r'^datasets/(?P<lang_pair>\w{2}_\w{2})/?$',
        AvailableDatasets.as_view(),
        name='datasets',
    ),
    url(
        r'^words/(?P<dataset_id>\d+)/?$',
        GetWords.as_view(),
        name='words',
    ),
    url(
        r'^local/words/(?P<dataset_id>\d+)/(?P<uri>.+)?/?$',
        LocalGetWords.as_view(),
        name='local_words',
    ),
    url(
        r'^local/to-study/(?P<language>\w{2})/?$',
        LocalGetToStudy.as_view(),
        name='to_study',
    ),
    url(
        r'^users/stats/?$',
        UserStats.as_view(),
        name='user_stats',
    ),

    ####################################################
    #                                                  #
    #                       POST                       #
    #                                                  #
    ####################################################

    url(
        r'^users/begin/?$',
        StartLearningLanguage.as_view(),
        name='learn_language',
    ),
    url(
        r'^users/results/?$',
        SaveResults.as_view(),
        name='results',
    ),
    url(
        r'^local/users/results/?$',
        LocalSaveResults.as_view(),
        name='local_results',
    ),
    url(
        r'^auth/login/?$',
        UserLogin.as_view(),
        name='login',
    ),
    url(
        r'^auth/register/?$',
        UserRegistration.as_view(),
        name='register',
    ),
]
