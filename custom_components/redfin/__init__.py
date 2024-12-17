import aiohttp
import logging

from .api import ApiClient
from .coordinator import RedfinDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry):
    """Set up the Redfin integration."""
    _LOGGER.info("Setting up Redfin integration")
    session = aiohttp.ClientSession()  # Create the aiohttp session
    hass.data.setdefault(DOMAIN, {})  # Ensure domain storage exists

    try:
        api_client = ApiClient(session)

        # Assume `property_id` is part of the configuration entry
        property_id = config_entry.data["property_id"]

        coordinator = RedfinDataUpdateCoordinator(hass, api_client, property_id)
        await coordinator.async_config_entry_first_refresh()

        # Store coordinator and session for cleanup
        hass.data[DOMAIN][config_entry.entry_id] = {
            "coordinator": coordinator,
            "session": session,
        }

        # Update the entry title if needed
        hass.config_entries.async_update_entry(
            config_entry,
            title=f"Redfin {config_entry.data['property_id']}",
        )

        hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator

        # Continue setting up platforms like sensors or switches
        # hass.config_entries.async_setup_platforms(config_entry, ["sensor"])
        await hass.config_entries.async_forward_entry_setups(config_entry, ["sensor"])
    except Exception as err:
        _LOGGER.error("Error setting up Redfin integration: %s", err)
        await session.close()  # Close the session if setup fails
        return False

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry and clean up resources."""
    _LOGGER.info("Unloading Redfin integration")

    # Retrieve the session and coordinator
    entry_data = hass.data[DOMAIN].pop(config_entry.entry_id, {})
    session = entry_data.get("session")

    # Close the session
    if session:
        await session.close()

    # Unload the platform(s)
    return await hass.config_entries.async_unload_platforms(config_entry, ["sensor"])
