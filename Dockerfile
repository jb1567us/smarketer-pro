# Base Image: Official Playwright Image (includes Python + Browsers + Deps)
# Using v1.40.0-jammy to match requirements.txt
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# working directory
ENV REBUILD_DATE=2025-01-27
WORKDIR /app

# Install system dependencies
# - ffmpeg: Required for Whisper/Audio processing
# - tor: For proxy rotation fallback
# - espeak, portaudio: For audio tasks
# Note: Docker/Git/Browsers are likely pre-installed or easier to manage here
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    ffmpeg \
    tor \
    espeak-ng \
    portaudio19-dev \
    python3-pyaudio \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright bits:
# Browsers are pre-installed in this image, so 'playwright install' is often skipped
# BUT we explicitly running it ensures we have exactly what we need if the image differs slightly
RUN playwright install chromium

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
