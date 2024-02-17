from math import atan2, degrees

from shapely import Point, STRtree, distance, get_point

from .data_types import CardinalDirection, TrackSegment, normalised_cardinal_direction_map


def get_closest_weather_site(segment_centroid: Point, location_id_by_location: dict[Point, int]):
    tree = STRtree(list(location_id_by_location.keys()))
    return location_id_by_location[tree.geometries.take(tree.nearest(segment_centroid))]

def bearing_to_16_point_compass(bearing: float) -> str:
    return normalised_cardinal_direction_map[int(((bearing + 11.25) % 360) / 22.5)]

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
    wind_directions = list(CardinalDirection)
    predecessor_wind_direction = wind_directions[wind_directions.index(wind_direction) - 1]
    try:
        successor_wind_direction = wind_directions[wind_directions.index(wind_direction) + 1]
    except IndexError:
        successor_wind_direction = wind_directions[0]
    return (
        bearing_by_percentage_of_segment[wind_direction]
        + bearing_by_percentage_of_segment[successor_wind_direction]
        + bearing_by_percentage_of_segment[predecessor_wind_direction]
    )
