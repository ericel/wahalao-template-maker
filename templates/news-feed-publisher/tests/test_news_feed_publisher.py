from dataclasses import dataclass

from news_feed_publisher.main import handler


@dataclass
class _Result:
    resource_id: str


class _Http:
    def __init__(self, entries):
        self.entries = entries
        self.connection_id = ""

    def get_feed(self, *, connection_id):
        self.connection_id = connection_id
        return self.entries


class _Config:
    def get(self, key, default=None):
        return {"MAX_ITEMS_PER_RUN": 5}.get(key, default)


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
        return _Result(resource_id="post-news-1")


class _Context:
    def __init__(self, entries):
        self.http = _Http(entries)
        self.config = _Config()
        self.state = _State()
        self.posts = _Posts()


def test_handler_publishes_canonical_url_once_for_native_preview():
    context = _Context([{
        "external_id": "bbc-news-1",
        "canonical_url": "https://www.bbc.com/news/articles/example",
        "headline": "Example breaking story",
        "source_name": "BBC News",
        "published_at": "2026-08-03T12:00:00Z",
    }])

    first = handler({}, context)
    second = handler({}, context)

    assert first == {"actions": ["post-news-1"]}
    assert second == {"actions": []}
    assert context.http.connection_id == "news-feed"
    assert len(context.posts.calls) == 1
    request = context.posts.calls[0]
    assert request["destination_id"] == "news-posts"
    assert request["content"]["template"] == "news.link.v1"
    assert request["content"]["fallback_text"] == request["content"]["data"]["url"]
