# Use official Python image as base
FROM python:3.11-slim

# Install nodejs, npm, and supervisor
RUN apt-get update && apt-get install -y curl gnupg supervisor && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/app /app/backend/app

# Copy frontend code
COPY frontend /app/frontend

# Build frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Move back to /app
WORKDIR /app

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports
EXPOSE 8000 3000

# Start supervisor
CMD ["/usr/bin/supervisord", "-n"]
