# Base Image: Python 3.10 Slim (Official)
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# working directory
WORKDIR /app

# Install system dependencies
# - curl/git: General utilities
# - build-essential: For compiling python extensions if needed
# - ffmpeg: Required for Whisper/Audio processing
# - tor: For proxy rotation fallback
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    ffmpeg \
    tor \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Browsers AND System Dependencies
# This command installs the browsers + the Linux libs needed to run them
RUN playwright install --with-deps chromium

# Copy application source code
# We copy everything else (respecting .dockerignore)
COPY . .

# Copy and setup entrypoint script
COPY start.sh .
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

# Expose Streamlit port
EXPOSE 8501

# Healthcheck to ensure Streamlit is responsive
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Entrypoint
CMD ["./start.sh"]
