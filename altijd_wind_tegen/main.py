import asyncio
import os

from .utils.data_types import DailyWindPrediction, TrackSegment
from .utils.geom_utils import calculate_track_segment_bearings, get_broad_direction_percentace, get_closest_weather_site
from .utils.gpx_parser import parse
from .utils.weather_utils import WeatherOffice

api_key = os.environ["MET_API_KEY"]


async def main(test_file_location: str):
    list_of_tracks = parse(test_file_location)
    track_segment: TrackSegment = list_of_tracks[0].track_segments[0]
    calculate_track_segment_bearings(track_segment)
    bearing_by_percentage_of_segment = track_segment.bearing_by_percentage_of_length

    office_client = WeatherOffice(api_key=api_key)
    await office_client.get_site_locations()
    closest_site = get_closest_weather_site(track_segment.get_centroid, office_client.location_id_by_location)

    wind_predictions: list[DailyWindPrediction] = await office_client.get_wind_predictions_for_location(closest_site)
    broad_direction_percentage = get_broad_direction_percentace(
        wind_predictions[0].wind_direction, bearing_by_percentage_of_segment
    )
    print(
        f"The main wind direction tomorrow will be {wind_predictions[0].wind_direction} at {wind_predictions[0].wind_speed} {wind_predictions[0].units}"
    )
    print(
        f"Your ride ({list_of_tracks[0].name}) will be facing this direction {broad_direction_percentage} % of the time"
    )


if __name__ == "__main__":
    asyncio.run(main("altijd_wind_tegen/test-files/malvern-mad-hare.gpx"))
    asyncio.run(main("altijd_wind_tegen/test-files/alcester_proper.gpx"))
    asyncio.run(main("altijd_wind_tegen/test-files/de-muro-a-avila.gpx"))
    asyncio.run(main("altijd_wind_tegen/test-files/adams-croissant.gpx"))
