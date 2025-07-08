# Use a specific version of Node.js for reproducibility
FROM node:20-alpine AS base

# Install pnpm
RUN npm install -g pnpm

# --- Builder Stage ---
FROM base AS builder

# Set the working directory to the root of the application
WORKDIR /app

# Copy the entire project source code into the builder
COPY . .

# Change the working directory to the frontend folder
WORKDIR /app/nextjs-frontend

# Install dependencies for the frontend
RUN pnpm install --frozen-lockfile

# Generate the API client.
# The source path is relative to the build context root.
# The destination path is relative to the current WORKDIR.
COPY ../local-shared-data/openapi.json ./shared-data/
RUN pnpm run generate-client

# Build the Next.js application for production
RUN pnpm build

# --- Production Stage ---
FROM base AS production

# Set environment variable for production and the working directory
ENV NODE_ENV=production
WORKDIR /app

# Selectively copy necessary files from the builder stage
COPY --from=builder /app/nextjs-frontend/.next ./.next
COPY --from=builder /app/nextjs-frontend/public ./public
COPY --from=builder /app/nextjs-frontend/package.json ./package.json
COPY --from=builder /app/nextjs-frontend/pnpm-lock.yaml ./pnpm-lock.yaml
COPY --from=builder /app/nextjs-frontend/next.config.mjs ./next.config.mjs

# Install only production dependencies
RUN pnpm install --prod

# Copy and set permissions for the production startup script
COPY ./start.prod.sh /start.prod.sh
RUN chmod +x /start.prod.sh

# Expose the application port
EXPOSE 3000

# The command to run the application
CMD ["/start.prod.sh"]