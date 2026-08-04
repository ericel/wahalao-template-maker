FROM scratch

ARG SOURCE_COMMIT
ARG TEMPLATE_VERSION=1.0.0

LABEL org.opencontainers.image.title="Weynear News Feed Publisher"
LABEL org.opencontainers.image.description="Capability-bound RSS and Atom news automation"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.source="https://github.com/ericel/wahalao-template-maker"
LABEL org.opencontainers.image.revision="${SOURCE_COMMIT}"
LABEL org.opencontainers.image.version="${TEMPLATE_VERSION}"
LABEL com.weynear.automation.entrypoint="main:handler"
LABEL com.weynear.automation.runtime="python3.12"

COPY src/news_feed_publisher/main.py /automation/main.py
COPY src/news_feed_publisher/__init__.py /automation/__init__.py
