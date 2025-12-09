# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install ffmpeg for voice/audio
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Read environment variables from .env (passed by Coolify)
# Use empty default values to avoid syntax errors
ENV DISCORD_TOKEN=""
ENV PREFIX="!"
ENV BOT_FILE="bot/app.py"

# Entrypoint: run the bot
CMD ["sh", "-c", "python $BOT_FILE"]
