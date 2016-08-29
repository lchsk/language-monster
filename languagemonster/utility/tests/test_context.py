from mock import (
    Mock,
    MagicMock,
)

from django.http import HttpResponseRedirect

from utility import views

from django.test.client import RequestFactory

from utility import interface, context

context.Context._get_user = MagicMock()

rf = RequestFactory()
get_request = rf.get('/hello/')
post_request = rf.post('/submit/', {'foo': 'bar'})

request = Mock(user=Mock())

def _setup_request(view_class, request, authenticated=False, superuser=False):
    view = view_class()
    view.request = request
    view.get_template_names = MagicMock()

    setattr(
        request,
        'user',
        Mock(
            is_authenticated=MagicMock(return_value=authenticated),
            is_superuser=superuser,
        ),
    )

    return view

def test_auth_context_fail():
    view = _setup_request(
        view_class=views.AuthContextView,
        request=rf.get('/'),
    )

    resp = view.dispatch(view.request)

    assert type(resp) == HttpResponseRedirect

def test_auth_context_succeed():
    view = _setup_request(
        view_class=views.AuthContextView,
        request=rf.get('/'),
        authenticated=True,
    )

    resp = view.dispatch(view.request)

    assert resp.status_code == 200

def test_superauth_context_fail():
    view = _setup_request(
        view_class=views.SuperUserContextView,
        request=rf.get('/'),
        authenticated=True,
    )

    resp = view.dispatch(view.request)

    assert type(resp) == HttpResponseRedirect

def test_superauth_context_succeed():
    view = _setup_request(
        view_class=views.AuthContextView,
        request=rf.get('/'),
        authenticated=True,
        superuser=True,
    )

    resp = view.dispatch(view.request)

    assert resp.status_code == 200
