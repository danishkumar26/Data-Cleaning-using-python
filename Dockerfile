# Dockerfile for dataclean
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e .

COPY src/ ./src/
COPY cleaning-rules.yaml.example ./

RUN groupadd -r dataclean && useradd -r -g dataclean dataclean \
    && mkdir -p /app/data /app/output \
    && chown -R dataclean:dataclean /app

USER dataclean

ENTRYPOINT ["dataclean"]
CMD ["--help"]