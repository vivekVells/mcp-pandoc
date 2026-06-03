FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y texlive-xetex texlive-lang-chinese pandoc fonts-noto-cjk && \
    rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY uv.lock pyproject.toml README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY src/ src/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV MCP_PANDOC_TRANSPORT=http
ENV MCP_PANDOC_UPLOAD_DIR=/tmp/uploads

RUN mkdir -p /tmp/uploads

EXPOSE 8080

ENTRYPOINT ["mcp-pandoc"]
