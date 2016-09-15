from django.conf.urls import patterns, url
import views, views_get, views_post, views_put

urlpatterns = [

    # GET - general lang info
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

    # Get information about languages to learn
    url(
        r'^languages/available/?$',
        views_get.LanguagesToLearn.as_view(),
        name='available_langs',
    ),

    # Get available datasets for a given language pair

    url(
        r'^datasets/(?P<lang_pair>\w{2}_\w{2})/?$',
        views_get.AvailableDatasets.as_view(),
        name='datasets',
    ),

    # Get words from a dataset

    url(
        # r'^data/(?P<dataset_id>(.+))/(?P<email>(.+))/?$',
        r'^words/(?P<dataset_id>(\d+))/?$',
        # views_get.get_words,
        views_get.GetWords.as_view(),
        name='words',
    ),

    url(
        r'^users/stats/?$',
        views_get.UserStats.as_view(),
        name='user_stats',
    ),

    #################
    # POST
    #################

    # User starts learning a new language

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

    # Game Session

    #################
    # GET
    #################

    # Get information about languages

    # Get user's stats

    # Get new password

    # url(r'^users/(?P<email>(.+))/password/?$', views_get.password, name='password'),

    # GET Get information about available games

    # url(r'^games/?$', views_get.games, name='games'),

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

    # this is left off without a key:
    # potentially dangerous, but it is also called by JS games
    # TODO: figure out how to protect games and/or add key
    # It should (probably) be onlly accessed from JS games (check domain)
    # url(r'^get-game-data/(?P<dataset_id>.+)/(?P<email>.+)/?$', views.get_game_data, name="get_game_data"),
    # url(r'^users/results/js/?$', views_post.save_results_js, name='results_js'),
]
