# Auto-generated from JSON Schema v0.3.2
# Do not edit manually - run src/generate_latest_domain.py


from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


class Status(TypedDict):
    is_neutral: bool  # Denotes whether the game was hosted in a neutral venue (true) or not (false)
    has_extratime: (
        bool  # Denotes whether the game went to extra time (true) or not (false)
    )
    has_shootout: (
        bool  # Denotes whether the game had a penalty shootout (true) or not (false)
    )


class Final(TypedDict):
    home: int  # Result after the final whistle excluding penalty shootout goals (i.e. home goals, away goals)
    away: int  # Result after the final whistle excluding penalty shootout goals (i.e. home goals, away goals)
    winning_team_id: (
        str | None
    )  # Unique identifier of the winning team, null when the match was drawn and no shootout was played


class FirstHalf(TypedDict):
    home: int  # Result after the first half (i.e. home goals, away goals)
    away: int  # Result after the first half (i.e. home goals, away goals)


class SecondHalf(TypedDict):
    home: int  # Result after the second half (i.e. home goals, away goals)
    away: int  # Result after the second half (i.e. home goals, away goals)


class FirstHalfExtratime(TypedDict):
    home: int  # Result after the first half of extra time (i.e. home goals, away goals). Only required if a game goes to extra time.
    away: int  # Result after the first half of extra time (i.e. home goals, away goals). Only required if a game goes to extra time.


class SecondHalfExtratime(TypedDict):
    home: int  # Result after the second half of extra time (i.e. home goals, away goals). Only required if a game goes to extra time.
    away: int  # Result after the second half of extra time (i.e. home goals, away goals). Only required if a game goes to extra time.


class Shootout(TypedDict):
    home: int  # Score for the penalty shootout (i.e. home goals, away goals, shootout goals only). Only required if a game goes to shootout.
    away: int  # Score for the penalty shootout (i.e. home goals, away goals, shootout goals only). Only required if a game goes to shootout.


class Result(TypedDict):
    final: Final
    first_half: FirstHalf
    second_half: SecondHalf
    first_half_extratime: NotRequired[
        FirstHalfExtratime
    ]  # Required if has_extratime is true
    second_half_extratime: NotRequired[
        SecondHalfExtratime
    ]  # Required if has_extratime is true
    shootout: NotRequired[Shootout]  # Required if has_shootout is true


class Match(TypedDict):
    id: str  # Unique match identifier
    status: Status
    result: Result


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


class Score(TypedDict):
    home: int  # Team score after the goal
    away: int  # Team score after the goal


class Goal(TypedDict):
    time: str  # Time a player scored
    period: Literal[
        "first_half",
        "second_half",
        "first_half_extratime",
        "second_half_extratime",
        "shootout",
    ]  # Period of the game when the goal was scored
    team_id: str  # Identifier of the team that scored (for own goals this should be identifier of the team that gained a goal)
    player_id: str  # Identifier of the player who scored
    assist_id: (
        str | None
    )  # Identifier of the player who assisted, if the goal was assisted else leave as null.
    is_own_goal: bool  # Denotes whether it was an own goal (true) or not (false)
    is_penalty: bool  # Denotes whether it was a penalty (true) or not (false)
    score: Score


class Substitution(TypedDict):
    team_id: str  # Identifier of the team that made the substitution
    in_time: str  # Time in UTC a player is substituted in
    period: Literal[
        "first_half", "second_half", "first_half_extratime", "second_half_extratime"
    ]  # Period of the game when the substitution occurred
    in_player_id: str  # Unique identifier of the player substituted in
    out_time: str  # Time the player was substituted out
    out_player_id: str  # Identifier of the player that is substituted out


class Card(TypedDict):
    team_id: str  # Identifier of the team that made the received a card
    time: str  # Time in UTC a player received a card
    period: Literal[
        "first_half",
        "second_half",
        "first_half_extratime",
        "second_half_extratime",
        "shootout",
    ]  # Period of the game when the card was shown
    player_id: str  # Identifier of the player who received a card
    type: Literal[
        "yellow_card", "red_card", "second_yellow_card"
    ]  # Type of card which can be yellow_card, red_card or second_yellow_card


class Events(TypedDict):
    goals: list[Goal] | None
    substitutions: list[Substitution] | None
    cards: list[Card] | None


class Meta(TypedDict):
    vendor: str  # Match sheet data vendor name (e.g. "company_a")


class Player(TypedDict):
    id: str  # Unique player identifier
    first_name: str  # First name
    last_name: str  # Last name
    short_name: NotRequired[
        str
    ]  # Short name. For example "Mohamed Salah Hamed Mahrous Ghaly" as "Mo Salah" (or "Mohamed Salah") or "Givanildo Vieira de Sousa" as "Hulk".
    team_id: str  # Unique team identifier denoting the team the player plays for
    jersey_number: int  # Jersey number for a player
    is_starter: bool  # Denotes whether a player started the game (true) or not (false)
    has_played: bool  # Denotes whether a player played in game (true) or not (false)
    maiden_name: NotRequired[
        str
    ]  # Maiden name. For example, "Smith" for Sophia Wilson.
    position_group: NotRequired[
        Literal["GK", "DF", "MF", "FW", "SUB"]
    ]  # Position group acronym given according to the CDF-compatible groups
    position: NotRequired[
        Literal[
            "GK",
            "LB",
            "LCB",
            "CB",
            "RCB",
            "RB",
            "LDM",
            "CDM",
            "RDM",
            "LM",
            "LCM",
            "CM",
            "RCM",
            "RM",
            "LAM",
            "CAM",
            "RAM",
            "LW",
            "LCF",
            "CF",
            "RCF",
            "RW",
            "SUB",
        ]
    ]  # Position label acronym per player given according to the CDF-compatible labels
    is_captain: NotRequired[
        bool
    ]  # Whether the player is a captain (true) or not (false)
    date_of_birth: NotRequired[str]  # A player's date of birth in YYYY-MM-DD format
    height: NotRequired[int]  # Height of a player in cm
    foot: NotRequired[
        Literal["left", "right", "both"]
    ]  # A player's dominant foot, which can take the values left, right or both
    alternative_id: NotRequired[str]  # Additional identifier(s) of the player


class Coach(TypedDict):
    id: str  # Unique identifier for a coach
    first_name: str  # First name
    last_name: str  # Last name
    short_name: NotRequired[
        str
    ]  # Short name, a combination of First name and Last name


class Team(TypedDict):
    id: str  # Unique identifier for the home or away team
    short_name: NotRequired[str]  # Short name of the home or away team
    formation: NotRequired[str]  # Formation label of the team (e.g. '4-4-2')
    players: list[Player]
    coaches: NotRequired[list[Coach]]


class Teams(TypedDict):
    home: Team
    away: Team


class CdfOfficialMatchData(TypedDict):
    match: Match
    teams: Teams
    officials: list[Official]
    events: Events
    meta: Meta
