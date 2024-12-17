import asyncio
import json

import aiohttp

from .const import RESOURCE_URL, USER_AGENT


class ApiClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.base_url = f"{RESOURCE_URL}/stingray/api/home/details/"

    async def get_home_details(self, end_point: str, property_id: str) -> dict:
        url = f"{self.base_url}{end_point}?accessLevel=1&propertyId={property_id}&listingId="
        headers = {
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        for attempt in range(2):
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    # Parse and return the data
                    raw_text = await response.text()
                    cleaned_text = raw_text[4:]
                    return json.loads(cleaned_text)
                if response.status == 202:
                    # Wait and try again
                    await asyncio.sleep(2)
                else:
                    raise Exception(f"Error fetching data: {response.status}")

        raise Exception("Timeout waiting for final response")
