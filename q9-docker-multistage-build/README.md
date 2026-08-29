# Q9 - Docker Multi-Stage Build

Two-stage Dockerfile for a Node app: builds in one stage, ships a small
production image from a second stage. Includes a minimal stub app
(`src/index.js`) just so this could actually be built and run instead of
being a Dockerfile nobody ever tested.

## Why two stages

Stage 1 (`builder`) uses the full `node:20` image - not alpine - because you
don't know ahead of time whether a real build step needs compilers or other
native tooling, and none of that weight matters here since this stage never
ships. Stage 2 (`production`) starts fresh from `node:20-alpine` and only
copies over the build output (`dist/`), not the builder's `node_modules` or
source files.

## Why dependencies get reinstalled instead of copied over

The builder stage's `node_modules` has devDependencies mixed in (test
runners, linters, whatever). Copying that whole folder into production would
ship dev tooling in the final image for no reason. Running
`npm ci --omit=dev` fresh in the production stage means only what's actually
needed at runtime ends up there.

## Non-root user

Didn't create a new user for this - the official node images (alpine
included) already ship one called `node`. Just switched to it with `USER
node`. Confirmed with `docker exec <container> whoami` -> `node`.

## Health check

Uses Node's own `http` module to hit the app instead of curl/wget, since
alpine doesn't include those by default and there's no reason to add them
just for a health check. Counts anything under a 500 status as healthy,
since this is a generic check and shouldn't assume a specific route exists
beyond what the app actually serves.

## BuildKit cache mount

`--mount=type=cache,target=/root/.npm` on both `npm ci` steps. Caches npm's
download cache between builds so rebuilding after a small code change
doesn't re-download every package from scratch.

## What actually got tested

    docker build -t q9-stub-app .
    docker run -d -p 3000:3000 --name q9-test q9-stub-app
    curl http://localhost:3000/          # -> "q9 stub app is running"
    docker exec q9-test whoami           # -> node
    docker inspect --format='{{json .State.Health}}' q9-test
                                          # -> "Status":"healthy"

Image content size: 48.4MB.

## Files

- `Dockerfile` - the actual deliverable
- `package.json`, `src/index.js` - minimal stub app, just enough to prove
  the multi-stage build and health check actually work
- `.dockerignore` - keeps node_modules/.git/dist out of the build context
