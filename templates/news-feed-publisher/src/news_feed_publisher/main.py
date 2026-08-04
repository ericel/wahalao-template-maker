"""Publish newly discovered feed entries as canonical links.

The hosted runtime supplies a reviewed RSS/Atom feed through ``ctx.http`` and
capability-scoped post/state APIs. It retains network credentials and tenant
identity outside template code. Weynear's post service enriches each canonical
URL with the same native link-preview pipeline used for user-authored posts.
"""

import hashlib


def _fingerprint(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def handler(event, ctx):
    del event
    entries = ctx.http.get_feed(connection_id="news-feed")
    maximum_items = max(1, min(int(ctx.config.get("MAX_ITEMS_PER_RUN", 5)), 20))
    actions = []
    for raw in entries[:maximum_items] if isinstance(entries, list) else []:
        if not isinstance(raw, dict):
            continue
        url = str(raw.get("canonical_url") or "").strip()
        headline = str(raw.get("headline") or "").strip()
        external_id = str(raw.get("external_id") or url).strip()
        source_name = str(raw.get("source_name") or "News feed").strip()
        if not url.startswith("https://") or not headline or not external_id:
            continue
        fingerprint = _fingerprint(url)
        state_key = "news:" + hashlib.sha256(external_id.encode("utf-8")).hexdigest()[:40]
        previous = ctx.state.get_json(state_key) or {}
        if previous.get("fingerprint") == fingerprint:
            continue
        published_at = str(raw.get("published_at") or "").strip()
        result = ctx.posts.upsert(
            destination_id="news-posts",
            external_key=state_key,
            source_version=(published_at or fingerprint[:24]).replace(":", "-")[:256],
            fingerprint=fingerprint,
            content={
                "template": "news.link.v1",
                "template_version": 1,
                "fallback_text": url,
                "data": {
                    "url": url,
                    "headline": headline[:300],
                    "source_name": source_name[:160],
                    **({"published_at": published_at} if published_at else {}),
                },
            },
            sources=[{
                "provider": "rss",
                "external_id": external_id[:256],
                "canonical_url": url,
                "publisher": source_name[:160],
                "title": headline[:300],
                **({"published_at": published_at} if published_at else {}),
            }],
            idempotency_key=f"news-link:{state_key}:{fingerprint[:24]}",
        )
        ctx.state.put_json(
            state_key,
            {"fingerprint": fingerprint, "result_id": result.resource_id},
        )
        actions.append(result.resource_id)
    return {"actions": actions}
