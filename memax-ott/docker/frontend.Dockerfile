# =============================================
# MEMAX OTT - Frontend Production Dockerfile
# Multi-stage: Install → Build → Slim Runtime
# =============================================

# --- Stage 1: Install dependencies ---
FROM node:18-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --only=production

# --- Stage 2: Build the Next.js app ---
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

# Inject env at build time
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Increase Node.js memory for next build (prevents OOM SIGTERM)
ENV NODE_OPTIONS="--max-old-space-size=4096"

RUN npm run build

# --- Stage 3: Production slim image ---
FROM node:18-alpine AS production

WORKDIR /app

ENV NODE_ENV=production

# Copy only necessary files
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.js ./next.config.js

# Non-root user
RUN addgroup -g 1001 -S memax && adduser -S memax -u 1001
USER memax

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

CMD ["npm", "start"]
