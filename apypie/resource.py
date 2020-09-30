from __future__ import print_function, absolute_import

from apypie.action import Action

try:
    from typing import Any
except ImportError:
    pass


class Resource:
    """
    Apipie Resource
    """

    def __init__(self, api, name):
        # type: (Any, str) -> None
        self.api = api
        self.name = name

    @property
    def actions(self):
        return sorted([method['name'] for method in self.api.apidoc['docs']['resources'][self.name]['methods']])

    def action(self, name):
        # type: (str) -> Action
        if self.has_action(name):
            return Action(name, self.name, self.api)
        else:
            message = "Unknown action '{}'. Supported actions: {}".format(name, ', '.join(sorted(self.actions)))
            raise KeyError(message)

    def has_action(self, name):
        # type: (str) -> bool
        return name in self.actions

    def call(self, action, params={}, headers={}, options={}, data=None, files=None):
        return self.api.call(self.name, action, params, headers, options, data, files)
