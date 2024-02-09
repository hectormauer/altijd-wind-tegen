from math import atan2, degrees

from shapely import Point, STRtree, distance, get_point

from .data_types import CardinalDirection, TrackSegment

wind_directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def get_closest_weather_site(segment_centroid: Point, location_id_by_location: dict[Point, int]):
    tree = STRtree(list(location_id_by_location.keys()))
    return location_id_by_location[tree.geometries.take(tree.nearest(segment_centroid))]


def bearing_to_16_point_compass(bearing: float) -> CardinalDirection:
    if 348.75 < bearing <= 360 or 0 <= bearing <= 11.25:
        return "N"
    elif 11.25 < bearing <= 33.75:
        return "NNE"
    elif 33.75 < bearing <= 56.25:
        return "NE"
    elif 56.25 < bearing <= 78.75:
        return "ENE"
    elif 78.75 < bearing <= 101.25:
        return "E"
    elif 101.25 < bearing <= 123.75:
        return "ESE"
    elif 123.75 < bearing <= 146.25:
        return "SE"
    elif 146.25 < bearing <= 168.75:
        return "SSE"
    elif 168.75 < bearing <= 191.25:
        return "S"
    elif 191.25 < bearing <= 213.75:
        return "SSW"
    elif 213.75 < bearing <= 236.25:
        return "SW"
    elif 236.25 < bearing <= 258.75:
        return "WSW"
    elif 258.75 < bearing <= 281.25:
        return "W"
    elif 281.25 < bearing <= 303.75:
        return "WNW"
    elif 303.75 < bearing <= 326.25:
        return "NW"
    elif 326.25 < bearing <= 348.75:
        return "NNW"
    else:
        print(f"The following bearing is not understood: {bearing}")


def calculate_track_segment_bearings(track_segment: TrackSegment):
    total_length = 0
    for segment in track_segment.segments:
        p1 = get_point(segment.geom, 0)
        p2 = get_point(segment.geom, 1)
        bearing = atan2(p2.x - p1.x, p2.y - p1.y)
        normalised_bearing = (degrees(bearing) + 360) % 360
        segment.bearing = bearing_to_16_point_compass(normalised_bearing)
        segment.length = distance(p1, p2)
        total_length += segment.length
    track_segment.total_length = total_length


def get_broad_direction_percentace(wind_direction: str, bearing_by_percentage_of_segment: dict[str, float]) -> float:
    precedessor_wind_direction = wind_directions[wind_directions.index(wind_direction) - 1]
    try:
        successor_wind_direction = wind_directions[wind_directions.index(wind_direction) + 1]
    except IndexError:
        successor_wind_direction = wind_directions[0]
    return (
        bearing_by_percentage_of_segment[wind_direction]
        + bearing_by_percentage_of_segment[successor_wind_direction]
        + bearing_by_percentage_of_segment[precedessor_wind_direction]
    )
