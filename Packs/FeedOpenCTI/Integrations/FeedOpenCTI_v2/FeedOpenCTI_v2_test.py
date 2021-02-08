import pytest

from FeedOpenCTI_v2 import get_indicators_command, fetch_indicators_command, get_indicators, indicator_delete_command, \
    indicator_field_update_command, indicator_create_or_update_command
from test_data.feed_data import RESPONSE_DATA, RESPONSE_DATA_WITHOUT_INDICATORS
from CommonServerPython import CommandResults


class StixCyberObservable:
    def list(self):
        return self

    def delete(self):
        return self

    def update_field(self):
        return self

    def create(self):
        return self


class Client:
    temp = ''
    stix_cyber_observable = StixCyberObservable


def test_get_indicators(mocker):
    """Tests get_indicators function
    Given
        The following indicator types: 'registry-key-value', 'user-account' that were chosen by the user.
    When
        - `fetch_indicators_command` or `get_indicators_command` are calling the get_indicators function
    Then
        - convert the result to indicators list
        - validate the length of the indicators list
        - validate the new_last_id that is saved into the integration context is the same as the ID returned by the
            command.
    """
    client = Client
    mocker.patch.object(client.stix_cyber_observable, 'list', return_value=RESPONSE_DATA)
    new_last_id, indicators = get_indicators(client, indicator_type=['registry-key-value', 'user-account'], limit=10)
    assert len(indicators) == 2
    assert new_last_id == 'YXJyYXljb25uZWN0aW9uOjI='


def test_fetch_indicators_command(mocker):
    """Tests fetch_indicators_command function
    Given
        The following indicator types: 'registry-key-value', 'user-account' that were chosen by the user.
    When
        - Calling `fetch_indicators_command`
    Then
        - convert the result to indicators list
        - validate the length of the indicators list
    """
    client = Client
    mocker.patch.object(client.stix_cyber_observable, 'list', return_value=RESPONSE_DATA)
    indicators = fetch_indicators_command(client, indicator_type=['registry-key-value', 'user-account'], max_fetch=200)
    assert len(indicators) == 2


def test_get_indicators_command(mocker):
    """Tests get_indicators_command function
    Given
        The following indicator types: 'registry-key-value', 'user-account' that were chosen by the user and 'limit': 2
    When
        - Calling `get_indicators_command`
    Then
        - convert the result to human readable table
        - validate the readable_output, raw_response.
    """
    client = Client
    args = {
        'indicator_types': 'registry-key-value,user-account',
        'limit': 2
    }
    mocker.patch.object(client.stix_cyber_observable, 'list', return_value=RESPONSE_DATA)
    results: CommandResults = get_indicators_command(client, args)
    assert len(results.raw_response) == 2
    assert "Indicators from OpenCTI" in results.readable_output


def test_get_indicators_command_with_no_data_to_return(mocker):
    """Tests get_indicators_command function with no data to return
    Given
        The following indicator types: 'registry-key-value', 'user-account' that were chosen by the user.
    When
        - Calling `get_indicators_command`
    Then
        - validate the response to have a "No indicators" string
    """
    client = Client
    args = {
        'indicator_types': ['registry-key-value', 'user-account']
    }
    mocker.patch.object(client.stix_cyber_observable, 'list', return_value=RESPONSE_DATA_WITHOUT_INDICATORS)
    results: CommandResults = get_indicators_command(client, args)
    assert "No indicators" in results.readable_output


def test_indicator_delete_command(mocker):
    """Tests indicator_delete_command function
    Given
        id of indicator to delete
    When
        - Calling `indicator_delete_command`
    Then
        - validate the response to have a "Indicator deleted." string
    """
    client = Client
    args = {
        'id': '123456'
    }
    mocker.patch.object(client.stix_cyber_observable, 'delete', return_value="Indicator deleted")
    results: CommandResults = indicator_delete_command(client, args)
    assert "Indicator deleted" in results.readable_output


@pytest.mark.parametrize(argnames="key, value",
                         argvalues=[('score', '50'),
                                    ('description', 'new description')])
def test_indicator_field_update_command(mocker, key, value):
    """Tests indicator_field_update_command function
    Given
        id of indicator to update
        key to update
        value to update
    When
        - Calling `indicator_field_update_command`
    Then
        - validate the response to have a "Indicator deleted." string and context as expected
    """
    client = Client
    args = {
        'id': '123456',
        'key': key,
        'value': value
    }
    mocker.patch.object(client.stix_cyber_observable, 'update_field', return_value={'id': '123456'})
    results: CommandResults = indicator_field_update_command(client, args)
    assert "Indicator updated successfully" in results.readable_output
    assert {'id': '123456'} == results.outputs


def test_indicator_create_or_update_command(mocker):
    """Tests indicator_field_update_command function
    Given
        id of indicator to update
        key to update
        value to update
    When
        - Calling `indicator_field_update_command`
    Then
        - validate the response to have a "Indicator deleted." string and context as expected
    """
    client = Client
    args = {
        'id': '123456',
        'score': '20',
        'type': 'Domain-Name',
        'data': "{\"value\": \"devtest.com\"}"
    }
    mocker.patch.object(client.stix_cyber_observable, 'create', return_value={'id': '123456'})
    results: CommandResults = indicator_create_or_update_command(client, args)
    assert "Indicator created successfully" in results.readable_output
    assert {'id': '123456'} == results.outputs
