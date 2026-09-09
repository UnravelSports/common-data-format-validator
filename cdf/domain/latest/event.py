# Auto-generated from JSON Schema v0.3.2
# Do not edit manually - run src/generate_latest_domain.py


from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


class Match(TypedDict):
    id: str  # Unique match identifier


class Meta(TypedDict):
    is_synced: bool  # Indicates if synced tracking data is available (true) or not (false) for this event


class Metrics(TypedDict):
    xg: NotRequired[float]  # Calculated xG value between [0,1]
    post_shot_xg: NotRequired[float]  # Calculated post-shot xG value between [0,1]
    xpass: NotRequired[float]  # Calculated expected pass value between [0,1]
    epv: NotRequired[float]  # Expected possession value between [0,1]


class Var(TypedDict):
    reviewed: NotRequired[
        bool
    ]  # Was this event reviewed by the video assistant referee (true) or not (false)
    upheld: NotRequired[
        bool
    ]  # Was the on-field ruling confirmed (true) or overturned (false)


class Event(TypedDict):
    id: str  # Unique identifier of the event
    time: str  # Absolute time in UTC of when the event started (e.g., moment the pass is given, the moment the ball leaves the hands on a thrown in)
    period: Literal[
        "first_half",
        "second_half",
        "first_half_extratime",
        "second_half_extratime",
        "shootout",
    ]  # Period of the match which can be first_half, second_half, first_half_extratime, second_half_extratime, or shootout
    type: str  # Name of the event type (e.g. shot, pass, referee, defending, goalkeeping, misc etc.)
    sub_type: (
        str | None
    )  # Name of the event sub type, which can be for shot - (penalty_kick, free_kick, corner_kick etc.); pass - (throw_in, free_kick, corner_kick, goal_kick, kick_off etc.); referee - (final_whistle, foul, caution, offside, substitution, player_on, player_off. Player on and player off events occur for example when a player has to abandon the game due to a lack of available substitutions, or as a temporary measure after a medical check); defending - (clearance, interception, pressing, block etc.); goalkeeping - (save, save_attempt, claim, etc.); misc - (other_ball_action, chance_without_shot, tackle, etc.)
    is_successful: (
        bool  # Denotes whether the event was successful (true) or not (false)
    )
    outcome_type: str  # Event outcome options: shot - (successful, saved, blocked, wide, woodwork, own_goal); pass - (e.g. successful, out_of_play, intercepted); referee - (start, end, injury, offside, yellow_card, red_card or second_yellow_card); defending - (e.g. clearance, block, interception, pressure); goalkeeping (e.g. save, save_attempt, claim); misc - (e.g. successful, unsuccessful)
    player_id: NotRequired[
        str
    ]  # Unique identifier of the player performing the action. For example, player committing a pass, or making a tackle. Required for all non-referee events. Referee events require event/official_id.
    team_id: NotRequired[
        str
    ]  # Unique team identifier of the player performing the action. Required for all non-referee events. Referee events require event/official_id.
    official_id: NotRequired[
        str
    ]  # Unique identifier of the official performing the action. Mandatory only when type is referee, else use event/player_id and event/team_id
    receiver_id: (
        str | None
    )  # Unique identifier of the player receiving a pass. Leave null when the event is not a pass or when the pass has no receiver.
    receiver_time: (
        str | None
    )  # Absolute time in UTC of the first moment the ball was received. Leave null when the event is not a pass or when the pass has no receiver.
    receiver_team_id: (
        str | None
    )  # Unique team identifier of the player identified by receiver_id, leave null if the event does not end with a known player in possession
    x: float  # x location where the action of player_id happened (m).
    y: float  # y location where the action of player_id happened (m).
    x_end: (
        float | None
    )  # x location where the action of player_id ended (m), null for single-point events that have no end coordinate.
    y_end: (
        float | None
    )  # y location where the action of player_id ended (m), null for single-point events that have no end coordinate.
    body_part: (
        Literal[
            "left_foot",
            "right_foot",
            "feet",
            "head",
            "hands",
            "upper_body",
            "lower_body",
            "body",
            "other",
        ]
        | None
    )  # Denotes the body part used by player_id, null allowed for events other than pass and shot.
    related_event_ids: (
        list[str] | None
    )  # Unique identifier(s) of the events related to the action, or pass and associated receival event. For example, a related aerial duel event or the player_off event associated with a player_on event. Leave null if no related events exist.
    match_clock: NotRequired[
        str
    ]  # The match clock as a string in format "MM:SS.mm" (i.e. minutes, seconds, milliseconds) (e.g. "92:01.04"). The clock resets to "45:00.00", "90:00.00" or "105:00.00" at the start of "second_half", "first_half_extratime", "second_half_extratime", respectively.
    metrics: NotRequired[Metrics]
    var: NotRequired[Var]


class Player(TypedDict):
    x: NotRequired[
        float
    ]  # x location of the player committing an event according to the tracking data. For example, player committing a pass, or making a tackle (m)
    y: NotRequired[
        float
    ]  # y location of the player committing an event according to the tracking data. For example, player committing a pass, or making a tackle (m)


class Tracking(TypedDict):
    frame_id: NotRequired[
        int
    ]  # Frame identifier from the tracking data related to the event at (x, y)
    frame_id_end: NotRequired[
        int
    ]  # Frame identifier from the tracking data related to the event at (x_end, y_end)
    player: NotRequired[Player]


class CdfEventDataSchema(TypedDict):
    match: Match
    meta: Meta
    event: Event
    tracking: NotRequired[Tracking]
