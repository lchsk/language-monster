# -*- coding: utf-8 -*-

import logging
import datetime
import os.path
from uuid import uuid4

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.contrib.auth import (
    login,
    logout,
)
from django.conf import settings
from django.http import Http404

from django_countries import countries

from core.models import (
    MonsterUserGame,
    MonsterUser,
)
import core.impl.mail as mail

from utility.views import (
    ContextView,
    AuthContextView,
    NoTemplateMixin,
)
from utility.user_language import landing_language
from utility.security import validate_password
from utility.interface import (
    get_context,
    context,
    create_hash,
    redirect_unauth,
)
from vocabulary.impl.study import get_user_games
from core.impl.user import register as register_user
from core.impl.user import (
    authenticate_user,
    update_public_name,
    process_games_list,
)

logger = logging.getLogger(__name__)
settings.LOGGER(logger)

class DoRegister(ContextView):
    def post(self, request, *args, **kwargs):
        if request.POST['monster_username']:
            logger.critical("No username")
            return self.redirect('info', args=[''])

        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']
        base = landing_language(request)

        valid, error, error_str = register_user(
            email,
            password1,
            password2,
            settings.REGISTRATION_CONFIRMATION,
            base
        )

        if valid:
            try:
                if settings.SEND_EMAIL_AFTER_REGISTRATION:
                    mail.send_template_email(
                        request=request,
                        recipient=email,
                        template='welcome',
                        ctx={
                            'PUBLIC_NAME': email,
                        }
                    )

                if settings.LOGIN_AFTER_REGISTRATION:
                    user = authenticate_user(
                        email=email,
                        password=password1
                    )

                    if user and user.user.is_active:
                        user.user.backend = \
                            'django.contrib.auth.backends.ModelBackend'
                        login(request, user.user)
                        return self.redirect('index')
                else:
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        _('You are registered. Please login.')
                    )
            except Exception, e:
                logger.critical("Exception in registration")
                logger.critical(str(e))
                messages.add_message(
                    request,
                    messages.WARNING,
                    _(
                        'Sorry, sending confirmation email failed.'
                        ' Please try again later.'
                    )
                )
        else:
            logger.warning("Registration data invalid")
            messages.add_message(request, messages.WARNING, (error_str))

            return self.redirect('info', args=[''])

        return self.redirect('index')

class DoLogin(ContextView):
    def post(self, request, *args, **kwargs):
        identifier = request.POST['identifier']
        password = request.POST['password']

        monster_user = authenticate_user(
            email=identifier,
            password=password
        )

        if monster_user:
            if monster_user.user.is_active:
                monster_user.user.backend = \
                    'django.contrib.auth.backends.ModelBackend'
                login(request, monster_user.user)
                logger.debug('User %s successfully logged in', identifier)
                return self.redirect('index')
            else:
                logger.info('User %s is inactive, cant log in', identifier)
                messages.add_message(
                    request,
                    messages.WARNING,
                    _(
                        'This user is listed as inactive. Make sure you '
                        'confirmed your registration by clicking on a link '
                        'in an email you have received. In case of problems, '
                        'please contact us. Sorry for inconvenience.'
                    )
                )
                return self.redirect('info', args=[''])
        else:
            logger.info("Login data for %s are invalid", identifier)
            messages.add_message(
                request,
                messages.WARNING,
                _('You must provide correct email/username and password.')
            )
            return self.redirect('info', args=[''])

class DoLogout(AuthContextView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return self.redirect('index')

class IndexView(ContextView):
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        if self._context.is_authorised:
            self.template_name = 'app/dashboard.html'
        else:
            self.template_name = 'landing/base.html'

        return context

    def get(self, request, *args, **kwargs):
        resp = super(IndexView, self).get(request, *args, **kwargs)

        if self._context.is_authorised and not self._context.user.studying:
            return self.redirect('vocabulary:add_language')

        return resp

class DoSaveUserEmail(AuthContextView):
    def post(self, request, *args, **kwargs):
        self.get_context_data()

        new_email = request.POST['email'].lower()

        if not new_email:
            messages.add_message(
                request,
                messages.WARNING,
                _('You need to type in your new email address.')
            )

            return self.redirect('core:settings')

        already_exists = MonsterUser.objects.filter(
            user__email=new_email
        ).first()

        if already_exists:
            messages.add_message(
                request,
                messages.WARNING,
                _('Email already in use'),
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
            _(
                'Confirmation email was sent. Please check your '
                'inbox (or possibly spam box).'
            )
        )

        return self.redirect('core:settings')

class SpecialPageView(ContextView):
    template_name = 'landing/special_page.html'

    def get_context_data(self, **kwargs):
        context = super(SpecialPageView, self).get_context_data(**kwargs)

        page = self.kwargs.get('page', 'success')

        if page not in (
            'forgot_password',
            'generate_password',
            'success',
            'failure',
        ):
            raise Http404

        context['home'] = reverse('index')
        context['language'] = landing_language(self.request)
        context['page'] = page
        context['messages'] = messages.get_messages(self.request)

        return context

class DoRecoverPassword(ContextView):
    def post(self, request, *args, **kwargs):
        identifier = request.POST['identifier']

        if not identifier:
            logger.warning("Email is not correct: %s", identifier)
            messages.add_message(
                request,
                messages.WARNING, _('Email is not correct.')
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
                _('Email has not been found.')
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
                URL='http://' + host + url
            )
        )

        messages.add_message(
            request,
            messages.SUCCESS,
            _(
                'Email was sent. Please check your inbox '
                '(or possibly spam box).'
            )
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
                _('Email not found.')
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
                _('Your password was successfully changed. You can now login.')
            )

            return self.redirect('info', kwargs=dict(page='success'))
        else:
            messages.add_message(
                request,
                messages.WARNING,
                _('Values you have entered are incorrect.')
            )

            return self.redirect('info', kwargs=dict(page='failure'))

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
                _('Confirmation procedure failed. Please try again.')
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
            _('Your email address was verified successfully.')
        )

        return self.redirect('info', kwargs=dict(page='success'))

class DoSaveContactEmail(ContextView):
    """Contact Form

        Can be sent from authorised and unauthorised view.
    """

    def post(self, request, *args, **kwargs):
        self.get_context_data()

        if request.POST['username']:
            return self.redirect('info', args=[''])

        name = request.POST['name']
        email = request.POST['email']
        text = request.POST['text']
        text = text[:2048]

        if name and email and text:
            mail.send_template_email(
                request=self.request,
                recipient=settings.EMAIL_FROM,
                template='contact_form',
                ctx=dict(
                    NAME=name,
                    EMAIL=email,
                    TEXT=text
                )
            )

            logger.info(
                "Contact email sent from %s, %s, %s", name, email, text
            )

            messages.add_message(
                self.request,
                messages.SUCCESS,
                _(
                    'Thank you for contacting us. We will do our best '
                    'to respond shortly!'
                )
            )

            return self.redirect('index')
        else:
            logger.info(
                "Invalid values for contact email: %s, %s, %s",
                name, email, text
            )

            messages.add_message(
                request,
                messages.WARNING,
                _(
                    'Email was not sent. Please make sure that all fields '
                    ' have valid values.'
                )
            )

            return self.redirect('index')



class DoChangeInterfaceLanguage(NoTemplateMixin, ContextView):
    def get(self, request, *args, **kwargs):
        resp = super(DoChangeInterfaceLanguage, self).get(
            request,
            *args,
            **kwargs
        )

        if 'HTTP_REFERER' in request.META:
            url = request.META['HTTP_REFERER']
        else:
            url = reverse('index')

        if self._context.is_authorised:
            base_language = None

            for symbol, lang in self._context.base_languages.iteritems():
                if symbol == self.args[0]:
                    base_language = lang
                    break

            if base_language is None:
                return self.redirect_url(url)

            self._context.user.change_language(self.args[0])

            logger.info(
                "Changing language for %s (%s)",
                self._context.user,
                self.args[0]
            )

            return self.redirect_url(url)
        else:
            date1 = datetime.datetime.now()
            end_date = date1 + datetime.timedelta(days=30)

            response = HttpResponseRedirect(url)
            response.set_cookie(
                'monster_language',
                self.args[0],
                expires=end_date
            )
            logger.info(
                "Changing language (cookie)"
            )

            return response

class ErrorPage(ContextView):
    template_name = 'landing/error.html'
    error = None

    def get_context_data(self, **kwargs):
        context = super(ErrorPage, self).get_context_data(**kwargs)

        context['error'] = self.error
        context['home'] = reverse('index')

        if self._context.is_authorised:
            auth = self._context.user
        else:
            auth = '<unlogged>'

        logger.error(
                '{error} error encountered, '
            'method: {method}, path: {path}, path_info: {path_info}, '
            'auth: {auth}'.format(
                error=self.error,
                method=self.request.method,
                path=self.request.path,
                path_info=self.request.path_info,
                auth=auth,
            )
        )

        return context
