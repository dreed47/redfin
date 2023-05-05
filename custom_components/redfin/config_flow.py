from copy import deepcopy
import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries, core
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get,
)

from .const import (CONF_PROPERTIES, DOMAIN, DEFAULT_SCAN_INTERVAL, DEFAULT_NAME,
                    CONF_PROPERTY_ID, CONF_SCAN_INTERVAL_MIN, CONF_SCAN_INTERVAL_MAX)

_LOGGER = logging.getLogger(__name__)

CONF_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                     ): vol.All(vol.Coerce(int), vol.Range(min=CONF_SCAN_INTERVAL_MIN, max=CONF_SCAN_INTERVAL_MAX))
    }
)
PROPERTY_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_PROPERTY_ID): cv.string,
        vol.Optional("add_another"): cv.boolean,
    }
)


class RedfinConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Redfin config flow."""

    VERSION = 1

    data: Optional[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = {}

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if self.hass.data.get(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            self.data = dict()  # user_input
            self.options = user_input
            self.options[CONF_PROPERTIES] = []
            # Return the form of the next step.
            return await self.async_step_property()

        return self.async_show_form(
            step_id="user", data_schema=CONF_SCHEMA, errors=errors
        )

    async def async_step_property(self, user_input: Optional[Dict[str, Any]] = None):
        """Second step in config flow to add a property id's."""
        errors: Dict[str, str] = {}

        if user_input is not None:

            # check for duplicate property id's
            is_dup = False
            for params in self.options[CONF_PROPERTIES]:
                if user_input[CONF_PROPERTY_ID] == params[CONF_PROPERTY_ID]:
                    is_dup = True
            if is_dup == True:
                errors["base"] = "duplicate_property_id"
            else:
                self.options[CONF_PROPERTIES].append(
                    {"property_id": user_input[CONF_PROPERTY_ID]}
                )

            if not errors:
                # If user ticked the box show this form again so they can add
                if user_input.get("add_another", False):
                    return await self.async_step_property()

                # User is done adding properties, create the config entry.
                _LOGGER.debug(
                    "%s component added a new config entry: %s", DOMAIN, self.options)
                return self.async_create_entry(title=self.options["name"], data=self.data, options=self.options)

        return self.async_show_form(
            step_id="property", data_schema=PROPERTY_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handles options flow for the component."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Manage the options for the component."""
        errors: Dict[str, str] = {}
        # Grab all configured propert id's from the entity registry so we can populate the
        # multi-select dropdown that will allow a user to remove a property.
        entity_registry = sync_get(self.hass)
        entries = async_entries_for_config_entry(
            entity_registry, self.config_entry.entry_id
        )
        # Default value for our multi-select.
        all_properties = {e.entity_id: e.original_name for e in entries}
        property_map = {e.entity_id: e for e in entries}

        if user_input is not None:
            updated_properties = deepcopy(
                self.config_entry.options[CONF_PROPERTIES])

            # Remove any unchecked properties.
            removed_entities = [
                entity_id
                for entity_id in property_map.keys()
                if entity_id not in user_input["properties"]
            ]
            for entity_id in removed_entities:
                # Unregister from HA
                entity_registry.async_remove(entity_id)
                # Remove from our configured properties.
                entry = property_map[entity_id]
                property_id = entry.unique_id
                updated_properties = [
                    e for e in updated_properties if e[CONF_PROPERTY_ID] != property_id]

            if user_input.get(CONF_PROPERTY_ID):

                # check for duplicate property id's
                is_dup = False
                for params in updated_properties:
                    if user_input[CONF_PROPERTY_ID] == params[CONF_PROPERTY_ID]:
                        is_dup = True
                if is_dup == True:
                    errors["base"] = "duplicate_property_id"
                else:
                    # Add the new property.
                    updated_properties.append(
                        {CONF_PROPERTY_ID: user_input[CONF_PROPERTY_ID]}
                    )

            if not errors:
                # Value of data will be set on the options property of the config_entry
                # instance.
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                        CONF_PROPERTIES: updated_properties
                    },
                )

        options_schema = vol.Schema(
            {
                vol.Optional("properties", default=list(all_properties.keys())): cv.multi_select(
                    all_properties
                ),
                vol.Optional(CONF_NAME, default=self.config_entry.options[CONF_NAME]): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=self.config_entry.options[CONF_SCAN_INTERVAL]
                             ): vol.All(vol.Coerce(int), vol.Range(min=CONF_SCAN_INTERVAL_MIN, max=CONF_SCAN_INTERVAL_MAX)),
                vol.Optional(CONF_PROPERTY_ID): cv.string,
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )
