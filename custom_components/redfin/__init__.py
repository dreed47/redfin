"""Redfin Component."""
import logging

from homeassistant import config_entries, core

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_PROPERTIES
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    # We allow setup only through config flow type of config
    return True


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up Redfin component from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    hass_data = dict()
    hass_data[CONF_NAME] = entry.options[CONF_NAME]
    hass_data[CONF_SCAN_INTERVAL] = entry.options[CONF_SCAN_INTERVAL]
    hass_data[CONF_PROPERTIES] = entry.options[CONF_PROPERTIES]
    # Registers update listener to update config entry when options are updated.
    unsub_options_update_listener = entry.add_update_listener(
        options_update_listener)
    # Store a reference to the unsubscribe function to cleanup if an entry is unloaded.
    hass_data["unsub_options_update_listener"] = unsub_options_update_listener
    hass.data[DOMAIN][entry.entry_id] = hass_data

    # Forward the setup to the sensor component.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True


async def options_update_listener(
    hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry
):
    _LOGGER.debug("%s options updated: %s", DOMAIN,
                  config_entry.as_dict()["options"])
    """Handle options update."""
    try:
        result = await hass.config_entries.async_reload(config_entry.entry_id)
    except config_entries.OperationNotAllowed:
        _LOGGER.error(
            "Entry cannot be reloaded. ID = %s  Restart is required.", config_entry.entry_id)
    except config_entries.UnknownEntry:
        _LOGGER.error("Invalid entry specified. ID = %s",
                      config_entry.entry_id)
