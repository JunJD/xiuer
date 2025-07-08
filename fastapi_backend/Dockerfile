FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# The uv installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest uv installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the uv installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# This is important for networking in Docker
ENV HOST=0.0.0.0

# Copy dependency files first to leverage Docker caching
COPY pyproject.toml uv.lock ./

# Remove any existing virtual environment and install dependencies (production)
RUN rm -rf .venv && uv sync --frozen

# Copy application code
COPY . .

# Copy and set permissions for the production startup script
COPY ./start.prod.sh /start.prod.sh
RUN chmod +x /start.prod.sh

# Expose the application port
EXPOSE 8000

# The command to run the application
CMD ["/start.prod.sh"]