from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import RESOURCE_URL


_LOGGER = logging.getLogger(__name__)


class RedfinDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api_client, home_id):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Redfin Home Details",
            update_interval=timedelta(minutes=10),  # Adjust interval as needed
        )
        self.api_client = api_client
        self.home_id = home_id
        self.data = None

    async def _async_update_data(self):
        """Fetch data from Redfin API."""
        try:
            _LOGGER.debug("Fetching data from Redfin for home_id: %s", self.home_id)

            avm_data = await self.api_client.get_home_details("avm", self.home_id)

            aboveTheFold_data = await self.api_client.get_home_details(
                "aboveTheFold", self.home_id
            )

            info_panel_data = await self.api_client.get_home_details(
                "mainHouseInfoPanelInfo", self.home_id
            )

            if "url" in info_panel_data["payload"]["mainHouseInfo"]:
                redfinUrl = (
                    RESOURCE_URL + info_panel_data["payload"]["mainHouseInfo"]["url"]
                )
                self.address = info_panel_data["payload"]["mainHouseInfo"][
                    "fullStreetAddress"
                ]
            else:
                redfinUrl = "Not Set"

            if (
                "streetViewUrl"
                in aboveTheFold_data["payload"]["mediaBrowserInfo"]["streetView"]
            ):
                streetViewUrl = aboveTheFold_data["payload"]["mediaBrowserInfo"][
                    "streetView"
                ]["streetViewUrl"]
            else:
                streetViewUrl = "Not Set"

            if "predictedValue" in avm_data["payload"]:
                predictedValue = avm_data["payload"]["predictedValue"]
            else:
                predictedValue = "Not Set"

            if "sectionPreviewText" in avm_data["payload"]:
                sectionPreviewText = avm_data["payload"]["sectionPreviewText"]
            else:
                sectionPreviewText = "Not Set"

            # Processing of the JSON data
            home_data = {
                "property_id": self.home_id,
                "amount": predictedValue,
                "amount_currency": "USD",
                "unit_of_measurement": "USD",
                "amount_formatted": sectionPreviewText,
                "address": avm_data["payload"]["streetAddress"]["assembledAddress"],
                "full_address": self.address,
                "redfin_url": redfinUrl,
                "street_view": streetViewUrl,
                "attribution": "Data provided by Redfin.com",
                "bedrooms": avm_data["payload"]["numBeds"],
                "bathrooms": avm_data["payload"]["numBaths"],
                "square_feet": avm_data["payload"]["sqFt"]["value"],
            }

            return home_data

        except Exception as err:
            _LOGGER.error("Failed to fetch data: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}")
