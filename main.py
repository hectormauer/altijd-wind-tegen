import asyncio
from argparse import ArgumentParser
from os import environ

from altijd_wind_tegen.data_types import DailyWindPrediction, TrackSegment
from altijd_wind_tegen.geom_utils import (
    calculate_track_segment_bearings,
    get_broad_direction_percentace,
    get_closest_weather_site,
)
from altijd_wind_tegen.gpx_parser import parse
from altijd_wind_tegen.weather_utils import WeatherOffice

DESCRIPTION = """Script to estimate the % of headwing in a given GPX file"""


def parse_args() -> dict:
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--file-location",
        "-f",
        help="Location of the GPX file",
    )
    parser.add_argument(
        "--api-key",
        "-a",
        default=environ.get("MET_API_KEY"),
        help="API_KEY to query Weather Office. Looks up 'MET_API_KEY' in environment",
    )
    args = parser.parse_args()
    return args


async def main(test_file_location: str, api_key: str):
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
        f"The main wind direction tomorrow will be {wind_predictions[0].wind_direction.value} at "
        f"{wind_predictions[0].wind_speed} {wind_predictions[0].units}"
    )
    print(
        f"Your ride ({list_of_tracks[0].name}) will be facing this direction "
        f"{broad_direction_percentage} % of the time"
    )


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.file_location, args.api_key))
