from api.views.base import APIAuthView

class Ping(APIAuthView):
    def get(self, request):
        return self.success({})
