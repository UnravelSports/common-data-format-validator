# Auto-generated from JSON Schema v0.3.1
# Do not edit manually - run generate_latest_domain.py


from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


class Match(TypedDict):
    id: str


class Ball(TypedDict):
    x: float | None
    y: float | None
    z: float | None
    status: NotRequired[bool]
    poss_team_id: NotRequired[str]
    poss_status: NotRequired[str]


class Official(TypedDict):
    id: str
    x: float | None
    y: float | None
    z: NotRequired[float | None]
    vel: NotRequired[float]
    acc: NotRequired[float]
    lat: NotRequired[float]
    long: NotRequired[float]
    is_visible: NotRequired[bool]


class Event(TypedDict):
    name: NotRequired[str]


class Tracking(TypedDict):
    name: NotRequired[str]


class Vendor(TypedDict):
    event: NotRequired[Event]
    tracking: NotRequired[Tracking]


class Player(TypedDict):
    id: str
    x: float | None
    y: float | None
    z: NotRequired[float | None]
    vel: NotRequired[float]
    acc: NotRequired[float]
    lat: NotRequired[float]
    long: NotRequired[float]
    is_visible: NotRequired[bool]


class Team(TypedDict):
    id: str
    players: list[Player]
    name: NotRequired[str]
    jersey_colour: NotRequired[str]
    formation: NotRequired[str]


class Teams(TypedDict):
    home: Team
    away: Team


class CdfTrackingDataSchema(TypedDict):
    frame_id: int
    timestamp: str
    period: Literal[
        "first_half",
        "second_half",
        "first_half_extratime",
        "second_half_extratime",
        "shootout",
    ]
    match: Match
    teams: Teams
    ball: Ball
    officials: NotRequired[list[Official]]
    vendor: NotRequired[Vendor]
