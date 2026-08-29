# Q11 - Docker Compose (Flask + Redis)

Two services wired together with Compose: a Flask API (multi-stage build,
non-root user) and Redis, talking to each other over an isolated network.
The Flask app actually uses Redis (a visit counter on `/`), not just a
container that happens to be running next to it.

## Bringing it up

    docker compose up -d --build

This picks up `docker-compose.override.yml` automatically, which is the dev
convenience layer - it bind-mounts the app source so code changes show up
without rebuilding, runs Flask's own debug server with the reloader instead
of gunicorn, and pins the port to a fixed 5000:5000 since you're only running
one instance locally.

Check status:

    docker compose ps

Try it:

    curl http://localhost:5000/          # increments a visits counter in redis
    curl http://localhost:5000/health    # checks flask can reach redis

## Bringing it down

    docker compose down

Add `-v` if you also want to wipe the redis data volume:

    docker compose down -v

## Scaling

Scaling only works against the base file, not with the dev override active -
the override pins the host port to a fixed 5000:5000, and multiple replicas
can't all bind the same host port. The base `docker-compose.yml` leaves the
host side of the port mapping unassigned on purpose (`ports: - "5000"`), so
Docker gives each replica its own free host port instead:

    docker compose -f docker-compose.yml up -d --build --scale api=3
    docker compose -f docker-compose.yml ps

That shows three api containers, each forwarding a different host port to
its own container port 5000.

## Design choices / assumptions

- Redis has no host port published at all - it's only reachable by the api
  service over the internal `backend` network. That's the actual network
  isolation piece, not just naming a network.
- `depends_on` on the api service uses `condition: service_healthy` against
  redis's own healthcheck (`redis-cli ping`), so api genuinely waits for
  redis to be ready to accept connections, not just for the container to
  have started.
- The Flask image runs as a non-root user (`app`), created manually in the
  Dockerfile since python's slim image doesn't ship one built-in the way
  node's images do. Confirmed with `docker compose exec api whoami`.
- `restart: on-failure:3` on both services - restarts automatically if
  something crashes, but caps the retries instead of restarting forever if
  something is genuinely broken.
- Config comes from `.env` (REDIS_HOST, REDIS_PORT). `.env` itself is
  gitignored and `.env.example` is committed instead - habit worth keeping
  even though nothing in this particular file is sensitive.
- The compose file still has `version: "3.9"` in it, which newer Docker
  Compose flags as obsolete and ignores - kept anyway since the challenge
  explicitly asked for version 3+. The warning is expected and harmless.

## What actually got tested

    docker compose up -d --build
    docker compose ps                    # both containers healthy
    curl http://localhost:5000/          # visits: 1
    curl http://localhost:5000/          # visits: 2
    docker compose exec api whoami       # -> app
    docker compose down
    docker compose -f docker-compose.yml up -d --build --scale api=3
    docker compose -f docker-compose.yml ps   # 3 api containers, 3 distinct host ports
