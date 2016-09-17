from core.models import Progression

from api.serializers import UserProgressionSerializer
from api.views.base import MonsterUserAuthView

class UserStats(MonsterUserAuthView):
    def get(self, request):
        progression = Progression.objects.filter(user=self.monster_user)

        resp = UserProgressionSerializer(progression, many=True)

        return self.success(resp.data)
