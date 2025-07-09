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

# Install dependencies for the frontend
RUN pnpm install --frozen-lockfile

# Generate the API client.
# The source path is relative to the build context root.
# The destination path is relative to the current WORKDIR.
RUN pnpm run generate-client

# Build the Next.js application for production
RUN pnpm build

# --- Production Stage ---
FROM base AS production

# Set environment variable for production and the working directory
ENV NODE_ENV=production
WORKDIR /app

# Copy the standalone output from the builder stage.
# This contains everything needed to run the application.
COPY --from=builder /app/.next/standalone .

# Copy the static assets from the builder stage.
# These are not included in the standalone output and must be copied separately.
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Expose the application port
EXPOSE 3000

# Start the application using the standalone server
# The command is now defined in start.prod.sh, which should run `node server.js`
CMD ["node", "server.js"]