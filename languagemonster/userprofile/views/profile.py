from django_countries import countries
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from utility.views import (
    AuthContextView,
    NoTemplateMixin,
)

from core.impl.user import (
    authenticate_user,
    update_public_name,
    process_games_list,
)

from vocabulary.impl.study import get_user_games

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
