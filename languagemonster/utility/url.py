from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect


def get_urls(request):
    '''Returns several useful urls'''

    u = {}
    u['absolute'] = request.build_absolute_uri(reverse('index'))
    u['current'] = request.build_absolute_uri()
    u['media'] = u['absolute'] + settings.MEDIA_URL[1:]
    u['static'] = u['absolute'] + settings.STATIC_URL[1:]
    u['avatar'] = settings.AVATARS_URL_FULL

    return u


def redirect_to_previous_page(request):
    '''
    Redirects back where he came from.
    '''
    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
