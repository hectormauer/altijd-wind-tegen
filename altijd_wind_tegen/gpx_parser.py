"""Simple and naive implementation to just extract the coordinates and elevation from the track points"""
import xml.etree.ElementTree as ET
from datetime import datetime
from xml.etree.ElementTree import Element

from pyproj import Transformer
from shapely import LineString, Point

from .data_types import Segment, Track, TrackSegment, source_epsg, target_epsg

# TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

GPX_NAMESPACE = {"topo": "http://www.topografix.com/GPX/1/1"}

transformer = Transformer.from_crs(source_epsg, target_epsg)


def get_text(element, sub_element: str) -> str | None:
    try:
        text_ = element.get(sub_element)
    except:
        print(f"{element} has no attribute {sub_element}.")
        text_ = None
    return text_


def find_text(element, sub_element) -> str | None:
    try:
        name = element.find(sub_element, GPX_NAMESPACE).text
    except:
        print(f"{element} has no attribute {sub_element}.")
        name = None
    return name


def get_float(element: Element, sub_element: str) -> float | None:
    try:
        float_ = float(element.get(sub_element))
    except:
        print(f"{element} has no attribute {sub_element}.")
        float_ = None
    return float_


def find_float(element, sub_element: str) -> float | None:
    try:
        float_ = float(element.find(sub_element, GPX_NAMESPACE).text)
    except:
        float_ = None
        print(f"{element} has no attribute {sub_element}.")
    return float_


def find_time(element: Element, sub_element: str) -> datetime | None:
    try:
        time_ = datetime.strptime(element.find(sub_element, GPX_NAMESPACE).text, TIME_FORMAT)
    except:
        time_ = None
        print(f"{element} has no attribute {sub_element}.")
    return time_


def parse_track_point(track_point) -> Point | None:
    if track_point is None:
        return None

    latitude = get_float(track_point, "lat")
    longitude = get_float(track_point, "lon")
    elevation = find_float(track_point, "topo:ele")
    x, y, z = transformer.transform(latitude, longitude, elevation)
    return Point(x, y, z)


def parse_track_segment(track_segment: Element) -> TrackSegment | None:
    if track_segment is None:
        return None

    list_of_trackpoints = []
    track_points = track_segment.findall("topo:trkpt", GPX_NAMESPACE)
    for track_point in track_points:
        list_of_trackpoints.append(parse_track_point(track_point))
    list_of_segments = []
    for point_1, point_2 in zip(list_of_trackpoints[:-1], list_of_trackpoints[1:]):
        list_of_segments.append(Segment(geom=LineString([point_1, point_2])))
    return TrackSegment(list_of_segments)


def parse_track(name: str, track: Element) -> Track:
    list_of_track_segments = []
    segments = track.findall("topo:trkseg", GPX_NAMESPACE)
    for segment in segments:
        list_of_track_segments.append(parse_track_segment(segment))
    return Track(name, list_of_track_segments)


# def parse_metadata(self, metadata, tag: str = "metadata") -> Metadata | None:
#     """
#     Parse metadataType element from GPX file.

#     Args:
#         metadata (xml.etree.ElementTree.Element): Parsed metadata element.
#         tag (str, Optional): XML tag. Defaults to "metadata".

#     Returns:
#         Metadata: Metadata instance.
#     """
#     if metadata is None:
#         return None

#     name = self.find_text(metadata, "topo:name")
#     desc = self.find_text(metadata, "topo:desc")
#     author = self.parse_person(metadata.find("topo:author", self.name_space))
#     copyright = self.parse_copyright(metadata.find("topo:copyright", self.name_space))
#     link = self.parse_link(metadata.find("topo:link", self.name_space))
#     time = self.find_time(metadata, "topo:time")
#     keywords = self.find_text(metadata, "topo:keywords")
#     bounds = self.parse_bounds(metadata.find("topo:bounds", self.name_space))
#     extensions = self.parse_extensions(metadata.find("topo:extensions", self.name_space))

#     return Metadata(tag, name, desc, author, copyright, link, time, keywords, bounds, extensions)


def parse(file_path: str) -> list[Track]:
    tracks_list = []
    xml_tree = ET.parse(file_path)
    xml_root = xml_tree.getroot()

    metadata = xml_root.find("topo:metadata", GPX_NAMESPACE)
    name = find_text(metadata, "topo:name")

    tracks = xml_root.findall("topo:trk", GPX_NAMESPACE)
    for track in tracks:
        tracks_list.append(parse_track(name, track))

    return tracks_list
