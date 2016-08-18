from django.conf.urls import url
from core import views

urlpatterns = [
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'^settings/$', views.settings_page, name='settings'),
    url(r'^update-profile/$', views.update_profile, name='update_profile'),
    url(r'^update-password/$', views.update_password, name='update_password'),
    url(r'^update-email/$', views.update_email, name='update_email'),
    url(r'^update-games/$', views.update_profile_games, name='update_profile_games'),
    url(r'^recover-password/$', views.recover_password, name='recover_password'),
    url(r'^send-email/$', views.send_email, name='send_email'),
    url(r'^upload-image/$', views.upload_image, name='upload_image'),

    url(r'^change-language/([a-z_]+)$', views.change_language, name='change_language'),

    # email change confirmation
    url(r'^confirm-email/([a-f0-9]+)$', views.confirm_email, name='confirm_email'),

    # confirm registration
    url(r'^confirm-registration/([a-f0-9]+)$', views.confirm_registration, name='confirm_registration'),


    # new password generation
    url(r'^generate-password/([a-f0-9]+)$', views.generate_password, name='generate_password'),
    url(r'^confirm-new-password/([a-f0-9]+)$', views.confirm_new_password, name='confirm_new_password'),

    url(r'^page/([a-z-]+)$', views.static_page, name='static_page'),
]
