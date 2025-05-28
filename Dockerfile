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

WORKDIR /opt/app_code

# Install Nginx
RUN apt-get update && apt-get install -y nginx && apt-get clean

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copy backend app and dependencies from backend-builder stage
COPY --from=backend-builder /opt/app_code/app ./app
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy Nginx configuration
# You will need to create an nginx.conf file
# COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
EXPOSE 8000

# Start Uvicorn for backend and Nginx for frontend
# You will need a script to start both, e.g., start.sh
# CMD ["sh", "./start.sh"]

# For now, just run the backend from the correct location
# The app is now at /opt/app_code/app/main.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
 