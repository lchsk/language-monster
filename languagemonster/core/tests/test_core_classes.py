import inspect

from core import views

from utility.views import AuthContextView
from utility.testing import assert_subclasses

def core_view_predicate(name):
    if name in (
        'ContextView',
        'DoChangeInterfaceLanguage',
        'DoConfirmNewPassword',
        'DoLogin',
        'DoRecoverPassword',
        'DoRegister',
        'DoSaveContactEmail',
        'IndexView',
        'PickNewPasswordView',
        'SpecialPageView',
    ):
        return False

    return any((
        name.startswith('Do'),
        name.endswith('View'),

    ))

def test_core_views_auth():
    assert_subclasses(
        classes=inspect.getmembers(views),
        class_=AuthContextView,
        predicate=core_view_predicate,
    )
