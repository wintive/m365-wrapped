# M365 Wrapped — cards are rendered SVG -> PNG with rsvg-convert (librsvg). No browser.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Card renderer: librsvg2-bin (rsvg-convert) + fonts. Inter is the designed look;
# fall back to DejaVu if the Inter package isn't in the base image.
RUN apt-get update \
 && apt-get install -y --no-install-recommends librsvg2-bin fontconfig fonts-dejavu-core \
 && (apt-get install -y --no-install-recommends fonts-inter || true) \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --upgrade pip && pip install .

RUN mkdir -p /app/out
VOLUME ["/app/out"]

ENTRYPOINT ["python", "-m", "m365_wrapped"]
CMD ["--help"]
