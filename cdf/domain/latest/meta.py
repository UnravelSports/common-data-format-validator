# Auto-generated from JSON Schema v0.3.2
# Do not edit manually - run src/generate_latest_domain.py


from __future__ import annotations

from typing import Literal, NotRequired, TypeAlias, TypedDict


class Competition(TypedDict):
    id: str  # Unique identifier for the competition
    name: NotRequired[str]  # Name of the competition
    format: NotRequired[
        str
    ]  # Specifying the competition set-up such as league_18 (i.e., league involving 18 teams), league_20, knock_out_neutral, etc.
    age_restriction: NotRequired[
        str
    ]  # Age restriction for the competition (e.g., 'U18', 'U20')
    type: NotRequired[str]  # Type of competition (e.g., 'youth', 'mens', 'womens')


class Season(TypedDict):
    id: str  # Unique identifier for the season
    name: NotRequired[str]  # Season name (e.g., '2022/23')


class Period(TypedDict):
    period: Literal[
        "first_half",
        "second_half",
        "first_half_extratime",
        "second_half_extratime",
        "shootout",
    ]  # Period of the match which can be first_half, second_half, first_half_extratime, second_half_extratime, or shootout
    play_direction: NotRequired[
        Literal["left_right", "right_left"]
    ]  # The direction of play for the home team. Possible options are left_right or right_left.
    start_time: NotRequired[str]  # Start time of the period in UTC
    end_time: NotRequired[str]  # End time of the period in UTC
    frame_id_start: NotRequired[
        int
    ]  # Frame identifier for the tracking data related to the start of the period
    frame_id_end: NotRequired[
        int
    ]  # Frame identifier for the tracking data related to the end of the period
    left_team_id: NotRequired[
        str
    ]  # Unique team identifier of the team playing on the left side of the pitch in this period. The CDF requires a standardized playing direction. The left_team_id and right_team_id should be the actual, non-standardized sides.
    right_team_id: NotRequired[
        str
    ]  # Unique team identifier of the team playing on the right side of the pitch in this period.


class Whistle(TypedDict):
    type: str  # Whistles that start and end major periods of play such as the start and end of halves and interruptions (e.g., weather, VAR review, player health events, streakers or abandoned). Examples of types first_half, second_half, weather_delay, health_delay, injury_treatment fan_health_delay etc.
    sub_type: str  # Sub type related to an interruption, for example 'start' or 'end'
    time: str  # The time in UTC of the whistle


class Misc(TypedDict):
    country: NotRequired[str]  # Country where the match is played
    city: NotRequired[str]  # City where the match is played
    is_open_roof: NotRequired[
        bool
    ]  # Indicates if the roof is open (true) or closed (false)
    precipitation: NotRequired[int]  # Precipitation during the match in millimetres


class Match(TypedDict):
    id: str  # Unique identifier for the match
    kickoff_time: str  # Scheduled kickoff time in UTC
    periods: list[Period]
    whistles: list[Whistle]  # Whistles that start and end major periods of play
    round: NotRequired[str]  # Round of the match (e.g. 1, 2, 3, final, semi_final)
    scheduled_kickoff_time: NotRequired[str]  # Scheduled kickoff time in UTC
    local_kickoff_time: NotRequired[str]  # Local kickoff time
    misc: NotRequired[Misc]


class Venue(TypedDict):
    id: str  # Unique identifier for the venue or stadium.
    pitch_length: NotRequired[
        float
    ]  # Length of the pitch in metres, null if not available
    pitch_width: NotRequired[
        float
    ]  # Width of the pitch in metres, null if not available
    name: NotRequired[str]  # Name of the venue or stadium
    turf: NotRequired[
        str
    ]  # Information on the turf of the stadium (natural, natural_reinforced, grass, clay,...)


class Video(TypedDict):
    perspective: str  # Camera perspective (e.g. 'in_stadium', 'broadcast', 'tactical', 'tactical_wide')
    version: str  # Version number for the video data collection in use (e.g. '0.1.0')
    name: str  # Vendor name of the video data
    fps: int  # Frames per second (i.e., frame rate) of tracking, landmark tracking or video


class Event(TypedDict):
    collection_timing: (
        str  # Indicates if the event data was collected 'live' or 'post_match'.
    )
    name: str  # Vendor name of the event data
    version: str  # Version number for the event data collection in use (e.g. '0.1.0')


class Tracking(TypedDict):
    version: (
        str  # Version number for the tracking data collection in use (e.g. '0.1.0')
    )
    name: str  # Vendor name of the tracking data
    fps: int  # Frames per second (i.e., frame rate) of tracking, landmark tracking or video
    collection_timing: (
        str  # Indicates if the tracking data was collected 'live' or 'post_match'.
    )


Joint: TypeAlias = str


class Connection(TypedDict):
    source: str  # Name of the parent landmark
    target: str  # Name of the child landmark


class Skeleton(TypedDict):
    root: str  # Name of the landmark the hierarchy is rooted at
    joints: list[Joint]  # Names of every landmark in the hierarchy
    connections: list[
        Connection
    ]  # Parent-child pairs describing how the landmarks connect


class Landmarks(TypedDict):
    version: (
        str  # Version number for the landmark data collection in use (e.g. '0.1.0')
    )
    name: str  # Vendor name of the landmark tracking data
    fps: int  # Frames per second (i.e., frame rate) of tracking, landmark tracking or video
    collection_timing: (
        str  # Indicates if the landmark data was collected 'live' or 'post_match'.
    )
    skeleton: Skeleton  # Skeletal hierarchy used: which landmarks are tracked and how they are connected. Required when landmark data is provided. Every name here is a landmark name from the landmark data.


class Ball(TypedDict):
    version: str  # Version number for the ball data collection in use (e.g. '0.1.0')
    name: str  # Vendor name of the ball data
    fps: int  # Frames per second (i.e., frame rate) of ball tracking
    collection_timing: (
        str  # Indicates if the ball data was collected 'live' or 'post_match'.
    )


class Meta1(TypedDict):
    version: str  # Version number for the data collection in use (e.g. '0.1.0')
    name: str  # Vendor name of the meta data


class Cdf(TypedDict):
    version: str  # Version number for the data collection in use (e.g. '0.1.0')


class Meta(TypedDict):
    video: Video | None  # Video meta data information, null if not relevant
    event: Event | None  # Event data meta information, null if not relevant
    tracking: Tracking | None  # Tracking data meta information, null if not relevant
    landmarks: (
        Landmarks | None
    )  # Landmark tracking data meta information, null if not relevant
    ball: (
        Ball | None
    )  # Ball tracking data meta information, null if not relevant. Only relevant when providing an independent ball file.
    meta: Meta1 | None  # Meta information
    cdf: Cdf | None  # Common Data Format (CDF) meta information


class Official(TypedDict):
    id: str  # Unique identifier for the official
    first_name: NotRequired[str]  # First name of the official, null if not available
    last_name: NotRequired[str]  # Last name of the official, null if not available
    short_name: NotRequired[str]  # Short name of the official, null if not available
    type: NotRequired[
        Literal[
            "main_referee",
            "fourth_official",
            "assistant_referee",
            "video_assistant_referee",
            "assistant_video_assistant_referee",
            "reserve_assistant_referee",
            "support_video_assistant_referee",
        ]
    ]  # Role of the official (e.g., 'main_referee', 'assistant_referee', 'fourth_official')


class Player(TypedDict):
    id: str  # Unique player identifier
    team_id: str  # Unique team identifier denoting the team the player plays for
    jersey_number: int  # Jersey number for a player
    is_starter: bool  # Denotes whether a player started the game (true) or not (false)
    last_name: NotRequired[str]  # Last name of the player, null if not available
    first_name: NotRequired[str]  # First name of the player, null if not available


class Team(TypedDict):
    id: str  # Unique identifier for the home or away team
    players: list[
        Player
    ]  # Array of player objects. One array under teams/home, one array under teams/away
    name: NotRequired[str]  # Name of the team
    jersey_colour: NotRequired[
        str
    ]  # Jersey colour of the team as a hexadecimal color code (e.g. #545B62).


class Teams(TypedDict):
    home: Team
    away: Team


class CdfMetaDataSchema(TypedDict):
    competition: Competition
    season: Season
    match: Match
    teams: Teams
    venue: Venue
    meta: Meta
    officials: NotRequired[list[Official]]
