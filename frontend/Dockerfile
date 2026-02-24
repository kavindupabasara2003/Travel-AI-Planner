# Build stage
FROM node:18-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
# If using Vue Router history mode, copy a custom nginx.conf or add a try_files directive
# Typically handled by replacing the default config or mapping it via compose
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
