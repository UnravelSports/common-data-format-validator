# Changelog

This changelog references Anzer et al. 2025. The changelog is structured to follow this papers' structure. As a result, the changelog address changes per table. 

Each table in the paper discusses mandatory and optional Match Sheet, Video Footage, Event, Tracking, Skeletal and Meta data.

### Changelog v0.2.0 (alpha)

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
- `events/goals` should be `null` if a game ends 0-0.

**events/substitutions**
- `events/substitutions/{i}/in_time` is recorded in UTC.
- `events/substitutions/{i}/out_time` is recorded in UTC.
- `events/substitutions/{i}/team_id` It denotes the unique team identifier of the team that made the substitution.

**events/cards**
- `events/cards/{i}/card_time` is:
    - renamed to `events/cards/{i}/time`.
    - recorded in UTC.
- `events/cards/{i}/team_id` It denotes the unique team identifier of the team that received the card.

