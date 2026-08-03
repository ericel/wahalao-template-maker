FROM scratch

ARG SOURCE_COMMIT
ARG TEMPLATE_VERSION=2.1.0

LABEL org.opencontainers.image.title="Weynear Live Sports Scores"
LABEL org.opencontainers.image.description="Capability-bound Weynear automation template"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.source="https://github.com/ericel/wahalao-template-maker"
LABEL org.opencontainers.image.revision="${SOURCE_COMMIT}"
LABEL org.opencontainers.image.version="${TEMPLATE_VERSION}"
LABEL com.weynear.automation.entrypoint="main:handler"
LABEL com.weynear.automation.runtime="python3.12"

COPY src/sports_live_scores/main.py /automation/main.py
COPY src/sports_live_scores/__init__.py /automation/__init__.py
