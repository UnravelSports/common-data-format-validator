# Changelog

This changelog references Anzer et al. 2025. The changelog is structured to follow this papers' structure. As a result, the changelog address changes per table. 

Each table in the paper discusses mandatory and optional Match Sheet, Video Footage, Event, Tracking, Skeletal and Meta data.

---

## Changelog v0.2.0 (alpha)

### Match Sheet Data

#### Table 1. Mandatory Match Sheet Data

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
- `events/cards/{i}/team_id` It denotes the unique team identifier of the team that received the card.

#### Table 7. Optional Match Sheet Data
- `teams/{home|away}/players/{i}/date_of_birth` description changed to: "A player's data of birth in YYYY-MM-DD format*".
- `teams/(home|away)/coaches/{i}/coach_id` renamed to `teams/(home|away)/coaches/{i}/id`
- `teams/(home|away)/coaches/{i}/short_name` description changed to "Short name, a combination of First name (first) and Last name (e.g. Jane Doe, **not** J. Doe)"

----

### Video Footage Data

#### Table 2. Mandatory Video Footage Data

No changes. Not yet supported in this package.

----

### Mandatory Event Data

#### Table 3. Mandatory Event Data
- `event/type` description changed to: "Name of the event type _(e.g. shot, pass, referee, misc)_"
- `event/outcome_detailed` description changed to: "[...] pass - (_e.g._ successful, out_of_play, intercepted) [...]"
- `event/related_event_ids` shall be `null` if no related events exist.

#### Table 8. Mandatory Event Data
- `tracking/frame_end_id` renamed to `tracking/frame_id_end`.
- `tracking/x_player` renamed to `tracking/player/x`
- `tracking/y_player` renamed to `tracking/player/y`
- `event/metrics/xpass` renamed to `event/metrics/expected_pass`
- `event/metrics/expected_poss_value` renamed to `event/metrics/epv`
- `event/var/reviewed` is:
    - changed to type Boolean.
    - description changed to: "Was this event reviewed by the video assistant referee (true) or not (false)"
- `event/var/upheld` is:
    - changed to type Boolean.
    - description changed to: "Was the on-field ruling confirmed (true) or overturned (false)"

----

### Mandatory Tracking Data

#### Table 4. Mandatory Tracking Data
- `period` description changed to: "Period of the match (first_half, second_half, _first_half_extratime_, _second_half_extratime_, shootout)"

#### Table 9. Optional Tracking Data
- `vendor/event` and `vendor/tracking` renamed to `vendor/{event|tracking}/name`
- `teams/{home|away}/jersey_colour` description changed to reflect British spelling ("Jersey colour")

---
### Mandory Skeletal Data

### Table 5. Mandory Skeletal Data

No changes. Not yet supported in this package.

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