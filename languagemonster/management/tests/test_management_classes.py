import inspect

from management import views

from utility.views import SuperUserContextView
from utility.testing import assert_subclasses

def management_view_predicate(name):
    return any((
        name.startswith('Do'),
        name.endswith('View'),
        'Dispatch' in name,
    ))

def test_management_views_auth():
    assert_subclasses(
        classes=inspect.getmembers(views),
        class_=SuperUserContextView,
        predicate=management_view_predicate,
    )
