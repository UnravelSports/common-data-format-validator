# Changelog

This changelog references Anzer et al. 2025. The changelog is structured to follow this papers' structure. As a result, the changelog address changes per table. 

Each table in the paper discusses mandatory and optional Match Sheet, Video Footage, Event, Tracking, Skeletal and Meta data.

---

## Changelog v0.2.0 (alpha)

### Table 1. Mandatory Match Sheet Data

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

### Table 2. Mandatory Video Footage Data

No changes. Not yet supported in this package.

### Table 3. Mandatory Event Datas
- `event/type` description changed to: "Name of the event type _(e.g. shot, pass, referee, misc)_"
- `event/outcome_detailed` description changed to: "[...] pass - (_e.g._ successful, out_of_play, intercepted) [...]"
- `event/related_event_ids` shall be `null` if no related events exist.

### Table 4. Mandatory Tracking Data
- `period` description changed to: "Period of the match (first_half, second_half, _first_half_extratime_, _second_half_extratime_, shootout)"

### Table 5. Mandory Skeletal Data

No changes. Not yet supported in this package.

### Table 6. Mandatory Match Meta Data