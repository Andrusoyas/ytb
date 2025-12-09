# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies including python-dotenv
RUN pip install --no-cache-dir -r requirements.txt python-dotenv

# Install ffmpeg for voice/audio support
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Environment variables (Coolify can override via .env)
ENV DISCORD_TOKEN=""
ENV PREFIX="!"
ENV BOT_FILE="main.py"

# Run the bot
CMD ["python", "main.py"]
