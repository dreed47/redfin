import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Redfin sensor from a config entry."""
    coordinator = hass.data["redfin"][config_entry.entry_id]

    property_id = config_entry.data.get("property_id")

    # Create a single sensor (no need for sensor_type)
    sensor = RedfinSensor(coordinator, property_id)
    async_add_entities([sensor], update_before_add=True)


class RedfinSensor(CoordinatorEntity):
    """Defines a single Redfin sensor with multiple attributes."""

    def __init__(self, coordinator, property_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.property_id = property_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Redfin {self.property_id}"

    @property
    def state(self):
        """Return the primary state of the sensor."""
        # Example: Use price as the primary state
        return self.coordinator.data.get("amount_formatted")

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"redfin_{self.property_id}"

    @property
    def extra_state_attributes(self):
        """Return the extra attributes of the sensor."""
        # Include additional details as attributes
        return {
            "amount": self.coordinator.data.get("amount"),
            "amount_currency": self.coordinator.data.get("amount_currency"),
            "unit_of_measurement": self.coordinator.data.get("unit_of_measurement"),
            "amount_formatted": self.coordinator.data.get("amount_formatted"),
            "address": self.coordinator.data.get("address"),
            "full_address": self.coordinator.data.get("full_address"),
            "redfin_url": self.coordinator.data.get("redfin_url"),
            "street_view": self.coordinator.data.get("street_view"),
            "bedrooms": self.coordinator.data.get("bedrooms"),
            "bathrooms": self.coordinator.data.get("bathrooms"),
            "square_feet": self.coordinator.data.get("square_feet"),
            "property_id": self.coordinator.data.get("property_id"),
            "attribution": self.coordinator.data.get("attribution"),
        }

    @property
    def device_info(self):
        """Return device information for the integration."""
        return {
            "identifiers": {(self.property_id, "redfin")},
            "name": f"Redfin Home {self.property_id}",
            "manufacturer": "Redfin",
            "model": "Home Details",
            "entry_type": "service",  # Optional: marks it as a service-based device
        }
