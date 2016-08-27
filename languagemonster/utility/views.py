from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from utility.interface import get_context

class ContextView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(ContextView, self).get_context_data(**kwargs)

        self._context = get_context(self.request)
        context['context'] = self._context

        return context

    def redirect(self, name, args=None, kwargs=None):
        return HttpResponseRedirect(reverse(name, args=args, kwargs=kwargs))

    def redirect_url(self, url):
        return HttpResponseRedirect(url)

class AuthContextView(ContextView):
    def get_context_data(self, **kwargs):
        context = super(AuthContextView, self).get_context_data(**kwargs)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('index'))

        return super(AuthContextView, self).dispatch(request, *args, **kwargs)

class SuperUserContextView(ContextView):
    def get_context_data(self, **kwargs):
        context = super(SuperUserContextView, self).get_context_data(**kwargs)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not all((
            request.user.is_authenticated(),
            request.user.is_superuser,
        )):
            return HttpResponseRedirect(reverse('index'))

        return super(SuperUserContextView, self).dispatch(
            request,
            *args,
            **kwargs
        )

class NoTemplateMixin(object):
    def get_template_names(self):
        return []
