"""Capability-bound sports score automation.

The hosted runtime supplies ``ctx.http``, ``ctx.posts``, and ``ctx.state``.
This package deliberately has no credentials, network client, database client,
or Weynear service imports.
"""

import hashlib
import json


_STATUS_MAP = {
    "TBD": "SCHEDULED",
    "NS": "NOT_STARTED",
    "1H": "LIVE",
    "HT": "HALF_TIME",
    "2H": "LIVE",
    "ET": "LIVE",
    "BT": "PAUSED",
    "P": "LIVE",
    "SUSP": "SUSPENDED",
    "INT": "PAUSED",
    "FT": "FINAL",
    "AET": "FINAL",
    "PEN": "FINAL",
    "PST": "POSTPONED",
    "CANC": "CANCELLED",
    "ABD": "ABANDONED",
    "AWD": "FINAL",
    "WO": "FINAL",
}


def _fixture_events(values, home_id, away_id):
    result = []
    for raw in values if isinstance(values, list) else []:
        team_id = (raw.get("team") or {}).get("id")
        if str(team_id) == str(home_id):
            side = "HOME"
        elif str(team_id) == str(away_id):
            side = "AWAY"
        else:
            continue

        detail = str(raw.get("detail") or "")
        event_type = str(raw.get("type") or "").lower()
        lowered_detail = detail.lower()
        if event_type == "goal":
            if "missed" in lowered_detail:
                kind = "MISSED_PENALTY"
            elif "own" in lowered_detail:
                kind = "OWN_GOAL"
            elif "penalty" in lowered_detail:
                kind = "PENALTY_GOAL"
            else:
                kind = "GOAL"
        elif event_type == "card":
            if "second yellow" in lowered_detail:
                kind = "SECOND_YELLOW_CARD"
            elif "red" in lowered_detail:
                kind = "RED_CARD"
            else:
                kind = "YELLOW_CARD"
        elif event_type in {"subst", "substitution"}:
            kind = "SUBSTITUTION"
        elif event_type == "var":
            kind = "VAR"
        else:
            kind = "OTHER"

        time = raw.get("time") or {}
        event = {
            "team_side": side,
            "kind": kind,
            "minute": int(time.get("elapsed") or 0),
        }
        if time.get("extra") is not None:
            event["extra_minute"] = int(time["extra"])
        for key, value in {
            "player": (raw.get("player") or {}).get("name"),
            "assist": (raw.get("assist") or {}).get("name"),
            "detail": detail,
        }.items():
            if value:
                event[key] = str(value)
        result.append(event)
    return result[:64]


def _fingerprint(match: dict) -> str:
    public = {
        "home_score": int(match["home_team"]["score"]),
        "away_score": int(match["away_team"]["score"]),
        "status": str(match["status"]).upper(),
        "clock": str(match.get("clock") or ""),
        "period": str(match.get("period") or ""),
    }
    return hashlib.sha256(
        json.dumps(public, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _api_football_fixture(item: dict) -> dict:
    fixture = item.get("fixture") or {}
    league = item.get("league") or {}
    teams = item.get("teams") or {}
    goals = item.get("goals") or {}
    status = fixture.get("status") or {}
    home = teams.get("home") or {}
    away = teams.get("away") or {}
    elapsed = status.get("elapsed")
    status_short = str(status.get("short") or "NS").upper()
    home_score = int(goals.get("home") or 0)
    away_score = int(goals.get("away") or 0)
    competition = str(league.get("name") or "").strip()
    country = str(league.get("country") or "").strip()
    if country and competition:
        competition = f"{competition} · {country}"
    result = {
        "id": str(fixture.get("id") or ""),
        "competition": competition,
        "home_team": {
            "name": str(home.get("name") or ""),
            "score": home_score,
            **({"logo_url": str(home.get("logo"))} if home.get("logo") else {}),
        },
        "away_team": {
            "name": str(away.get("name") or ""),
            "score": away_score,
            **({"logo_url": str(away.get("logo"))} if away.get("logo") else {}),
        },
        "home_score": home_score,
        "away_score": away_score,
        "status": _STATUS_MAP.get(status_short, status_short),
        "clock": f"{int(elapsed):02d}:00" if elapsed is not None else "",
        "period": status_short,
        "revision": f"{status_short}:{elapsed}:{home_score}:{away_score}",
        "provider": "API-Football",
        "source_url": "https://www.api-football.com/",
    }
    venue = fixture.get("venue") or {}
    for key, value in {
        "round": league.get("round"),
        "started_at": fixture.get("date"),
        "venue": venue.get("name"),
        "venue_city": venue.get("city"),
        "referee": fixture.get("referee"),
    }.items():
        if value:
            result[key] = str(value)
    half_time = (item.get("score") or {}).get("halftime") or {}
    if half_time.get("home") is not None and half_time.get("away") is not None:
        result["half_time"] = {
            "home": int(half_time["home"]),
            "away": int(half_time["away"]),
        }
    events = _fixture_events(item.get("events"), home.get("id"), away.get("id"))
    if events:
        result["events"] = events
    return result


def _provider_matches(payload: dict) -> list[dict]:
    if not isinstance(payload, dict):
        return []
    if isinstance(payload.get("response"), list):
        return [
            _api_football_fixture(item)
            for item in payload["response"]
            if isinstance(item, dict)
        ]
    return [item for item in payload.get("matches") or [] if isinstance(item, dict)]


def handler(event, ctx):
    del event
    matches = ctx.http.get_json(connection_id="sports-data")
    actions = []
    for raw in _provider_matches(matches)[:20]:
        match_id = str(raw.get("match_id") or raw.get("id") or "").strip()
        home_raw = raw.get("home_team")
        away_raw = raw.get("away_team")
        home_name = (
            str(home_raw.get("name") or "").strip()
            if isinstance(home_raw, dict)
            else str(home_raw or "").strip()
        )
        away_name = (
            str(away_raw.get("name") or "").strip()
            if isinstance(away_raw, dict)
            else str(away_raw or "").strip()
        )
        home_score = int(
            home_raw.get("score", raw.get("home_score", 0))
            if isinstance(home_raw, dict)
            else raw.get("home_score", 0)
        )
        away_score = int(
            away_raw.get("score", raw.get("away_score", 0))
            if isinstance(away_raw, dict)
            else raw.get("away_score", 0)
        )
        if not match_id or not home_name or not away_name or home_score < 0 or away_score < 0:
            continue
        match = {
            "source_match_id": match_id,
            "competition": str(raw.get("competition") or "").strip(),
            "home_team": {
                "name": home_name,
                "score": home_score,
                **(
                    {"logo_url": str(home_raw.get("logo_url"))}
                    if isinstance(home_raw, dict) and home_raw.get("logo_url")
                    else {}
                ),
            },
            "away_team": {
                "name": away_name,
                "score": away_score,
                **(
                    {"logo_url": str(away_raw.get("logo_url"))}
                    if isinstance(away_raw, dict) and away_raw.get("logo_url")
                    else {}
                ),
            },
            "home_score": home_score,
            "away_score": away_score,
            "status": str(raw.get("status") or "SCHEDULED").upper(),
            "clock": str(raw.get("clock") or ""),
            "period": str(raw.get("period") or ""),
        }
        for key in ("round", "started_at", "venue", "venue_city", "referee"):
            if raw.get(key):
                match[key] = str(raw[key])
        if isinstance(raw.get("half_time"), dict):
            match["half_time"] = raw["half_time"]
        if isinstance(raw.get("events"), list) and raw["events"]:
            match["events"] = raw["events"][:64]

        fingerprint = _fingerprint(match)
        state_key = f"match:{match_id}"
        previous = ctx.state.get_json(state_key) or {}
        if previous.get("fingerprint") == fingerprint:
            continue
        result = ctx.posts.upsert(
            destination_id="league-score-posts",
            external_key=state_key,
            source_version=str(raw.get("revision") or "0"),
            fingerprint=fingerprint,
            content={
                "template": "sports.score.v1",
                "template_version": 1,
                "fallback_text": (
                    f"{home_name} {home_score}–{away_score} {away_name} "
                    f"— {match['status']}"
                ),
                "data": {
                    key: value
                    for key, value in match.items()
                    if key not in {"home_score", "away_score"}
                },
            },
            sources=[
                {
                    "provider": str(raw.get("provider") or "sports-data"),
                    "external_id": match_id,
                    "canonical_url": str(raw.get("source_url") or ""),
                }
            ],
            idempotency_key=(
                f"sports-score:{match_id}:"
                f"{raw.get('revision') or '0'}:{fingerprint[:16]}"
            ),
        )
        ctx.state.put_json(
            state_key,
            {"fingerprint": fingerprint, "result_id": result.resource_id},
        )
        actions.append(result.resource_id)
    return {"actions": actions}
