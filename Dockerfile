# Multi-stage build for efficiently caching dependencies
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Create a non-root user for security (and Hugging Face Spaces compliance)
RUN useradd -m -u 1000 user

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libmagic1 \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces image size
# --user installs to /home/user/.local
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set permissions for data directory
RUN mkdir -p data/memory data/vectors && chown -R user:user /app

# Switch to non-root user
USER user

# Add local bin to PATH
ENV PATH=/home/user/.local/bin:$PATH

# Expose Gradio port
EXPOSE 7860

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT=7860
ENV ANONYMIZED_TELEMETRY=False

# Command to run the application
CMD ["python", "main.py"]
