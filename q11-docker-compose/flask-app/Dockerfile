# syntax=docker/dockerfile:1

# ---- builder ----
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- production ----
FROM python:3.12-slim AS production

# python's slim image doesn't ship a non-root user like node's does, so
# creating one here with an actual home dir (needed since pip --user
# installs land under the user's home)
RUN adduser --disabled-password --gecos "" --home /home/app app

WORKDIR /app

COPY --from=builder --chown=app:app /root/.local /home/app/.local
COPY --chown=app:app . .

ENV PATH=/home/app/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

USER app

EXPOSE 5000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
