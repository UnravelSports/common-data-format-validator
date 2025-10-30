# Auto-generated from JSON Schema v0.2.2
# Do not edit manually - run generate_latest_domain.py


from __future__ import annotations

from typing import List, Optional, TypedDict

from typing_extensions import NotRequired


class Match(TypedDict):
    id: str  # Unique identifier for the match


class Camera(TypedDict):
    x: NotRequired[
        Optional[float]
    ]  # x location of the camera in relation to the pitch center (m)
    y: NotRequired[
        Optional[float]
    ]  # y location of the camera in relation to the pitch center (m)
    z: NotRequired[
        Optional[float]
    ]  # z location of the camera in relation to the pitch center (m)


class Recording(TypedDict):
    fps: int  # Frames per second (i.e. frame rate) from vendor
    resolution: (
        str  # Resolution of the video in pixels (e.g., 3840x2160, 1920x1080, ...)
    )
    start_time: str  # The start time in UTC of the recording
    type: (
        str  # Information how the video was recorded (e.g. fixed camera, camcorder,...)
    )
    operation_type: (
        str  # Information whether the camera operation was manual or automated
    )
    perspective: str  # Camera angle (tactical_wide, camera_1, high_behind_right, high_behind_left, cable_camera, 16m_right, 16m_left, broadcast)
    camera: NotRequired[Camera]


class Whistle(TypedDict):
    type: str  # Whistles that start and end major periods of play such as the start and end of halves and interruptions
    sub_type: str  # Sub type related to an interruption, for example start or end
    time: str  # The time in UTC of the whistle
    video_time: int  # The time tag of the whistle in milliseconds


class VideoFootageCdfSchema(TypedDict):
    match: Match
    recording: Recording
    whistles: List[Whistle]
