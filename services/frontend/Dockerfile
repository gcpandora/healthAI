# ─────────────────────────────────────────────────────────────
# STAGE 1 — Build
# On compile le Vue.js en statique avec la bonne VITE_API_URL
# ─────────────────────────────────────────────────────────────
FROM node:18-alpine AS build

WORKDIR /app

# Copier les manifestes en premier → cache npm si inchangés
COPY package*.json ./
RUN npm ci

COPY . .

# VITE_API_URL est injectée au build (pas au runtime)
# Elle doit donc passer par un ARG → ENV avant npm run build
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# ─────────────────────────────────────────────────────────────
# STAGE 2 — Serve
# On sert le dist/ compilé avec Nginx (plus léger que vite preview)
# ─────────────────────────────────────────────────────────────
FROM nginx:alpine

# Config Nginx : SPA routing + proxy /api → backend
COPY config/nginx.conf /etc/nginx/conf.d/default.conf

# Copier le build depuis le stage précédent
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]