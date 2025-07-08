# Use a specific version of Node.js for reproducibility
FROM node:20-alpine AS base

# Set the working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# --- Builder Stage ---
FROM base AS builder

# Copy dependency definitions
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy the rest of the application source code
COPY . .

# Copy the OpenAPI specification from the shared volume location
# This assumes openapi.json is present in shared-data
COPY ../local-shared-data/openapi.json ../local-shared-data/openapi.json

# Generate the API client
RUN pnpm run generate-client

# Build the Next.js application for production
RUN pnpm build

# --- Production Stage ---
FROM base AS production

# Set environment variable for production
ENV NODE_ENV=production

# Copy built assets from the builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/pnpm-lock.yaml ./pnpm-lock.yaml
COPY --from=builder /app/next.config.mjs ./next.config.mjs

# Install only production dependencies
RUN pnpm install --prod

# Copy and set permissions for the production startup script
COPY ./start.prod.sh /start.prod.sh
RUN chmod +x /start.prod.sh

# Expose the application port
EXPOSE 3000

# The command to run the application
CMD ["/start.prod.sh"]