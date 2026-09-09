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


class Player(TypedDict):
    id: str  # Unique identifier for a player
    x: float | None  # x location of the player on the pitch (m).
    y: float | None  # y location of the player on the pitch (m).
    z: NotRequired[float | None]  # z location of the player on the pitch (m).
    vel: NotRequired[float]  # Speed of the player/ball (m/s)
    acc: NotRequired[float]  # Acceleration of the player/ball (m/s^2)
    lat: NotRequired[
        float
    ]  # latitude of the player's position if the data is collected by GNSS or GPS
    long: NotRequired[
        float
    ]  # longitude of the player's position if the data is collected by GNSS or GPS
    is_visible: NotRequired[
        bool
    ]  # Denotes if a player was visible (in view of the camera) (true) or not (false)
    dist: NotRequired[
        float
    ]  # Distance covered by the player/ball in the current frame (m)


class Team(TypedDict):
    id: str  # Unique identifier for the home or away team
    players: list[Player]


class Teams(TypedDict):
    home: Team
    away: Team


class CdfTrackingDataSchema(TypedDict):
    frame_id: int  # Unique frame identifier
    timestamp: str  # Timestamp of the frame in UTC
    period: Literal[
        "first_half",
        "second_half",
        "first_half_extratime",
        "second_half_extratime",
        "shootout",
    ]  # Period of the match (first_half, second_half, first_half_extratime, second_half_extratime, shootout)
    match: Match
    teams: Teams
    ball: Ball
    officials: NotRequired[list[Official]]
