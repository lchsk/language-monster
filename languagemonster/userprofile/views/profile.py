import logging
from uuid import uuid4

from django_countries import countries
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.core.urlresolvers import reverse

from core.models import MonsterUser

from core.impl import mail

from utility.views import (
    ContextView,
    AuthContextView,
)

from utility.security import validate_password

from core.impl.user import process_games_list

from core.views import SpecialPageView

from vocabulary.impl.study import get_user_games

logger = logging.getLogger(__name__)

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
            M=_('gender_male'),
            F=_('gender_female'),
            O=_('gender_other'),
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
            _('msg_profile_updated')
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
            _('msg_profile_updated')
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
                _("msg_profile_updated")
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
                _('msg_only_png_jpg')
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
                _('msg_file_too_large_0_5_mb')
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
                _('msg_file_uploaded')
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
                _('msg_unknown_error')
            )
            return self.redirect('core:settings')

class DoSaveUserEmail(AuthContextView):
    def post(self, request, *args, **kwargs):
        self.get_context_data()

        new_email = request.POST['email'].lower()

        if not new_email:
            messages.add_message(
                request,
                messages.WARNING,
                _('msg_type_new_email')
            )

            return self.redirect('core:settings')

        already_exists = MonsterUser.objects.filter(
            user__email=new_email
        ).first()

        if already_exists:
            messages.add_message(
                request,
                messages.WARNING,
                _('msg_email_already_in_use'),
            )

            return self.redirect('core:settings')

        secure_hash = self._context.user.change_email(new_email)

        host = request.get_host()
        url = reverse('core:confirm_email', args=[secure_hash])

        mail.send_template_email(
            request=request,
            recipient=new_email,
            template='email_change',
            ctx=dict(
                PUBLIC_NAME=self._context.user.public_name,
                URL='http://' + host + url,
            )
        )

        messages.add_message(
            request,
            messages.SUCCESS,
            _('msg_email_sent'),
        )

        return self.redirect('core:settings')

class DoConfirmNewEmail(AuthContextView):
    def get(self, request, *args, **kwargs):
        self.get_context_data()

        if self._context.user.secure_hash != kwargs['secret']:
            logger.warning(
                'Invalid secret hash when chaning email for %s',
                self._context.user
            )

            messages.add_message(
                request,
                messages.WARNING,
                _('msg_confirmation_failed')
            )
            return self.redirect('core:settings')

        self._context.user.save_new_email()

        logger.info(
            'User %s successfully confirmed email',
            self._context.user,
        )

        messages.add_message(
            request,
            messages.SUCCESS,
            _('msg_email_verified')
        )

        return self.redirect('info', kwargs=dict(page='success'))

class DoRecoverPassword(ContextView):
    def post(self, request, *args, **kwargs):
        identifier = request.POST['identifier']

        if not identifier:
            logger.warning("Email is not correct: %s", identifier)

            messages.add_message(
                request,
                messages.WARNING, _('msg_invalid_email')
            )
            return self.redirect('info', args=[''])

        monster_user = MonsterUser.objects.filter(
            user__email=identifier
        ).first()

        if not monster_user:
            logger.warning("Email has not been found: %s", identifier)

            messages.add_message(
                request,
                messages.WARNING,
                _('msg_email_not_found')
            )
            return self.redirect('info', args=[''])

        secure_hash = uuid4().hex
        monster_user.secure_hash = secure_hash
        monster_user.save()

        host = request.get_host()
        url = reverse('core:generate_password', args=[secure_hash])

        mail.send_template_email(
            request=request,
            recipient=monster_user.user.email,
            template='password_recovery',
            ctx=dict(
                PUBLIC_NAME=monster_user.public_name,
                URL='http://' + host + url,
            )
        )

        messages.add_message(
            request,
            messages.SUCCESS,
            _('msg_email_sent'),
        )

        logger.info("Email sent for password recovery: %s", identifier)

        return self.redirect('info', kwargs=dict(page='success'))

class PickNewPasswordView(SpecialPageView):
    def get_context_data(self, **kwargs):
        context = super(PickNewPasswordView, self).get_context_data(**kwargs)

        context['page'] = 'generate_password'
        context['secret'] = kwargs['secret']

        return context

class DoConfirmNewPassword(ContextView):
    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        monster_user = MonsterUser.objects.filter(
            secure_hash=kwargs['secret'],
            user__email=email
        )

        if len(monster_user) != 1:
            logger.warning('User not found %s', email)

            messages.add_message(
                request,
                messages.WARNING,
                _('msg_email_not_found'),
            )

            raise Http404

        monster_user = monster_user.first()

        valid = validate_password(request, password1, password2, messages)

        if valid:
            monster_user.secure_hash = None
            monster_user.save()

            monster_user.user.set_password(password1)
            monster_user.user.save()

            logger.info("Password confirmed: %s", monster_user)

            messages.add_message(
                request,
                messages.SUCCESS,
                _('msg_password_changed'),
            )

            return self.redirect('info', kwargs=dict(page='success'))
        else:
            messages.add_message(
                request,
                messages.WARNING,
                _('msg_invalid_values'),
            )

            return self.redirect('info', kwargs=dict(page='failure'))
