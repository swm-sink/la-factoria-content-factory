# Dockerfile for the AI Content Factory
# ------------------------------------------------------------------------------
# This Dockerfile uses a multi-stage build to create a production-ready image
# for the application. It includes stages for building the frontend and backend,
# and a final stage that combines these with Nginx for serving static assets
# and proxying to the FastAPI backend run by Uvicorn.
# The final image runs the application as a non-root user.
# ------------------------------------------------------------------------------

# Stage 1: Build the frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the backend
FROM python:3.11-slim AS backend-builder
WORKDIR /opt/app_code

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app ./app

# Stage 3: Final image with Nginx for serving frontend and Uvicorn for backend
FROM python:3.11-slim

# Create a non-root user and group
RUN groupadd -r appgroup && useradd --no-log-init -r -g appgroup appuser

WORKDIR /opt/app_code

# Install Nginx and envsubst utility
RUN apt-get update && apt-get install -y nginx gettext-base && apt-get clean

# Copy placeholder static content first (will be overwritten by frontend-builder if it exists)
COPY docker/static_content/index.html /usr/share/nginx/html/index.html

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copy backend app and dependencies from backend-builder stage
# Ensure correct ownership when copying
COPY --from=backend-builder --chown=appuser:appgroup /opt/app_code/app ./app
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin


# Copy Nginx configuration
# Nginx typically needs to run its master process as root to bind to port 80.
# Worker processes then run as a less privileged user (e.g., www-data, specified in nginx.conf).
# We will keep Nginx running as default for now, focusing on running the app as non-root.
COPY docker/nginx/nginx.conf /etc/nginx/

# Copy start script and make it executable
COPY --chown=appuser:appgroup start.sh /start.sh
RUN chmod +x /start.sh

# Set permissions for appuser for necessary directories if Uvicorn needs to write logs/pids here
# For now, assuming logs go to stdout/stderr which is fine.
# If Uvicorn needs to write to /opt/app_code for any reason (e.g. temp files, though unlikely for this app)
# RUN chown -R appuser:appgroup /opt/app_code
# Ensure Nginx can read static files (usually default permissions are fine)

# Nginx will listen on this port (via env var substitution in start.sh),
# Uvicorn on another internal one (typically 8000, set by APP_PORT for Uvicorn in start.sh).
# Cloud Run will map to the NGINX_PORT.
EXPOSE 8080

# Switch to the non-root user
USER appuser

# Start Uvicorn for backend and Nginx for frontend
# The start.sh script will handle starting Nginx (which might need root for master) and Uvicorn (as appuser)
CMD ["/start.sh"]
