"""Support for estimate data from redfin.com."""
from datetime import timedelta
import logging

import voluptuous as vol
from redfin import Redfin
from homeassistant import config_entries, core

from .const import (DEFAULT_NAME, DOMAIN, CONF_PROPERTIES, ATTRIBUTION, DEFAULT_SCAN_INTERVAL, CONF_PROPERTY_IDS,
                    ICON, CONF_PROPERTY_ID, ATTR_AMOUNT, ATTR_AMOUNT_FORMATTED, ATTR_ADDRESS, ATTR_FULL_ADDRESS,
                    ATTR_CURRENCY, ATTR_STREET_VIEW, ATTR_REDFIN_URL, RESOURCE_URL, ATTR_UNIT_OF_MEASUREMENT)
from homeassistant.core import callback
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME, CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_PROPERTY_IDS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                     ): vol.All(vol.Coerce(int)),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

SCAN_INTERVAL = timedelta(hours=12)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [RedfinDataSensor(config[CONF_NAME], params, config[CONF_SCAN_INTERVAL])
               for params in config[CONF_PROPERTIES]]
    async_add_entities(sensors, update_before_add=True)


class RedfinDataSensor(SensorEntity):
    """Implementation of a Redfin sensor."""

    def __init__(self, name, params, interval):
        """Initialize the sensor."""
        self._name = name
        self.params = params
        self.data = None
        self.address = None
        self.property_id = params[CONF_PROPERTY_ID]
        self._state = None
        self._interval = timedelta(minutes=interval)

    @property
    def unique_id(self):
        """Return the property_id."""
        return self.params[CONF_PROPERTY_ID]

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} {self.address}"

    @property
    def state(self):
        """Return the state of the sensor."""
        try:
            # return self._state
            return round(float(self._state), 1)
        except ValueError:
            return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = {}
        if self.data is not None:
            attributes = self.data
        return attributes

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    async def async_added_to_hass(self):
        """Start custom polling."""

        @callback
        def async_update(event_time=None):
            """Update the entity."""
            self.async_schedule_update_ha_state(True)

        async_track_time_interval(self.hass, async_update, self._interval)

    def update(self):
        """Get the latest data and update the states."""

        client = Redfin()
        try:
            avm_details = client.avm_details(self.params[CONF_PROPERTY_ID], "")
            if avm_details["resultCode"] != 0:
                _LOGGER.error("The API returned: %s",
                              avm_details["errorMessage"])
        except:
            _LOGGER.error("Unable to retrieve data from %s", RESOURCE_URL)
            return
        _LOGGER.debug("%s - The avm_details API returned: %s for property id: %s",
                      self._name, avm_details["errorMessage"], self.params[CONF_PROPERTY_ID])

        try:
            above_the_fold = client.above_the_fold(
                self.params[CONF_PROPERTY_ID], "")
            if above_the_fold["resultCode"] != 0:
                _LOGGER.error("The API returned: %s",
                              above_the_fold["errorMessage"])
        except:
            _LOGGER.error("Unable to retrieve data from %s", RESOURCE_URL)
            return
        _LOGGER.debug("%s - The above_the_fold API returned: %s for property id: %s",
                      self._name, above_the_fold["errorMessage"], self.params[CONF_PROPERTY_ID])

        try:
            info_panel = client.info_panel(self.params[CONF_PROPERTY_ID], "")
            if info_panel["resultCode"] != 0:
                _LOGGER.error("The API returned: %s",
                              info_panel["errorMessage"])
        except:
            _LOGGER.error("Unable to retrieve data from %s", RESOURCE_URL)
            return
        _LOGGER.debug("%s - The info_panel API returned: %s for property id: %s",
                      self._name, info_panel["errorMessage"], self.params[CONF_PROPERTY_ID])

        if 'url' in info_panel["payload"]["mainHouseInfo"]:
            redfinUrl = RESOURCE_URL + \
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
        details[ATTR_UNIT_OF_MEASUREMENT] = details[ATTR_CURRENCY]
        details[ATTR_AMOUNT_FORMATTED] = sectionPreviewText
        details[ATTR_ADDRESS] = address_line
        details[ATTR_FULL_ADDRESS] = self.address
        details[ATTR_REDFIN_URL] = redfinUrl
        details[ATTR_STREET_VIEW] = streetViewUrl
        details[CONF_PROPERTY_ID] = self.params[CONF_PROPERTY_ID]
        details[ATTR_ATTRIBUTION] = ATTRIBUTION

        self.data = details

        if self.data is not None:
            self._state = self.data[ATTR_AMOUNT]
        else:
            self._state = None
            _LOGGER.error("Unable to get Redfin estimate from response")
