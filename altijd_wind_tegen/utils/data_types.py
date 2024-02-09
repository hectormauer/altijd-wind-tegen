from collections import defaultdict
from dataclasses import dataclass, field
from typing import Literal

from dataclasses_json import DataClassJsonMixin, config
from shapely import LineString, Point

target_epsg = "epsg:27700"  # TODO this should be configurable, by fetching the gpx location.
source_epsg = "epsg:4326"

CardinalDirection = Literal[
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
]


@dataclass
class DailyWindPrediction(DataClassJsonMixin):
    # There are many values. We just want the wind related
    wind_direction: str = field(metadata=config(field_name="D"))
    wind_speed: str = field(metadata=config(field_name="S"))
    wind_gust_noon: str | None = field(default=None, metadata=config(field_name="Gn"))
    wind_gust_midnight: str | None = field(default=None, metadata=config(field_name="Gm"))
    units: str = "mph"
    am_or_pm: Literal["am", "pm"] = field(init=False)

    def __post_init__(self):
        self.am_or_pm = "am" if self.wind_gust_noon else "pm"


@dataclass
class Segment:
    geom: LineString
    bearing: CardinalDirection = field(init=False)
    length: float = field(init=False)


@dataclass
class TrackSegment:
    segments: list[Segment]
    crs: str = "epsg:27700"
    total_length: float | None = None

    @property
    def get_centroid(self) -> Point:
        # This will get a lot of repeated coordinates
        return LineString([coord for segment in self.segments for coord in segment.geom.coords]).centroid

    @property
    def bearing_by_percentage_of_length(self) -> dict[CardinalDirection, float]:
        dict_ = defaultdict(float)
        for segment in self.segments:
            dict_[segment.bearing] += round((segment.length / self.total_length) * 100, 2)
        return dict_


@dataclass
class Track:
    name: str
    track_segments: list[TrackSegment]
