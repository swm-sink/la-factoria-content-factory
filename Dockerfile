# Use the official Python image as a parent image
FROM python:3.10-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set the working directory in the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir safety

# Copy the main application code
COPY . .

# Set proper file permissions
RUN chown -R appuser:appuser /app && \
    chmod -R 755 /app

# Switch to non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 8080

# Run security scan
RUN safety check

# Command to run the application
CMD ["gunicorn", "--workers=4", "--bind=:8080", "--timeout=120", "main:app"]
