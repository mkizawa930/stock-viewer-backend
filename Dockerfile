FROM python:3.11-slim AS rye

# pycをfalse
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /workspace

ENV RYE_HOME="/opt/rye"
ENV PATH="$RYR_HOME/shims:$PATH"

RUN curl -sSf https://rye-up.com/get | RYE_NO_AUTO_INSTALL=1 RYE_INSTALL_OPTION="--yes" bash

# RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
#     --mount=type=bind,source=requirements.lock,target=requirements.lock \
#     --mount=type=bind,source=requirements-dev.lock,target=requirements-dev.lock \
#     --mount=type=bind,source=.python-version,target=.python-version \
#     --mount=type=bind,source=README.md,target=README.md \
#     rye sync --no-dev --no-lock