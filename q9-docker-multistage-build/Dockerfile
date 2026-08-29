# syntax=docker/dockerfile:1

# ---- builder ----
# full node image here on purpose - need npm and whatever build tooling the
# build step might need. none of this ends up in the final image.
FROM node:20 AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci

COPY . .
RUN npm run build

# ---- production ----
FROM node:20-alpine AS production

WORKDIR /app

ENV NODE_ENV=production

# reinstalling here instead of copying node_modules from builder - that one
# has devDependencies in it (linters, test runners, etc), don't want any of
# that shipping in the image that actually runs
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev

# only pulling the build output over, not the whole builder /app
COPY --from=builder --chown=node:node /app/dist ./dist

# alpine's official node image already has a non-root "node" user built in
USER node

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/', r => process.exit(r.statusCode < 500 ? 0 : 1)).on('error', () => process.exit(1))"

CMD ["npm", "start"]
