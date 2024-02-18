from pathlib import Path

from altijd_wind_tegen.data_types import CardinalDirection, Track
from altijd_wind_tegen.geom_utils import bearing_to_16_point_compass
from altijd_wind_tegen.gpx_parser import parse

TEST_FILES_LOCATIONS = Path(__file__).parent / "test-files"


def test_parse_gpx():
    for file_name in TEST_FILES_LOCATIONS.glob("*.gpx"):
        for track in parse(file_name):
            assert track.name is not None
            assert track.track_segments


def test_bearing_to_cardinal_point():
    assert bearing_to_16_point_compass(348.75) == CardinalDirection.N
    assert bearing_to_16_point_compass(356) == CardinalDirection.N
    assert bearing_to_16_point_compass(11.24) == CardinalDirection.N
    assert bearing_to_16_point_compass(11.25) == CardinalDirection.NNE
    assert bearing_to_16_point_compass(21.25) == CardinalDirection.NNE
    assert bearing_to_16_point_compass(34) == CardinalDirection.NE
    assert bearing_to_16_point_compass(65.24) == CardinalDirection.ENE
    assert bearing_to_16_point_compass(100.24) == CardinalDirection.E
    assert bearing_to_16_point_compass(122.75) == CardinalDirection.ESE
    assert bearing_to_16_point_compass(140) == CardinalDirection.SE
    assert bearing_to_16_point_compass(180) == CardinalDirection.S
    assert bearing_to_16_point_compass(191.26) == CardinalDirection.SSW
    assert bearing_to_16_point_compass(215) == CardinalDirection.SW
    assert bearing_to_16_point_compass(258.74) == CardinalDirection.WSW
    assert bearing_to_16_point_compass(258.75) == CardinalDirection.W
    assert bearing_to_16_point_compass(270) == CardinalDirection.W
    assert bearing_to_16_point_compass(300) == CardinalDirection.WNW
    assert bearing_to_16_point_compass(311.56777) == CardinalDirection.NW
    assert bearing_to_16_point_compass(330) == CardinalDirection.NNW
    assert bearing_to_16_point_compass(348.74) == CardinalDirection.NNW
