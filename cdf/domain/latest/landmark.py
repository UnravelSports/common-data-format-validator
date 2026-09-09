# Auto-generated from JSON Schema v0.3.2
# Do not edit manually - run src/generate_latest_domain.py


from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


class Match(TypedDict):
    id: str  # Unique match identifier


class Ball(TypedDict):
    x: float | None  # x location of the ball on the pitch (m).
    y: float | None  # y location of the ball on the pitch (m).
    z: float | None  # z location of the ball on the pitch (m).
    status: NotRequired[
        bool
    ]  # Indicates if the ball is either in play (true) or out of play (false)
    poss_team_id: NotRequired[
        str
    ]  # Unique identifier of the team that currently possesses the ball
    poss_status: NotRequired[
        str
    ]  # Contextual description of the level of control (e.g., controlled, contested,...)


class Official(TypedDict):
    id: str  # Unique identifier for an official
    x: float | None  # x location of the official on the pitch (m)
    y: float | None  # y location of the official on the pitch (m)
    z: NotRequired[float | None]  # z location of the official on the pitch (m)
    vel: NotRequired[float]  # Speed of the official (m/s)
    acc: NotRequired[float]  # Acceleration of the official (m/s^2)
    lat: NotRequired[
        float
    ]  # Latitude of the official's position if the data is collected by GNSS or GPS
    long: NotRequired[
        float
    ]  # Longitude of the official's position if the data is collected by GNSS or GPS
    is_visible: NotRequired[
        bool
    ]  # Denotes if an official was visible (in view of the camera) (true) or not (false)


class Landmark(TypedDict):
    name: str  # Name for a landmark
    x: (
        float | None
    )  # Relative x coordinate of landmark in relation to the point of origin (m)
    y: (
        float | None
    )  # Relative y coordinate of landmark in relation to the point of origin (m)
    z: (
        float | None
    )  # Relative z coordinate of landmark in relation to the point of origin (m)
    is_visible: bool  # If landmark is detected (true) or inferred (false)


class Player(TypedDict):
    id: str  # Unique identifier for a player
    landmarks: list[Landmark]


class Team(TypedDict):
    id: str  # Unique identifier for the home or away team
    players: list[Player]


class Teams(TypedDict):
    home: Team
    away: Team


class CdfLandmarkTrackingDataSchema(TypedDict):
    frame_id: int  # Unique frame identifier
    timestamp: str  # Timestamp of the frame in UTC
    period: Literal[
        "first_half",
        "second_half",
        "first_half_extratime",
        "second_half_extratime",
        "shootout",
    ]  # Period of the match which can be first_half, second_half, first_half_extratime, second_half_extratime, or shootout
    match: Match
    teams: Teams
    ball: NotRequired[Ball]
    officials: NotRequired[list[Official]]
