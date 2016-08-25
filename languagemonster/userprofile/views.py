from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django_countries.fields import Country
from django.http import Http404

from core.views import get_context
from core.models import (
    MonsterUser,
    Progression,
)

from core.data.language_pair import LANGUAGE_PAIRS_FLAT

from utility.views import AuthContextView
from utility.interface import obfuscate

class UserPage(AuthContextView):
    template_name = 'app/public_page.html'

    def get_context_data(self, **kwargs):
        context = super(UserPage, self).get_context_data(**kwargs)

        user = MonsterUser.objects.filter(
            uri=self.kwargs['identifier']
        ).select_related('user')

        if len(user) != 1:
            raise Http404

        user = user.first()

        progressions = Progression.objects.filter(user=user)

        if user.public_name == user.user.email:
            login, host = user.user.email.split('@')

            username = obfuscate(login, '*', half=2)
        else:
            username = user.public_name

        country = Country(user.country)

        knows, studies = set(), set()

        for pair in progressions:
            pair = LANGUAGE_PAIRS_FLAT[pair.lang_pair]
            knows.add(pair.base_language)
            studies.add(pair.target_language)

        context['country'] = country if country else None
        context['username'] = username
        context['knows'] = knows
        context['studies'] = studies
        context['u'] = user

        return context
