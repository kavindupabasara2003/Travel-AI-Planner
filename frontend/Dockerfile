# Build stage
FROM node:20-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
# Production stage
FROM caddy:alpine as production-stage
COPY --from=build-stage /app/dist /srv
COPY Caddyfile /etc/caddy/Caddyfile
EXPOSE 80
EXPOSE 443
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
