FROM node:20-alpine

# Install bash
RUN apk add --no-cache bash

# Set the working directory
WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Copy package files and install dependencies
COPY package*.json ./

# Install dependencies as root (or myappuser, depending on your structure)
RUN pnpm install

## Switch to the non-root user
USER node

# Copy the rest of your application code
COPY . .

# Ensure start.sh has execute permissions
USER root
RUN chmod +x ./start.sh
USER node

EXPOSE 3000

# Start the application
CMD ["./start.sh"]