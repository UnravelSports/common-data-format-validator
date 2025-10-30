# Auto-generated from JSON Schema v0.2.2
# Do not edit manually - run generate_latest_domain.py


from __future__ import annotations

from typing import List, Literal, Optional, TypedDict

from typing_extensions import NotRequired


class Match(TypedDict):
    id: str  # Unique match identifier


class Meta(TypedDict):
    is_synced: (
        bool  # Indicates if synced tracking data is available (true) or not (false)
    )


class Metrics(TypedDict):
    xg: NotRequired[Optional[float]]  # Calculated xG value between [0,1]
    post_shot_xg: NotRequired[
        Optional[float]
    ]  # Calculated post-shot xG value between [0,1]
    xpass: NotRequired[Optional[float]]  # Calculated xPass value between [0,1]
    epv: NotRequired[Optional[float]]  # Expected possession value between [-1,1]
    packing_traditional: NotRequired[
        Optional[int]
    ]  # Number of opposing players that have been outplayed by a pass according to the traditional packing approach
    packing_horizontal: NotRequired[
        Optional[int]
    ]  # Number of opposing players that have been outplayed by a pass according to the horizontal packing approach


class Var(TypedDict):
    reviewed: NotRequired[
        bool
    ]  # Was this event reviewed by the video assistant referee (true) or not (false
    upheld: NotRequired[
        bool
    ]  # Was the ruling on the field confirmed (true) or not (false)


class Event(TypedDict):
    id: str  # Unique identifier of the event
    time: str  # Absolute time in UTC of when the event started
    period: Literal[
        "first_half",
        "second_half",
        "first_half_extratime",
        "second_half_extratime",
        "shootout",
    ]
    type: str  # Name of the event type
    sub_type: Optional[str]  # Name of the event subtype
    is_successful: (
        bool  # Denotes whether the event was successful (true) or not (false)
    )
    outcome_type: str  # Detailed event outcome options
    player_id: str  # Unique identifier of the player performing the action
    team_id: str  # Unique team identifier of the player performing the action
    receiver_id: Optional[
        str
    ]  # Unique identifier of the player receiving a pass, leave null if event is not a pass
    receiver_time: Optional[
        str
    ]  # Absolute time in UTC of the first moment the ball was received
    x: float  # x location where the action of player_id happened (m)
    y: float  # y location where the action of player_id happened (m)
    x_end: float  # x location where the action of player_id ended (m)
    y_end: float  # y location where the action of player_id ended (m)
    body_part: Literal[
        "left_foot", "right_foot", "head", "other"
    ]  # Denotes the body part used by player_id
    related_event_ids: Optional[
        List[str]
    ]  # Unique identifier(s) of the events related to the action
    match_clock: NotRequired[str]  # The match clock as a string in format MM:SS.mm
    metrics: NotRequired[Optional[Metrics]]
    var: NotRequired[Optional[Var]]


class Player(TypedDict):
    x: NotRequired[
        float
    ]  # x location of the player committing the action according to the tracking data
    y: NotRequired[
        float
    ]  # y location of the player committing the action according to the tracking data


class Tracking(TypedDict):
    frame_id: NotRequired[
        Optional[int]
    ]  # Frame identifier from the tracking data related to the event at (x, y)
    frame_id_end: NotRequired[
        Optional[int]
    ]  # Frame identifier from the tracking data related to the event at (x_end, y_end)
    player: NotRequired[Player]


class Model(TypedDict):
    match: Match
    meta: Meta
    event: Event
    tracking: NotRequired[Tracking]
