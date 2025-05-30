#!/bin/sh
# Startup script for the Docker container.
# This script starts Nginx in the background to serve static frontend assets
# and proxy API requests, then starts Uvicorn as the main process for the
# FastAPI backend application.
# It's intended to be run as the non-root 'appuser'.
set -e

# Define ports. Nginx listens on NGINX_PORT, Uvicorn on APP_PORT (internal).
# Cloud Run's PORT environment variable will typically define what NGINX_PORT should be.
export NGINX_PORT=${PORT:-8080} # Use PORT from Cloud Run, default to 8080
export APP_PORT_UVICORN=${APP_PORT:-8000} # Uvicorn's internal port, Nginx proxies to this

# Substitute environment variables in Nginx config template
# Create a temporary config file that Nginx will use.
# Note: nginx.conf should use ${NGINX_PORT} and ${APP_PORT_UVICORN} for substitution.
# The proxy_pass in nginx.conf template should point to http://localhost:${APP_PORT_UVICORN}
CONF_TEMPLATE="/etc/nginx/nginx.conf"
CONFIG_FILE="/tmp/nginx.conf"

# Ensure the nginx.conf refers to APP_PORT_UVICORN for proxy_pass
# Example line in nginx.conf template for proxy_pass:
# proxy_pass http://localhost:${APP_PORT_UVICORN};
envsubst '${NGINX_PORT} ${APP_PORT_UVICORN}' < "${CONF_TEMPLATE}" > "${CONFIG_FILE}"

# Start Nginx in the background with the processed config
echo "Starting Nginx on port ${NGINX_PORT}, proxying to Uvicorn on ${APP_PORT_UVICORN}..."
nginx -c "${CONFIG_FILE}" -g 'daemon off;' &

# Start Uvicorn, listening on APP_PORT_UVICORN
# The number of workers can also be configured via an environment variable
echo "Starting Uvicorn on port ${APP_PORT_UVICORN}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT_UVICORN} --workers ${UVICORN_WORKERS:-1}
