# ---- Base Node ----
FROM node:alpine AS base
WORKDIR /app
COPY package*.json ./

# ---- Dependencies ----
FROM base AS dependencies
RUN npm ci
# Install additional dependencies that might be missing
RUN npm install rehype-mathjax --save

# ---- Build ----
FROM dependencies AS build
COPY . .
RUN npm run build

# ---- Production ----
FROM node:alpine AS production
WORKDIR /app
COPY --from=dependencies /app/node_modules ./node_modules
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/package*.json ./
COPY --from=build /app/next.config.js ./next.config.js
COPY --from=build /app/next-i18next.config.js ./next-i18next.config.js

# Set the environment variable
ENV DEFAULT_MODEL="default"
ENV API_HOST="http://localhost:8000"
ENV NEXT_PUBLIC_API_TIMEOUT="600000"

# Expose the port the app will run on
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
