#!/usr/bin/env python
import os
import sys
import inspect

import requests

if __name__ == "__main__":
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "languagemonster.settings"
    )

    import django
    django.setup()

    from languagemonster.settings import API_KEY

    from api.urls import urlpatterns
    from api.views2.base import APIAuthView

    patterns = sorted(urlpatterns, key=lambda x: x.name)

    for ep in patterns:
        auth_type = 'Unknown'
        methods = []

        cls_ = ep._callback.cls
        functions = inspect.getmembers(cls_, predicate=inspect.ismethod)

        for name, _ in functions:
            if name in ('post', 'get', 'put', 'delete'):
                methods.append(name.upper())

        if APIAuthView in cls_.__bases__:
            auth_type = 'Key'

        print '{0:20}\t{1:10}\t{2:10}\t{3}'.format(
            ep.name,
            auth_type,
            ', '.join(methods),
            ep._regex,
        )
