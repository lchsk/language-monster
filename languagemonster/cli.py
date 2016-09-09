#!/usr/bin/env python
import os
import sys
import inspect
import json
import readline

import requests

class Endpoint(object):
    def __init__(self, name, auth_type, methods, regexp):
        self._name = name
        self._auth_type = auth_type
        self._methods = methods
        self._regexp = regexp
        self._host = 'http://localhost:' + Command.default_port

    @property
    def auth_type(self):
        return self._auth_type

    def get_url(self, kwargs, query):
        try:
            uri = reverse('api:' + self._name, kwargs=kwargs) + query
        except django.core.urlresolvers.NoReverseMatch:
            uri = reverse('api:' + self._name) + query

        return self._host + uri

    def __str__(self):
        return '{0:20}\t{1:10}\t{2:10}\t{3}'.format(
            self._name,
            self._auth_type,
            ', '.join(self._methods),
            self._regexp,
        )

class App(object):
    def __init__(self, patterns):
        self._endpoints = {}
        self._patterns = patterns
        self._headers = {}

        if os.path.exists('./login'):
            with open('./login', 'r') as login_f:
                self._login_hash = login_f.read().strip()

                print 'Read login hash from file'
        else:
            self._login_hash = None

        readline.parse_and_bind('tab: complete')

        self._insert_endpoints()

    def run(self):
        while True:
            cmd = raw_input(">>> ")

            tokens = cmd.split()

            if cmd in ('endpoints', 'ep'):
                self.print_endpoints()
            elif cmd in ('q', 'quit'):
                break
            elif tokens[0] in ('get', 'post'):
                if len(tokens) < 2:
                    return self._help()

                self._run_cmd(*tokens)
            else:
                self._help()

    def print_endpoints(self):
        for ep in sorted(self._endpoints.values(), key=lambda x: x._name):
            print ep

    def _run_cmd(self, cmd, name, *args):
        self._set_headers(name)

        params = {}
        query = ''

        for arg in args:
            if arg.startswith('?'):
                query = arg
            else:
                key, value = arg.split('=')

            params[key] = value

        ep = self._endpoints[name]

        url = ep.get_url(params, query)

        if cmd == 'get':
            resp = requests.get(url, headers=self._headers)
        elif cmd == 'post':
            resp = requests.post(
                url,
                headers=self._headers,
                data=params,
            )

        print '%s %s' % (cmd.upper(), url)
        print self._headers

        if params:
            print json.dumps(params, indent=4)

        print '%s %s' % (resp.status_code, resp.reason)
        print json.dumps(resp.json(), indent=4)

        # Handle MonsterUser login
        if self._login_hash is None:
            self._login_hash = resp.json().get('data', {}).get('login_hash')

            if self._login_hash is not None:
                with open('./login', 'w') as login_f:
                    login_f.write(self._login_hash)

    def _help(self):
        print 'Help:'

    def _set_headers(self, name):
        auth_type = self._endpoints[name].auth_type

        if auth_type == 'key':
            self._headers = dict(Authorization=API_KEY)
        elif auth_type == 'user':
            if self._login_hash is None:
                print 'login_hash is not set - you must login first'
            else:
                self._headers = dict(Authorization=self._login_hash)

    def _insert_endpoints(self):
        for pat in self._patterns:
            auth_type = None
            methods = []

            cls_ = pat._callback.cls
            functions = inspect.getmembers(cls_, predicate=inspect.ismethod)

            for name, _ in functions:
                if name in ('post', 'get', 'put', 'delete'):
                    methods.append(name.upper())

            if APIAuthView in cls_.__bases__:
                auth_type = 'key'
            elif MonsterUserAuthView in cls_.__bases__:
                auth_type = 'user'

            self._endpoints[pat.name] = Endpoint(
                name=pat.name,
                auth_type=auth_type,
                methods=methods,
                regexp=pat._regex,
            )


if __name__ == "__main__":
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "languagemonster.settings"
    )

    import django
    django.setup()

    from django.core.urlresolvers import reverse
    from django.core.management.commands.runserver import Command

    from languagemonster.settings import API_KEY

    from api.urls import urlpatterns
    from api.views2.base import APIAuthView, MonsterUserAuthView

    app = App(urlpatterns)
    app.print_endpoints()

    app.run()
