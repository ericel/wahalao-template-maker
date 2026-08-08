# Breaking News Feed 1.1.0

Publishes newly discovered articles from a configured public RSS or Atom feed
once per hour. The feed URL may use any public HTTPS host. Weynear rejects
credentials in URLs, fragments, custom ports, redirects, private or link-local
network addresses, non-feed responses, and responses larger than 2 MiB.

The automation stores only entry fingerprints for deduplication. Each post
contains the article's canonical HTTPS URL and source provenance. The existing
Weynear post service then generates the same Open Graph/link preview used for
ordinary URL posts, so the template does not scrape article pages or duplicate
preview rendering.

Publishers remain responsible for the source feed's terms, attribution, and any
permissions required for their intended use. A feed protected by an interactive
browser challenge is not compatible with server-side polling.
