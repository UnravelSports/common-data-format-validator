# Auto-generated from JSON Schema v0.2.2
# Do not edit manually - run generate_latest_domain.py


from __future__ import annotations

from typing import List, Literal, TypedDict

from typing_extensions import NotRequired


class Match(TypedDict):
    id: str  # Unique match identifier


class Ball(TypedDict):
    x: float
    y: float
    z: float


class Referee(TypedDict):
    id: str
    x: float
    y: float
    z: NotRequired[float]
    vel: NotRequired[float]
    acc: NotRequired[float]
    lat: NotRequired[float]
    long: NotRequired[float]
    is_visible: NotRequired[bool]
    minutes_played: NotRequired[float]


class Event(TypedDict):
    name: NotRequired[str]


class Tracking(TypedDict):
    name: NotRequired[str]


class Vendor(TypedDict):
    event: NotRequired[Event]
    tracking: NotRequired[Tracking]


class Landmark(TypedDict):
    index: str  # Unique identifier for a landmark
    name: str  # Name for a landmark
    x: float  # Relative x coordinate of landmark in relation to the point of origin (m)
    y: float  # Relative y coordinate of landmark in relation to the point of origin (m)
    z: float  # Relative z coordinate of landmark in relation to the point of origin (m)
    children: List[int]  # List of children indexes associated with keypoint
    is_visible: bool  # If landmark is detected (true) or inferred (false)


class Player(TypedDict):
    id: str  # Unique identifier for a player
    landmarks: List[Landmark]


class Team(TypedDict):
    id: str  # Unique identifier for the team
    players: List[Player]
    name: NotRequired[str]
    jersey_colour: NotRequired[str]
    formation: NotRequired[str]


class Teams(TypedDict):
    home: Team
    away: Team


class CdfSkeletalTrackingDataSchema(TypedDict):
    frame_id: int  # Unique frame identifier
    timestamp: str  # Timestamp of the frame in UTC
    period: Literal[
        "first_half",
        "second_half",
        "first_half_extratime",
        "second_half_extratime",
        "shootout",
    ]  # Period of the match
    match: Match
    teams: Teams
    ball: NotRequired[Ball]
    ball_status: NotRequired[bool]
    ball_poss_team_id: NotRequired[str]
    ball_poss_status: NotRequired[str]
    referees: NotRequired[List[Referee]]
    vendor: NotRequired[Vendor]
