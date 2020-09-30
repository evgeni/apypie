from __future__ import print_function, absolute_import

from apypie.route import Route
from apypie.example import Example
from apypie.param import Param
from apypie.exceptions import MissingArgumentsError, InvalidArgumentTypesError

try:
    basestring
except NameError:  # Python 3 has no basestring
    basestring = str  # pylint: disable=W0622


class Action:
    """
    Apipie Action
    """

    def __init__(self, name, resource, api):
        self.name = name
        self.resource = resource
        self.api = api

    @property
    def apidoc(self):
        resource_methods = self.api.apidoc['docs']['resources'][self.resource]['methods']
        return [method for method in resource_methods if method['name'] == self.name][0]

    @property
    def routes(self):
        return [Route(route['api_url'], route['http_method'], route['short_description']) for route in self.apidoc['apis']]

    @property
    def params(self):
        return [Param(**param) for param in self.apidoc['params']]

    @property
    def examples(self):
        return [Example.parse(example) for example in self.apidoc['examples']]

    def call(self, params={}, headers={}, options={}, data=None, files=None):
        return self.api.call(self.resource, self.name, params, headers, options, data, files)

    def find_route(self, params=None):
        param_keys = set(self.filter_empty_params(params).keys())
        sorted_routes = sorted(self.routes, key=lambda route: [-1 * len(route.params_in_path), route.path])
        for route in sorted_routes:
            if set(route.params_in_path) <= param_keys:
                return route
        return sorted_routes[-1]

    def validate(self, values=None, data=None, files=None):
        self._validate(self.params, values, data, files)

    def _add_to_path(self, path=None, *additions):
        if path is None:
            path = ''
        for addition in additions:
            if path == '':
                path = "{}".format(addition)
            else:
                path = "{}[{}]".format(path, addition)
        return path

    def _validate(self, params, values, data=None, files=None, path=None):
        given_params = set(self.filter_empty_params(values).keys())
        given_files = set((files or {}).keys())
        given_data = set((data or {}).keys())
        required_params = set([param.name for param in params if param.required])
        missing_params = required_params - given_params - given_files - given_data
        if missing_params:
            missing_params_with_path = [self._add_to_path(path, param) for param in missing_params]
            message = "The following required parameters are missing: {}".format(', '.join(missing_params_with_path))
            raise MissingArgumentsError(message)

        for param, value in values.items():
            param_descriptions = [p for p in params if p.name == param]
            if param_descriptions:
                param_description = param_descriptions[0]
                if param_description.params and value is not None:
                    if param_description.expected_type == 'array':
                        for num, item in enumerate(value):
                            self._validate(param_description.params, item, path=self._add_to_path(path, param_description.name, num))
                    elif param_description.expected_type == 'hash':
                        self._validate(param_description.params, value, path=self._add_to_path(path, param_description.name))
                if (param_description.expected_type == 'numeric' and isinstance(value, basestring)):
                    try:
                        value = int(value)
                    except ValueError:
                        # this will be caught in the next check
                        pass
                if ((param_description.expected_type == 'boolean' and not isinstance(value, bool) and not (isinstance(value, int) and value in [0, 1]))
                        or (param_description.expected_type == 'numeric' and not isinstance(value, int))
                        or (param_description.expected_type == 'string' and not isinstance(value, (basestring, int)))):
                    raise ValueError("{} ({}): {}".format(param, value, param_description.validator))

    def filter_empty_params(self, params=None):
        if params is not None:
            if isinstance(params, dict):
                return dict((k, v) for k, v in params.items() if v is not None)
            else:
                raise InvalidArgumentTypesError
        else:
            return {}

    def prepare_params(self, input_dict):
        """
        Transform a dict with data into one that can be accepted as params for calling the action.

        This will ignore any keys that are not accepted as params when calling the action.
        It also allows generating nested params without forcing the user to care about them.

        :param input_dict: a dict with data that should be used to fill in the params
        :return: :class:`dict` object
        :rtype: dict

        Usage::

            >>> action.prepare_params({'id': 1})
            {'user': {'id': 1}}
        """
        return self._prepare_params(self.params, input_dict)

    def _prepare_params(self, action_params, input_dict):
        result = {}

        for param in action_params:
            if param.expected_type == 'hash' and param.params:
                nested_result = self._prepare_params(param.params, input_dict)
                if nested_result:
                    result[param.name] = nested_result
            elif param.name in input_dict:
                result[param.name] = input_dict[param.name]

        return result
