import apypie
import pytest


def test_resource_action(action):
    assert 'show' == action.name


def test_action_apidoc(action):
    assert action.apidoc


def test_action_routes(action):
    assert action.routes
    assert isinstance(action.routes[0], apypie.Route)


def test_action_route(action):
    route = action.routes[0]
    assert '/users/:id' == route.path
    assert 'get' == route.method


def test_action_params(resource):
    action = resource.action('create')
    assert action.params
    assert ['user'] == [param.name for param in action.params]


def test_action_examples(resource):
    action = resource.action('index')
    assert action.examples


def test_action_example(resource):
    action = resource.action('index')
    example = action.examples[0]
    assert 'GET' == example.http_method
    assert '/users' == example.path
    assert '' == example.args
    assert 200 == example.status
    assert '[ {"user":{"name":"John Doe" }} ]' in example.response


def test_action_call(resource, mocker):
    params = {}
    headers = {'content-type': 'application/json'}
    mocker.patch('apypie.Api.call', autospec=True)
    assert resource.action('index').call(params, headers)
    resource.api.call.assert_called_once_with(resource.api, resource.name, 'index', params, headers, {})


def test_action_find_route(resource):
    action = resource.action('index')
    assert '/users' == action.find_route().path


def test_action_find_route_longest(api):
    action = api.resource('comments').action('archive')
    params = {'id': 1, 'user_id': 1}
    assert '/archive/users/:user_id/comments/:id' == action.find_route(params).path


def test_action_find_route_longest_ignoring_none(api):
    action = api.resource('comments').action('archive')
    params = {'id': 1, 'user_id': None}
    assert '/archive/comments/:id' == action.find_route(params).path


def test_action_validate_missing_required_params(resource):
    action = resource.action('create')
    with pytest.raises(apypie.exceptions.MissingArgumentsError) as excinfo:
        action.validate({'user': {'vip': True}})
    assert "The following required parameters are missing" in str(excinfo.value)
    assert "name" in str(excinfo.value)


def test_action_validate_missing_nested_required_params(resource):
    action = resource.action('create')
    with pytest.raises(apypie.exceptions.MissingArgumentsError) as excinfo:
        action.validate({'user': {'name': 'John Doe', 'address': {'street': 'K JZD'}}})
    assert "The following required parameters are missing" in str(excinfo.value)
    assert "user[address][city]" in str(excinfo.value)


def test_action_validate_missing_nested_required_params_array(resource):
    action = resource.action('create')
    with pytest.raises(apypie.exceptions.MissingArgumentsError) as excinfo:
        action.validate({'user': {'name': 'John Doe', 'contacts': [{'kind': 'email'}]}})
    assert "The following required parameters are missing" in str(excinfo.value)
    assert "user[contacts][0][contact]" in str(excinfo.value)


def test_action_validate_missing_nested_invalid_params(resource):
    action = resource.action('create')
    with pytest.raises(apypie.exceptions.InvalidArgumentTypesError):
        action.validate({'user': {'name': 'John Doe', 'contacts': [1, 2]}})


def test_action_validate_invalid_boolean(resource):
    action = resource.action('create')
    with pytest.raises(ValueError) as excinfo:
        action.validate({'user': {'name': 'John Doe', 'vip': 'maybe'}})
    assert "vip (maybe): Must be one of: <code>true</code>, <code>false</code>, <code>1</code>, <code>0</code>" in str(excinfo.value)


def test_action_validate_valid_boolean(resource):
    action = resource.action('create')
    action.validate({'user': {'name': 'John Doe', 'vip': False}})


def test_action_validate_valid_boolean_as_int(resource):
    action = resource.action('create')
    action.validate({'user': {'name': 'John Doe', 'vip': 0}})


def test_action_validate_invalid_numeric(api):
    action = api.resource('comments').action('archive')
    with pytest.raises(ValueError) as excinfo:
        action.validate({'id': 'MYNUMBER'})
    assert "id (MYNUMBER): Must be a Integer" in str(excinfo.value)


def test_action_validate_valid_numeric(api):
    action = api.resource('comments').action('archive')
    action.validate({'id': 1})


def test_action_validate_invalid_string(resource):
    action = resource.action('create')
    with pytest.raises(ValueError) as excinfo:
        action.validate({'user': {'name': []}})
    assert "name ([]): Must be a String" in str(excinfo.value)


def test_action_validate_valid_string(resource):
    action = resource.action('create')
    action.validate({'user': {'name': 'John Doe'}})


def test_action_validate_valid_string_as_int(resource):
    # workaround for https://projects.theforeman.org/issues/27107
    action = resource.action('create')
    action.validate({'user': {'name': 1}})


def test_action_validate_minimal_correct_params(resource):
    resource.action('create').validate({'user': {'name': 'John Doe'}})
    resource.action('create_unnested').validate({'name': 'John Doe'})


def test_action_validate_full_correct_params(resource):
    action = resource.action('create')
    params = {'user': {
        'name': 'John Doe',
        'vip': True,
        'address': {
            'city': 'Ankh-Morpork',
            'street': 'Audit Alley'
        },
        'contacts': [
            {'contact': 'john@doe.org', 'kind': 'email'},
            {'contact': '123456', 'kind': 'pobox'}
        ]
    }}
    action.validate(params)


@pytest.mark.parametrize('resource,action,input_dict,expected_params', [
    ('comments', 'archive', {'id': 1}, {'id': 1}),
    ('comments', 'archive', {'id': 1, 'should_be_ignored': True}, {'id': 1}),
    ('users', 'create', {'name': 'testuser'}, {'user': {'name': 'testuser'}}),
])
def test_action_prepare_params(api, resource, action, input_dict, expected_params):
    generated_params = api.resource(resource).action(action).prepare_params(input_dict)
    assert expected_params == generated_params
