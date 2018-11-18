from __future__ import print_function, absolute_import

import json

from apypie.resource import Resource

class Api:
    """
    Apipie API bindings
    """

    def __init__(self, apifile):
        with open(apifile, 'r') as f:
            self.apidoc = json.load(f)
            self.options = {'skip_validation': True}

    @property
    def resources(self):
        return sorted(self.apidoc['docs']['resources'].keys())

    def resource(self, name):
        if name in self.resources:
            return Resource(self, name)
        else:
            raise IOError

    def call(self, resource_name, action_name, params={}, headers={}, options={}):
        resource = Resource(self, resource_name)
        action = resource.action(action_name)
        if not self.options['skip_validation']:
            action.validate(params)

        self.call_action(action, params, headers, options)

    def call_action(self, action, params={}, headers={}, options={}):
        route = action.find_route(params)
        get_params = dict((key, value) for key, value in params.items() if key not in route.params_in_path)
        return (
            route.method,
            route.path_with_params(params),
            get_params,
            headers, options)