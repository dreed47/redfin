"""Test component api."""
from homeassistant.setup import async_setup_component
from custom_components.redfin.const import DOMAIN
from redfin import Redfin

client = Redfin()


def test_api_call():
    """  """

    address = '1712 Glen Echo Rd Unit C,Nashville, TN 37215'

    response = client.search(address)
    assert response['errorMessage'] == "Success"

    url = response['payload']['exactMatch']['url']
    initial_info = client.initial_info(url)
    assert initial_info['errorMessage'] == "Success"

    property_id = initial_info['payload']['propertyId']
    mls_data = client.below_the_fold(property_id)
    assert mls_data['errorMessage'] == "Success"

    above_the_fold = client.above_the_fold(property_id, "")
    assert above_the_fold['errorMessage'] == "Success"

    info_panel = client.info_panel(property_id, "")
    assert info_panel['errorMessage'] == "Success"
