from copy import deepcopy
from dataclasses import dataclass

from sports_live_scores.main import _fingerprint, _provider_matches, handler


def _fixture(home_score=1, away_score=0, status="1H", elapsed=42):
    return {
        "fixture": {
            "id": 404,
            "date": "2026-08-03T19:00:00Z",
            "status": {"short": status, "elapsed": elapsed},
            "venue": {"name": "Weynear Ground", "city": "Gwangju"},
        },
        "league": {"name": "Premier League", "country": "England", "round": "Round 1"},
        "teams": {
            "home": {"id": 1, "name": "Orange Grass", "logo": "https://example.test/home.png"},
            "away": {"id": 2, "name": "Blue River", "logo": "https://example.test/away.png"},
        },
        "goals": {"home": home_score, "away": away_score},
        "events": [
            {
                "team": {"id": 1},
                "type": "Goal",
                "detail": "Normal Goal",
                "time": {"elapsed": elapsed},
                "player": {"name": "Ada Forward"},
            }
        ],
    }


def test_api_football_payload_is_normalized_without_credentials():
    match = _provider_matches({"response": [_fixture()]})[0]

    assert match["id"] == "404"
    assert match["competition"] == "Premier League · England"
    assert match["status"] == "LIVE"
    assert match["home_team"]["score"] == 1
    assert match["events"][0]["kind"] == "GOAL"
    assert "api_key" not in str(match).lower()


def test_fingerprint_ignores_richer_display_fields():
    match = _provider_matches({"response": [_fixture()]})[0]
    enriched = deepcopy(match)
    enriched["venue"] = "A different display label"
    enriched["events"].append({"team_side": "AWAY", "kind": "VAR", "minute": 43})

    assert _fingerprint(enriched) == _fingerprint(match)


@dataclass
class _Result:
    resource_id: str


class _Http:
    def __init__(self, payload):
        self.payload = payload
        self.connection_id = ""

    def get_json(self, *, connection_id):
        self.connection_id = connection_id
        return self.payload


class _State:
    def __init__(self):
        self.values = {}

    def get_json(self, key):
        return self.values.get(key)

    def put_json(self, key, value):
        self.values[key] = value


class _Posts:
    def __init__(self):
        self.calls = []

    def upsert(self, **request):
        self.calls.append(request)
        return _Result(resource_id="post-score-404")


class _Context:
    def __init__(self, payload):
        self.http = _Http(payload)
        self.state = _State()
        self.posts = _Posts()


def test_handler_upserts_once_and_skips_unchanged_score():
    context = _Context({"response": [_fixture()]})

    first = handler({}, context)
    second = handler({}, context)

    assert first == {"actions": ["post-score-404"]}
    assert second == {"actions": []}
    assert context.http.connection_id == "sports-data"
    assert len(context.posts.calls) == 1
    request = context.posts.calls[0]
    assert request["destination_id"] == "league-score-posts"
    assert request["content"]["template"] == "sports.score.v1"
    assert request["sources"][0]["provider"] == "API-Football"
