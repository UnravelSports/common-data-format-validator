# Changelog

This changelog references Anzer et al. 2025. The changelog is structured to follow this papers' structure. As a result, the changelog address changes per table.

Each table in the paper discusses mandatory and optional Match Sheet, Video Footage, Event, Tracking, Skeletal and Meta data.

--

## 🗒️ Changelog v0.3.0 (alpha) - Friday 21st August 2026

---

### General

- Within the CDF, "skeletal" has been replaced with "landmark". Added `LandmarkSchemaValidator` as a pass-through of `SkeletalSchemaValidator`, and deprecated `SkeletalSchemaValidator` (it now emits a `DeprecationWarning` pointing to `LandmarkSchemaValidator`).
- Tracking and Skeletal validators now check, when validating a full file (`limit=None`), that `frame_id` is a monotonically increasing unique integer starting at 0.
- `validate_schema` gained a `mode` argument (`"soft"`, `"strict"`, `"extreme"`) replacing the boolean `soft` (still accepted but deprecated). Unknown / undefined keys are now reported with a "did you mean?" suggestion: as warnings in `"soft"` and `"strict"`, and as errors in `"extreme"`.
- All validators now check that every `date-time` field is a well-formed RFC 3339 UTC timestamp (trailing `Z` or `+00:00`), except `match/local_kickoff_time` which is intentionally local. This covers tracking/skeletal `timestamp`, event `time`/`receiver_time`, meta `kickoff_time`/`scheduled_kickoff_time`/`periods` times/`whistles` times, match goal/substitution/card times, and video `recording/start_time`/`whistles` times.
- Timestamp chronology checks: meta `match/periods` and `match/whistles` timestamps must be chronological, and tracking/skeletal per-frame `timestamp` must be non-decreasing across a full file (`limit=None`), alongside the existing `frame_id` check.
- Values of `receiver_id` and `receiver_team_id` are no longer checked for snake_case, matching `team_id` and `player_id`.
- The renames in this release are breaking and have no automatic migration: an old key is reported as an unknown field and the new one as a missing required property.

---

### Meta Data

#### Table 6. Mandatory Meta Data

- Added `meta/event/name` with description "Vendor name of the event data"
- Added `meta/event/version` with description "Version number for the event data collection in use (e.g. '0.1.0')"
- Changed `match/periods/{i}/play_direction` from Mandatory to Optional for the `shootout` period only (it remains Mandatory for all other period types)
- Renamed `stadium` to `venue` 
- Renamed `match/periods/{i}/time_start` to `match/periods/{i}/start_time`
- Renamed `match/periods/{i}/time_end` to `match/periods/{i}/end_time`

#### Table 10. Optional Meta Data

- Added `teams/{home|away}/players/{i}/first_name` (String, _null_ if not available)
- Added `teams/{home|away}/players/{i}/last_name` (String, _null_ if not available)
- Added `officials` list. Each `officials/{i}` requires `id`, and optionally carries `first_name` (String, _null_ if not available), `last_name` (String, _null_ if not available), `short_name` (String, _null_ if not available) and `type`
- Constrained `officials/{i}/type` to an enum: `main_referee`, `fourth_official`, `assistant_referee`, `video_assistant_referee`, `assistant_video_assistant_referee`, `reserve_assistant_referee`, `support_video_assistant_referee`

---

### Match Sheet Data

#### Table 1. Mandatory Match Sheet Data

- Renamed `referees` to `officials`
- Renamed `officials/{i}/official_type` to `officials/{i}/type`
- Constrained `officials/{i}/type` to the same enum used in Meta (it was an unconstrained String)
- Changed `officials/{i}/first_name`, `officials/{i}/last_name` and `officials/{i}/short_name` to (String, _null_ if not available), matching Meta
- Added `shootout` to the `events/cards/{i}/period` enum (`events/substitutions/{i}/period` deliberately excludes it)
- Changed the `match/result` extra time and shootout blocks to be required only when `match/status/has_extratime` / `match/status/has_shootout` are true (previously required on every match)
- Removed the root-level `version` key (the version is stated in the schema description)

---

### Event Data

#### Table 3. Mandatory Event Data

- Changed the `body_part` enum to add `hands`, `upper_body` and `lower_body`
- Changed `x_end` and `y_end` to (Float, _null_ for single-point events that have no end coordinate)
- Constrained `x_end` and `y_end` to a Float when `type` is `pass` or `shot`
- Added `receiver_team_id` (String, _null_ if not available) with description "Unique team identifier of the player identified by receiver_id"
- Changed `receiver_id` and `receiver_time` to be permitted on any event ending with a known player in possession (they were documented as pass-only)

---

### Tracking Data

#### Table 10. Optional Tracking Data

- Renamed `referees` to `officials`
- Removed `teams/{home|away}/players/{i}/minutes_played` (a cumulative match statistic that does not belong in per-frame tracking data)
- Removed `officials/{i}/minutes_played`
- Moved `ball_status` into `ball` and renamed it to `ball/status`
- Moved `ball_poss_team_id` into `ball` and renamed it to `ball/poss_team_id`
- Moved `ball_poss_status` into `ball` and renamed it to `ball/poss_status`

---

### Skeletal Data

#### Table 5. Mandatory Skeletal Data

- Renamed `referees` to `officials`
- Removed `officials/{i}/minutes_played`
- Moved `ball_status` into `ball` and renamed it to `ball/status`
- Moved `ball_poss_team_id` into `ball` and renamed it to `ball/poss_team_id`
- Moved `ball_poss_status` into `ball` and renamed it to `ball/poss_status`

---

## 🗒️ Changelog v0.2.3 (alpha) - Wednesday 18th March 2026

---

### Mandatory Tracking Data

#### Table 4. Mandatory Tracking Data

- Added `"type": "object"` to `team` definition (consistency fix)

### Mandatory Skeletal Data

#### Table 5. Mandatory Skeletal Data

- Changed `ball/x`, `ball/y`, `ball/z` from Mandatory to Optional (to accommodate missing data as `None`; these fields remain **explicitly required** in practice)
- Changed `referee/x`, `referee/y`, `referee/z` from Mandatory to Optional (to accommodate missing data as `None`)

---

## 🗒️ Changelog v0.2.2 (alpha) - October 30th 2025

---

### Mandatory Tracking Data

#### Table 4. Mandatory Tracking Data

- Changed `player/x`, `player/y`, `player/z` from Mandatory to Optional (to accommodate missing data as `None`; these fields remain **explicitly required** in practice)
- Changed `ball/x`, `ball/y`, `ball/z` from Mandatory to Optional (to accommodate missing data as `None`; these fields remain **explicitly required** in practice)
- Changed `referee/x`, `referee/y`, `referee/z` from Mandatory to Optional (to accommodate missing data as `None`; these fields remain **explicitly required** in practice)
- Clarified that `teams/home/id` and `teams/away/id` are **strictly required** for each frame
- Clarified that `teams/home/players` and `teams/away/players` lists are **strictly required** for each frame

---

### Meta Data

#### Table 6. Mandatory Meta Data

- Renamed all references from "limb" to "landmarks" (terminology update across meta schema)

---

## 🗒️ Changelog v0.2.1 (alpha) - June 17th 2025

### General

- Added table "Optional Video Data" to the Appendix (B.2.). This means all table numbers after this are now shifted by 1 (e.g. Optional Event Data was Table 8, it is now Table 9).

### Match Sheet Data

#### Table 1. Mandatory Match Sheet Data

No changes

#### Table 7. Optional Match Sheet Data

No changes

---

### Video Footage Data

#### Table 2. Mandatory Video Footage Data

- Removed `recording/location/x`
- Removed `recording/location/y`
- Removed `recording/location/z`

#### Table 8. Optional Video Footage Data

- Created this table in the Appendix
- Added `recording/location/x`
- Added `recording/location/y`
- Added `recording/location/z`

---

### Mandatory Event Data

#### Table 3. Mandatory Event Data

- Renamed `event/outcome` to `event/is_successful`
- Renamed `event/outcome_detailed` to `event/outcome_type`
- Changed description of `receiver_id` to "Unique identifier of the player receiving a pass. Leave _null_ when the event is not a pass **or when the pass has no receiver.**"
- Changed description of `receiver_time` to "Absolute time in UTC of the first moment the ball was received. Leave _null_ when the event is not a pass **or when the pass has no receiver.**"

#### Table 9. Mandatory Event Data

- Changed to Table 9.

---

### Mandatory Tracking Data

In Section 5.2: "Every period starts with frame = 0" is changed to "Frame identifiers should be monotonically increasing unique integers starting at 0."

#### Table 4. Mandatory Tracking Data

- Added the field `timestamp` with description "Timestamp of the frame in UTC."

#### Table 10. Optional Tracking Data

- Changed to Table 10.

---

### Mandory Skeletal Data

### Table 5. Mandory Skeletal Data

- Added the field `timestamp` with description "Timestamp of the frame in UTC."
- Changed Description of `teams/{home|away}/players/{i}/landmarks/{j}/name` to "Name for a landmark".
- Changed Type of `is_visible` to Boolean.
- Changed Description of `is_visible` to " If landmark is detected (i.e., not occluded) or inferred (false)"

---

### Meta Data

#### Table 6. Mandatory Meta Data

- Renamed `meta/limb` to `meta/landmarks`
- Renamed `meta/{event|tracking|video|limb|ball|meta|cdf}` to `meta/{event|tracking|video|landmarks|ball|meta|cdf}`
- Renamed `meta/{event|tracking|video|limb|ball|meta}` to `meta/{event|tracking|video|landmarks|ball|meta}`
- Renamed `meta/{tracking|video|limb|ball}` to `meta/{tracking|video|landmarks|ball}`
- Renamed `meta/{event|tracking|limb|ball}` to `meta/{event|tracking|landmarks|ball}`
- Updated `meta/{event|tracking|video|landmarks|ball|meta|cdf}` to include "event"
- Updated `meta/{event|tracking|video|landmarks|ball|meta}` to include "event"

#### Table 10. Optional Meta Data

---

## 🗒️  Changelog v0.2.0 (alpha) - April 29th 2025

### Match Sheet Data

---

**match**

- `match/result/final/winning_team_id` is of type String
- `match/result/first_extratime` is renamed to `match/result/first_half_extratime`
- `match/result/second_extratime` is renamed to `match/result/second_half_extratime`

**events/goals**

- `events/goals` can now be `null`
- `events/goals/{i}/goal_time` is:
  - renamed to `events/goals/{i}/time`.
  - recorded in UTC.
- `events/goals/{i}/goal_player_id` is renamed to `events/goals/{i}/player_id`
- `events/goals/{i}/goal_assist_id` is renamed to `events/goals/{i}/assist_id`
- `events/goals/{i}/score/{home|away}` is added as two Integer fields describing the score after the goal.
- `events/goals/{i}/team_id` is added. It denotes the unique team identifier of the player that score. In the event of an own goal, it denotes the goal of the team that gained a goal.
- `events/goals` shall be `null` if a game ends 0-0.

**events/substitutions**

- `events/substitutions/{i}/in_time` is recorded in UTC.
- `events/substitutions/{i}/out_time` is recorded in UTC.
- `events/substitutions/{i}/team_id` It denotes the unique team identifier of the team that made the substitution.

**events/cards**

- `events/cards/{i}/card_time` is:
  - renamed to `events/cards/{i}/time`.
  - recorded in UTC.
- `events/cards/{i}/card_player_id` is renamed to `events/cards/{i}/player_id`
- `events/cards/{i}/card_type` is renamed to `events/cards/{i}/type`
- `events/cards/{i}/team_id` It denotes the unique team identifier of the team that received the card.

#### Table 7. Optional Match Sheet Data

- `teams/{home|away}/players/{i}/date_of_birth` description changed to: "A player's data of birth in YYYY-MM-DD format*".
- `teams/(home|away)/coaches/{i}/coach_id` renamed to `teams/(home|away)/coaches/{i}/id`
- `teams/(home|away)/coaches/{i}/short_name` description changed to "Short name, a combination of First name (first) and Last name (e.g. Jane Doe, **not** J. Doe)"

---

### Video Footage Data

#### Table 2. Mandatory Video Footage Data

- `match_id` is renamed to `match/id`.
- `fps` is renamed to `recording/fps`.
- `resolution` is renamed to `recording/resolution`.
- `start_time` is renamed to `recording/start_time`.
- `operation_type` is renamed to `recording/operation_type`.
- `recording_type` is renamed to `recording/type`.
- `perspective`  is renamed to `recording/perspective`.
- `camera_location_x` is:
  - Renamed to `recording/camera/x`
  - Type changed from `Integer` to `Float`
- `camera_location_y` is:
  - Renamed to `recording/camera/y`
  - Type changed from `Integer` to `Float`
- `camera_location_z`is:
  - Renamed to `recording/camera/z`
  - Type changed from `Integer` to `Float`

---

### Mandatory Event Data

#### Table 3. Mandatory Event Data

- `event/type` description changed to: "Name of the event type _(e.g. shot, pass, referee, misc etc.)_"
- `event/outcome_detailed` description changed to: "[...] pass - (_e.g._ successful, out_of_play, intercepted) [...]"
- `event/related_event_ids` shall be `null` if no related events exist.

#### Table 8. Mandatory Event Data

- `tracking/frame_end_id` renamed to `tracking/frame_id_end`.
- `tracking/x_player` renamed to `tracking/player/x`
- `tracking/y_player` renamed to `tracking/player/y`
- `event/metrics/expected_poss_value` renamed to `event/metrics/epv`
- `event/var/reviewed` is:
  - changed to type Boolean.
  - description changed to: "Was this event reviewed by the video assistant referee (true) or not (false)"
- `event/var/upheld` is:
  - changed to type Boolean.
  - description changed to: "Was the on-field ruling confirmed (true) or overturned (false)"

---

### Mandatory Tracking Data

#### Table 4. Mandatory Tracking Data

- `period` description changed to: "Period of the match (first_half, second_half, _first_half_extratime_, _second_half_extratime_, shootout)"

#### Table 9. Optional Tracking Data

- `vendor/event` and `vendor/tracking` renamed to `vendor/{event|tracking}/name`
- `teams/{home|away}/jersey_colour` description changed to reflect British spelling ("Jersey colour")

---

### Mandory Skeletal Data

### Table 5. Mandory Skeletal Data

No changes.

---

### Meta Data

#### Table 6. Mandatory Meta Data

- `match/periods/{i}/period` renamed to `match/periods/{i}/type`.
- `stadium/pitch_length` description changed to: "Length of the pitch (m), _null_ if not available."
- `stadium/pitch_width` description changed to: "Width of the pitch (m), _null_ if not available."
- `meta/id_space/match_data` removed.
- `meta/id_space/event` removed.
- `meta/id_space/tracking` removed.

#### Table 10. Optional Meta Data

- `match/round` description changed to reflect snake case (e.g. _semi_final_)
- `match/misc/percipitation` data type changed to `Integer`
- `stadium/turf` description changed to reflect snake case (e.g. `natural_reinforced`)
