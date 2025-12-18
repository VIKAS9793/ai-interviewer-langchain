# Dockerfile for ADK Interviewer - GCP Cloud Run
# Optimized for free tier (minimal resources)

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/adk_interviewer /app/adk_interviewer

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run with ADK web server
CMD ["adk", "web", "--port", "8080", "--host", "0.0.0.0", "adk_interviewer"]
