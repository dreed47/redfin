"""Support for estimate data from redfin.com."""
from datetime import timedelta
import logging

import voluptuous as vol
from redfin import Redfin

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)
_RESOURCE = "https://www.redfin.com"

ATTRIBUTION = "Data provided by Redfin.com"

CONF_PROPERTY_IDS = "property_ids"

DEFAULT_NAME = "Redfin"
NAME = "redfin"

ICON = "mdi:home-variant"

ATTR_AMOUNT = "amount"
ATTR_AMOUNT_FORMATTED = "amount_formatted"
ATTR_ADDRESS = "address"
ATTR_FULL_ADDRESS = "full_address"
ATTR_CURRENCY = "amount_currency"
ATTR_STREET_VIEW = "street_view"
ATTR_REDFIN_URL = "redfin_url"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_PROPERTY_IDS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

SCAN_INTERVAL = timedelta(hours=12)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Redfin sensor."""

    name = config.get(CONF_NAME)
    properties = config[CONF_PROPERTY_IDS]

    sensors = []
    for property_id in properties:
        params = {"property_id": property_id}
        sensors.append(RedfinDataSensor(name, params))
    add_entities(sensors, True)


class RedfinDataSensor(SensorEntity):
    """Implementation of a Redfin sensor."""

    def __init__(self, name, params):
        """Initialize the sensor."""
        self._name = name
        self.params = params
        self.data = None
        self.address = None
        self._state = None

    @property
    def unique_id(self):
        """Return the property_id."""
        return self.params["property_id"]

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} {self.address}"

    @property
    def state(self):
        """Return the state of the sensor."""
        try:
            return self._state
            # return round(float(self._state), 1)
        except ValueError:
            return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = {}
        if self.data is not None:
            attributes = self.data
        attributes[ATTR_ADDRESS] = self.address
        attributes[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attributes

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    def update(self):
        """Get the latest data and update the states."""

        client = Redfin()
        try:
            avm_details = client.avm_details(self.params["property_id"], "")
            if avm_details["resultCode"] != 0:
                _LOGGER.error("The API returned: %s",
                              avm_details["errorMessage"])
        except:
            _LOGGER.error("Unable to retrieve data from %s", _RESOURCE)
            return
        _LOGGER.debug("The avm_details API returned: %s for property id: %s",
                      avm_details["errorMessage"], self.params["property_id"])

        try:
            above_the_fold = client.above_the_fold(
                self.params["property_id"], "")
            if above_the_fold["resultCode"] != 0:
                _LOGGER.error("The API returned: %s",
                              above_the_fold["errorMessage"])
        except:
            _LOGGER.error("Unable to retrieve data from %s", _RESOURCE)
            return
        _LOGGER.debug("The above_the_fold API returned: %s for property id: %s",
                      above_the_fold["errorMessage"], self.params["property_id"])

        try:
            info_panel = client.info_panel(self.params["property_id"], "")
            if info_panel["resultCode"] != 0:
                _LOGGER.error("The API returned: %s",
                              info_panel["errorMessage"])
        except:
            _LOGGER.error("Unable to retrieve data from %s", _RESOURCE)
            return
        _LOGGER.debug("The info_panel API returned: %s for property id: %s",
                      info_panel["errorMessage"], self.params["property_id"])

        if 'url' in info_panel["payload"]["mainHouseInfo"]:
            redfinUrl = _RESOURCE + \
                info_panel["payload"]["mainHouseInfo"]['url']
        else:
            redfinUrl = 'Not Set'

        if 'streetAddress' in above_the_fold["payload"]["addressSectionInfo"]:
            address_line = above_the_fold["payload"]["addressSectionInfo"]["streetAddress"][
                "assembledAddress"
            ]
            city = above_the_fold["payload"]["addressSectionInfo"]["city"]
            state = above_the_fold["payload"]["addressSectionInfo"]["state"]
            self.address = f"{address_line} {city} {state}"
        else:
            self.address = "unknown"

        if 'streetViewUrl' in above_the_fold["payload"]["mediaBrowserInfo"]["streetView"]:
            streetViewUrl = above_the_fold["payload"]["mediaBrowserInfo"]["streetView"]["streetViewUrl"]
        else:
            streetViewUrl = 'Not Set'

        if 'predictedValue' in avm_details["payload"]:
            predictedValue = avm_details["payload"]["predictedValue"]
        else:
            predictedValue = 'Not Set'

        if 'sectionPreviewText' in avm_details["payload"]:
            sectionPreviewText = avm_details["payload"]["sectionPreviewText"]
        else:
            sectionPreviewText = 'Not Set'

        details = {}
        details[ATTR_AMOUNT] = predictedValue
        details[ATTR_CURRENCY] = "USD"
        details[ATTR_AMOUNT_FORMATTED] = sectionPreviewText
        details[ATTR_ADDRESS] = address_line
        details[ATTR_FULL_ADDRESS] = self.address
        details[ATTR_REDFIN_URL] = redfinUrl
        details[ATTR_STREET_VIEW] = streetViewUrl

        self.data = details

        if self.data is not None:
            self._state = self.data[ATTR_AMOUNT_FORMATTED]
        else:
            self._state = None
            _LOGGER.error("Unable to get Redfin estimate from response")
