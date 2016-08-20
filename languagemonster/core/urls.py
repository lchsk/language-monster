from django.conf.urls import url
from core import views

urlpatterns = [
    url(
        r'^register/$',
        views.DoRegister.as_view(),
        name='register',
    ),
    url(
        r'^login/$',
        views.DoLogin.as_view(),
        name='login',
    ),
    url(
        r'^logout/$',
        views.DoLogout.as_view(),
        name='logout',
    ),
    url(
        r'^settings/$',
        views.SettingsView.as_view(),
        name='settings',
    ),
    url(
        r'^update-profile/$',
        views.DoSaveProfile.as_view(),
        name='update_profile',
    ),
    url(
        r'^update-password/$',
        views.DoSaveUserPassword.as_view(),
        name='update_password',
    ),
    url(
        r'^update-email/$',
        views.DoSaveUserEmail.as_view(),
        name='update_email',
    ),
    url(
        r'^update-games/$',
        views.DoSaveUserGames.as_view(),
        name='update_profile_games',
    ),
    url(
        r'^recover-password/$',
        views.DoRecoverPassword.as_view(),
        name='recover_password',
    ),
    url(
        r'^send-email/$',
        # views.DoSaveContactEmail.as_view(),
        views.send_email,
        name='send_email',
    ),
    url(
        r'^upload-image/$',
        views.DoSaveAvatar.as_view(),
        name='upload_image',
    ),
    url(
        r'^change-language/([a-z_]+)$',
        views.DoChangeInterfaceLanguage.as_view(),
        name='change_language',
    ),

    # email change confirmation
    url(
        r'^confirm-email/([a-f0-9]+)$',
        views.confirm_email,
        name='confirm_email',
    ),
    # new password generation
    url(
        r'^generate-password/([a-f0-9]+)$',
        views.generate_password,
        name='generate_password',
    ),
    url(
        r'^confirm-new-password/([a-f0-9]+)$',
        views.confirm_new_password,
        name='confirm_new_password',
    ),

    url(
        r'^page/([a-z-]+)$',
        views.static_page,
        name='static_page',
    ),
]
