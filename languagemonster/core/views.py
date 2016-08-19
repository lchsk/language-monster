# -*- coding: utf-8 -*-

import logging
import datetime
import os.path

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

from django_countries import countries

from core.models import (
    MonsterUserGame,
    MonsterUser,
)
import core.impl.mail as mail

from utility.views import (
    ContextView,
    AuthContextView,
)
from utility.user_language import landing_language
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

        if len(self._context.user.studying) == 0:
            return self.redirect('vocabulary:add_language')

        return resp

class SettingsView(AuthContextView):
    template_name = 'app/profile.html'

    def get_context_data(self, **kwargs):
        context = super(SettingsView, self).get_context_data(**kwargs)

        context['countries'] = countries
        context['games'] = process_games_list(
            settings.GAMES,
            get_user_games(self._context.user.raw)
        )
        context['gender'] = {
            'M' : _('male'),
            'F' : _('female'),
            'O' : _('other'),
        }

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
            uri=d['uri'],
        )

        self._context.user.save()

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

class DoSaveUserEmail(AuthContextView):
    def post(self, request, *args, **kwargs):
        self.get_context_data()

        new_email = request.POST['email']

        if new_email:
            secure_hash = self._context.user.change_email(new_email)

            try:
                host = request.get_host()
                url = reverse('core:confirm_email', args=[secure_hash])

                mail.send_template_email(
                    request=request,
                    recipient=new_email,
                    template='email_change',
                    ctx={
                        'PUBLIC_NAME': self._context.user.public_name,
                        'URL': 'http://' + host + url
                    }
                )

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    _('Confirmation email was sent. Please check your inbox (or possibly spam box).')
                )
            except Exception, e:
                logger.critical(
                    "Error when changing email for %s",
                    self._context.user
                )
                logger.critical(str(e))
                messages.add_message(
                    request,
                    messages.WARNING,
                    _('Sorry, sending confirmation email failed. Please try again later.')
                )
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    _('You need to type in your new email address.')
                )


        return self.redirect('core:settings')

@context
@redirect_unauth
def confirm_email(request, p_secure_hash, ctx):

    if ctx['user'].secure_hash != p_secure_hash:
        logger.warning(
            "User %s probably does not exist",
            str(ctx['user'])
        )
        messages.add_message(
            request,
            messages.WARNING,
            _('Confirmation procedure failed. Please try again.')
        )
        return HttpResponseRedirect(reverse('core:settings'))

    ctx['user'].user.email = ctx['user'].new_email
    ctx['user'].user.save()
    update_public_name(ctx['user'])

    ctx['user'].secure_hash = ''
    ctx['user'].new_email = ''
    ctx['user'].save()

    logger.info("User %s successfully confirmed email", str(ctx['user']))
    messages.add_message(
        request,
        messages.SUCCESS,
        _('Your email address was verified successfully.')
    )
    return HttpResponseRedirect(reverse('core:settings'))


def validate_password(request, password1, password2, messages):
    # TODO: send context as argument
    # c = get_context(request)
    valid = True

    if len(password1) < 8:
        messages.add_message(
            request,
            messages.WARNING,
            _("New password must be at least 8 characters long.")
        )
        valid = False

    if password1 != password2:
        messages.add_message(
            request,
            messages.WARNING,
            _("Passwords don't match.")
        )
        valid = False

    return valid

class InfoView(ContextView):
    template_name = 'landing/base.html'

    def get_context_data(self, **kwargs):
        context = super(InfoView, self).get_context_data(**kwargs)

        context['language'] = landing_language(self.request)
        context['page'] = 'info'
        context['param'] =  kwargs.get('param')
        context['additional'] = kwargs.get('additional')
        context['messages'] = messages.get_messages(self.request)

        return context

# def info(request, param=None, additional={}):
#     ''' View for unlogged user only '''

#     ctx = get_context(request)
#     ctx['language'] = landing_language(request)
#     ctx['page'] = 'info'
#     ctx['param'] =  param
#     ctx['additional'] = additional
#     ctx['messages'] = messages.get_messages(request)

#     return render(request, 'landing/base.html', ctx)


def recover_password(request):
    """Unauthorized only"""

    identifier = request.POST['identifier']

    if not identifier:
        logger.warning("Email is not correct: %s", str(identifier))
        messages.add_message(
            request,
            messages.WARNING, _('Email is not correct.')
        )
        return HttpResponseRedirect(reverse('info', args=['']))

    u = MonsterUser.objects.filter(
        user__email=identifier
    ).first()

    if not u:
        logger.warning("Email has not been found: %s", str(u))
        messages.add_message(
            request,
            messages.WARNING,
            _('Email has not been found.')
        )
        return HttpResponseRedirect(reverse('info', args=['']))

    secure_hash = create_hash(u)
    u.secure_hash = secure_hash
    u.save()

    try:
        host = request.get_host()
        url = reverse('core:generate_password', args=[secure_hash])

        mail.send_template_email(
            request=request,
            recipient=u.user.email,
            template='password_recovery',
            ctx={
                'PUBLIC_NAME': u.public_name,
                'URL': 'http://' + host + url
            }
        )

        messages.add_message(
            request,
            messages.SUCCESS,
            _('Email was sent. Please check your inbox (or possibly spam box).')
        )
        logger.info("Email sent for password recovery: %s", str(u))
    except Exception, e:
        logger.critical("Error when sending email for password recovery")
        logger.critical(str(e))
        messages.add_message(
            request,
            messages.WARNING,
            _('Sorry, sending confirmation email failed. Please try again later.')
        )

    return HttpResponseRedirect(reverse('info', args=['']))


def generate_password(request, p_secure_hash):
    """TODO: check what is that"""

    user = MonsterUser.objects.filter(secure_hash=p_secure_hash).first()

    if not user:
        logger.warning("Reloaded page during password generation")
        messages.add_message(
            request,
            messages.WARNING,
            _('Reloading page during password change is forbidden for security reasons. In order to change your password you have to start again, sorry.')
        )
        return HttpResponseRedirect(reverse('info', args=['']))

    secure_hash = create_hash(user)
    user.secure_hash = secure_hash
    user.save()

    return info(request, 'generate_password', {'secure_hash': secure_hash})


def confirm_new_password(request, p_secure_hash):

    email = request.POST['email']
    password1 = request.POST['password1']
    password2 = request.POST['password2']

    user = MonsterUser.objects.filter(
        secure_hash=p_secure_hash,
        user__email=email
    ).first()

    if not user:
        logger.warning("Invalid email: %s", str(user))
        messages.add_message(
            request,
            messages.WARNING,
            _('Email you have entered is either incorrect or you have reloaded the webpage. Reloading page during password change is forbidden for security reasons. In order to change your password you have to start again, sorry.')
        )
        return HttpResponseRedirect(reverse('info', args=['']))

    user.secure_hash = ''
    user.save()

    valid = validate_password(request, password1, password2, messages)

    if valid:
        user.user.set_password(password1)
        user.user.save()
        logger.info("Password confirmed: %s", str(user))
        messages.add_message(
            request,
            messages.SUCCESS,
            _("Your password was successfully changed. You can now login.")
        )

    return HttpResponseRedirect(reverse('info', args=['']))


def send_email(request):
    ''' This sends email (eg. from contact form on the landing page)'''

    # Antispam

    if request.POST['username']:
        return HttpResponseRedirect(reverse('info', args=['']))

    name = request.POST['name']
    email = request.POST['email']
    text = request.POST['text']

    if name and email and text and len(name) > 1 and len(text) > 1:

        mail.send_template_email(
            request=request,
            recipient=settings.EMAIL_FROM,
            template='contact_form',
            ctx={
                'NAME': name,
                'EMAIL': email,
                'TEXT': text
            }
        )

        logger.info(
            "Contact email sent from %s, %s, %s",
            str(name),
            str(email),
            str(text)
        )
        messages.add_message(
            request,
            messages.SUCCESS,
            _('Thank you for contacting us. We will do our best to respond shortly!')
        )
        return HttpResponseRedirect(reverse('index'))

    else:
        logger.info(
            "Invalid values for contact email: %s, %s, %s",
            str(name),
            str(email),
            str(text)
        )
        messages.add_message(
            request,
            messages.WARNING,
            _('Email was not sent. Please make sure that all fields have valid values.')
        )
        return HttpResponseRedirect(reverse('index'))

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

def change_language(request, p_base_language):
    ctx = get_context(request)

    if 'HTTP_REFERER' in request.META:
        url = request.META['HTTP_REFERER']
    else:
        url = reverse('index')

    if ctx['user']:
        base_language = None

        for symbol, lang in ctx['basic']['base_languages'].iteritems():
            if symbol == p_base_language:
                base_language = lang
                break

        if base_language is None:
            return HttpResponseRedirect(url)

        ctx['user'].language = p_base_language
        logger.info(
            "Changing language for %s (%s)",
            str(ctx['user']),
            str(p_base_language)
        )
        ctx['user'].save()
    else:
        date1 = datetime.datetime.now()
        end_date = date1 + datetime.timedelta(days=30)

        response = HttpResponseRedirect(url)
        response.set_cookie(
            'monster_language',
            p_base_language,
            expires=end_date
        )
        logger.info(
            "Chaning language (cookie)"
        )

        return response

    return HttpResponseRedirect(url)

def error_page(request, error_code):
    ctx = get_context(request)

    if ctx['user']:
        path = 'app/error_page.html'
        ctx['error_code'] = error_code
    else:
        path = 'landing/error_page.html'
        ctx['language'] = landing_language(
            request
        )
        ctx['error_code'] = error_code

    return render(request, path, ctx)


def handler404(request):
    return error_page(request, 404)

def handler400(request):
    return error_page(request, 400)

def handler500(request):
    return error_page(request, 500)

def static_page(request, page):
    '''
        View (static page)
    '''

    ctx = get_context(request)

    if ctx['user']:
        path = 'app/static.html'
        ctx['page'] = page
    else:
        path = 'landing/static.html'
        ctx['language'] = landing_language(
            request
        )
        ctx['page'] = page

    return render(request, path, ctx)
