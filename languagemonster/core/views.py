# -*- coding: utf-8 -*-

import logging
import datetime

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.contrib.auth import (
    login,
    logout,
)
from django.conf import settings
from django.http import Http404

import core.impl.mail as mail
from core.impl.user import (
    register as register_user,
    authenticate_user,
    get_games,
)

from utility.views import (
    ContextView,
    AuthContextView,
    NoTemplateMixin,
)
from utility.user_language import landing_language

from vocabulary.impl.study import (
    get_datasets,
    get_game_translations,
)

logger = logging.getLogger(__name__)

class DoRegister(ContextView):
    def post(self, request, *args, **kwargs):
        if request.POST['monster_username']:
            logger.warning("Received: %s", request.POST['monster_username'])

            return self.redirect('info', args=['']) # will raise 404

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
                        _('msg_user_registered')
                    )
            except Exception, e:
                logger.critical("Exception in registration")
                logger.critical(str(e))

                messages.add_message(
                    request,
                    messages.WARNING,
                    _('msg_email_failed'),
                )
        else:
            logger.warning("Registration data invalid: %s", error_str)

            messages.add_message(request, messages.WARNING, error_str)

            return self.redirect('info', args=['failure'])

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
                    _('msg_user_inactive'),
                )
                return self.redirect('info', args=['failure'])
        else:
            logger.info("Login data for %s are invalid", identifier)

            messages.add_message(
                request,
                messages.WARNING,
                _('msg_invalid_email_password'),
            )
            return self.redirect('info', args=['failure'])

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

            context['games'] = get_games().keys()
            context['xl'] = get_game_translations()

        return context

    def get(self, request, *args, **kwargs):
        resp = super(IndexView, self).get(request, *args, **kwargs)

        if self._context.is_authorised and not self._context.user.studying:
            return self.redirect('vocabulary:add_language')

        return resp


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

class DoSaveContactEmail(ContextView):
    """Contact Form

        Can be sent from authorised and unauthorised view.
    """

    def post(self, request, *args, **kwargs):
        self.get_context_data()

        if request.POST['username']:
            logger.warning('Suspicious argument: %s', request.POST['username'])

            return self.redirect('info', args=['']) # will raise 404

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
                _('msg_contact_recv'),
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
                _('msg_email_failed'),
            )

            return self.redirect('index')

class DoChangeInterfaceLanguage(NoTemplateMixin, ContextView):
    def get(self, request, *args, **kwargs):
        resp = super(DoChangeInterfaceLanguage, self).get(
            request,
            *args,
            **kwargs
        )

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
