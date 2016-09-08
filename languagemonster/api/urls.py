from django.conf.urls import patterns, url
import views, views_get, views_post, views_admin, views_put

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

    #################
    # POST
    #################

    # Register new device

    url(r'^devices/?$', views_admin.devices, name='devices'),

    # User starts learning a new language

    url(r'^users/begin/?$', views_post.add_language, name='learn_language'),

    url(r'^users/results/?$', views_post.save_results, name='results'),

    # Game Session

    url(r'^users/results/js/?$', views_post.save_results_js, name='results_js'),

    #################
    # GET
    #################

    # Get information about languages




    # Get user's stats

    url(r'^users/(?P<email>(.+))/stats/?$', views_get.user_stats, name='user_stats'),

    # Get new password

    url(r'^users/(?P<email>(.+))/password/?$', views_get.password, name='password'),

    # GET Get information about available games

    url(r'^games/?$', views_get.games, name='games'),

    # Get available datasets for a given language pair

    url(r'^data/(?P<base>(.{2}))/(?P<target>(.{2}))/?$', views_get.get_datasets, name='datasets'),

    # Get words from a dataset

    url(r'^data/(?P<dataset_id>(.+))/(?P<email>(.+))/?$', views_get.get_words, name='data'),

    # Ping




    #################
    # PUT
    #################

    # PUT Set games the user does not want to play

    url(r'^users/games/?$', views_put.set_banned_games, name='banned_games'),

    # Change user's language

    url(r'^users/language/?$', views_put.set_language, name='user_language'),

    # Change user's email

    url(r'^users/email/?$', views_put.change_user_email, name='user_email'),

    # url(r'^games/?$', views.ga),

    # POST - registration
    # PUT - login

    url(r'^auth/login/?$', views.UserLogin.as_view(), name='users'),
    # url(r'^register/(?P<key>(.+))/?$', views.user_register),



    # --------------------------------------------------------------

    # User related

    # GET


    url(r'^language/(?P<key>(.+))/(?P<acronym>([a-z]{2}))/?$', views_get.language),

    # this is left off without a key:
    # potentially dangerous, but it is also called by JS games
    # TODO: figure out how to protect games and/or add key
    # It should (probably) be onlly accessed from JS games (check domain)
    url(r'^get-game-data/(?P<dataset_id>.+)/(?P<email>.+)/?$', views.get_game_data, name="get_game_data"),

    # POST

    #TODO: TEST

    # Study related
    # url(r'^dataset/(?P<base>[a-z]+)/(?P<target>[a-z]+)/(?P<dataset>[a-z]+)/?$', views.get_dataset, name='get_dataset'),

    #################
    # Update user data (PUT) or return user (GET)
    # MUST STAY AT THE BOTTOM - #FIXME: fix regexp
    #################

    url(r'^users/(?P<email>(.+))/?$', views.get_or_update_user, name='get_or_update_user'),
]
