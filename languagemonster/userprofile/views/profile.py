import logging

from django_countries import countries
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from utility.views import (
    AuthContextView,
    NoTemplateMixin,
)

from utility.security import validate_password

from core.impl.user import (
    authenticate_user,
    update_public_name,
    process_games_list,
)

from vocabulary.impl.study import get_user_games

logger = logging.getLogger(__name__)
settings.LOGGER(logger)

class SettingsView(AuthContextView):
    template_name = 'app/profile.html'

    def get_context_data(self, **kwargs):
        context = super(SettingsView, self).get_context_data(**kwargs)

        context['countries'] = countries
        context['games'] = process_games_list(
            settings.GAMES,
            get_user_games(self._context.user.raw)
        )
        context['gender'] = dict(
            M=_('male'),
            F=_('female'),
            O=_('other'),
        )

        return context

class DoSaveProfile(AuthContextView):
    def post(self, request, *args, **kwargs):
        self.get_context_data()

        d = self.request.POST.dict()

        self._context.user.update(
            first_name=d['first_name'],
            last_name=d['last_name'],
            gender=d['gender'],
            country=d['country'],
            www=d['www'],
            location=d['location'],
            about=d['about'],
            uri=None,
        )

        logger.debug("Settings updated for %s", self._context.user)

        messages.add_message(
            self.request,
            messages.SUCCESS,
            _('Your profile was successfully updated')
        )

        return self.redirect('core:settings')

class DoSaveUserGames(AuthContextView):
    def post(self, request, *args, **kwargs):
        self.get_context_data()

        games = settings.GAMES
        res = {}

        for k, v in games.iteritems():
            res[k] = {}
            res[k]['available'] = False

            if k in request.POST and request.POST[k]:
                res[k]['available'] = True

        self._context.user.update_games(res)

        logger.info(
            "Games settings were updated for %s",
            self._context.user
        )

        messages.add_message(
            request,
            messages.SUCCESS,
            _('Your profile was successfully updated')
        )

        return self.redirect('core:settings')

class DoSaveUserPassword(AuthContextView):
    def post(self, request, *args, **kwargs):
        self.get_context_data()

        password1 = request.POST['password1']
        password2 = request.POST['password2']

        valid = validate_password(request, password1, password2, messages)

        if valid:
            self._context.user.change_password(password1)

            logger.info("Password changed for %s", self._context.user)

            messages.add_message(
                request,
                messages.SUCCESS,
                _("Your password was successfully changed.")
            )

        return self.redirect('core:settings')

class DoSaveAvatar(AuthContextView):
    def post(self, request, *args, **kwargs):
        self.get_context_data()

        f = request.FILES['file']
        content_type = f.content_type.split('/')[1]

        if content_type not in ('png', 'jpeg', 'jpg'):
            logger.warning(
                "%s tried to upload wrong file format: %s",
                self._context.user,
                content_type,
            )
            messages.add_message(
                request,
                messages.WARNING,
                _('Only png and jpg files are accepted, sorry.')
            )

            return self.redirect('core:settings')

        if f._size > 500000:
            logger.warning(
                "%s tried to upload file to big: %s",
                self._context.user,
                f._size,
            )
            messages.add_message(
                request,
                messages.WARNING,
                _('File is too large. Maximum size is 0.5 MB.')
            )

            return self.redirect('core:settings')

        if f:
            self._context.user.save_avatar(f, content_type)

            logger.info(
                "File %s uploaded for %s",
                self._context.user.avatar,
                self._context.user,
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                _('File was successfully uploaded.')
            )

            return self.redirect('core:settings')
        else:
            logger.warning(
                "Error when uploading a file for %s",
                self._context.user
            )
            messages.add_message(
                request,
                messages.WARNING,
                _('Unknown error when uploading a file. Please try again later.')
            )
            return self.redirect('core:settings')
