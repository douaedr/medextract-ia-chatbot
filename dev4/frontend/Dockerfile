# --- Build ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
# Connexion lente : on rend npm patient (plus de temps, plus d'essais)
RUN npm config set fetch-timeout 600000 \
 && npm config set fetch-retries 15 \
 && npm config set fetch-retry-maxtimeout 120000 \
 && npm install --no-audit --no-fund
COPY . .
RUN npm run build

# --- Serve (nginx) ---
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
