from django.conf.urls import url
from core import views

from userprofile.views import (
    social,
    profile,
)

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
        r'^send-email/$',
        views.DoSaveContactEmail.as_view(),
        name='send_email',
    ),
    url(
        r'^change-language/([a-z_]+)$',
        views.DoChangeInterfaceLanguage.as_view(),
        name='change_language',
    ),

    ############################################
    #                                          #
    #                User Profile              #
    #                                          #
    ############################################

    url(
        r'^settings/$',
        profile.SettingsView.as_view(),
        name='settings',
    ),
    url(
        r'^update-profile/$',
        profile.DoSaveProfile.as_view(),
        name='update_profile',
    ),
    url(
        r'^update-password/$',
        profile.DoSaveUserPassword.as_view(),
        name='update_password',
    ),
    url(
        r'^update-email/$',
        profile.DoSaveUserEmail.as_view(),
        name='update_email',
    ),
    url(
        r'^update-games/$',
        profile.DoSaveUserGames.as_view(),
        name='update_profile_games',
    ),
    url(
        r'^recover-password/$',
        profile.DoRecoverPassword.as_view(),
        name='recover_password',
    ),
    url(
        r'^generate-password/(?P<secret>[a-f0-9]+)/?$',
        profile.PickNewPasswordView.as_view(),
        name='generate_password',
    ),
    url(
        r'^confirm-email/(?P<secret>[a-f0-9]+)/?$',
        profile.DoConfirmNewEmail.as_view(),
        name='confirm_email',
    ),
    url(
        r'^confirm-new-password/(?P<secret>[a-f0-9]+)/?$',
        profile.DoConfirmNewPassword.as_view(),
        name='confirm_new_password',
    ),
    url(
        r'^upload-image/$',
        profile.DoSaveAvatar.as_view(),
        name='upload_image',
    ),
]
