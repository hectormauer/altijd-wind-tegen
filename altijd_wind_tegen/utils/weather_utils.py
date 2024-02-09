# TODO I should subdivide this by country. Currently only works for the UK.
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal

import aiohttp
from shapely import Point

from .data_types import DailyWindPrediction


@dataclass
class WeatherOffice:
    api_key: str
    base_url: str =  "http://datapoint.metoffice.gov.uk/public/data"
    data_format: Literal["json", "xml"] = "json"
    locations_by_location_id: dict[int, Point] = field(init=False)
    location_id_by_location: dict[Point, int] = field(init=False)

    async def get_site_locations(self):
        # This takes 0.5 seconds. Not sure if I can speed it.
        site_locations_url = f"{self.base_url}/val/wxfcs/all/{self.data_format}/sitelist?key={self.api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(site_locations_url) as response:
                locations_as_dict = await response.json()
        self.locations_by_location_id = {
            l["id"]: Point(l["longitude"], l["latitude"]) for l in locations_as_dict["Locations"]["Location"]
        }
        self.location_id_by_location = {
            Point(l["longitude"], l["latitude"]): l["id"] for l in locations_as_dict["Locations"]["Location"]
        }

    async def get_wind_predictions_for_location(
        self,
        location_id: int,
        temporal_resolution: str = "daily",
        prediction_date: str = (datetime.now() + timedelta(1)).strftime("%Y-%m-%dT"),
    ) -> list[DailyWindPrediction]:
        # daily predictions return two, one for AM, one for PM
        # 3hourly return for 0, 3, 6, 9, 12, 15, 18, 21
        # Let's stick to daily and the AM for simplicity
        # prediction date defaults to tomorrow.
        forecast_url_by_location_id = (
            f"{self.base_url}/val/wxfcs/all/{self.data_format}/{location_id}?"
            f"res={temporal_resolution}&time={prediction_date}&key={self.api_key}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(forecast_url_by_location_id) as response:
                forecast_as_dict = await response.json()
        winds = [
            DailyWindPrediction.from_dict(wind_prediction)
            for wind_prediction in forecast_as_dict["SiteRep"]["DV"]["Location"]["Period"]["Rep"]
        ]
        return winds
