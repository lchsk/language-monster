from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django_countries.fields import Country
from django.http import Http404

from core.views import get_context
from core.models import (
    MonsterUser,
    Progression,
)

from utility.interface import obfuscate


@login_required
def public_page(request, identifier):
    '''
        User's public page view.
    '''

    c = get_context(request)

    if c['user'].uri == identifier:
        u = c['user']

        progressions = c['basic']['studying']
    else:
        u = MonsterUser.objects.filter(
            uri=identifier
        ).select_related('user').first()

        progressions = Progression.objects.filter(
            user=u
        )

    if u:
        if u.public_name == u.user.email:
            # Bad...
            login, host = u.user.email.split('@')

            c['username'] = obfuscate(login, '*', half=2)
        else:
            # OK
            c['username'] = u.public_name

        country = Country(u.country)

        c['country'] = country if country else None

        knows, studies = set(), set()

        for p, pair in progressions:
            knows.add(pair.base_language)
            studies.add(pair.target_language)

        c['knows'] = knows
        c['studies'] = studies

        # TODO:
        # c['age'] = calculate_age (u['birthday'])

        c['u'] = u
    else:
        raise Http404

    return render(request, 'app/public_page.html', c)
