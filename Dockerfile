# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install ffmpeg (required for voice/audio)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set environment variables (from .env)
ENV DISCORD_TOKEN=${DISCORD_TOKEN}
ENV PREFIX=${PREFIX}
ENV BOT_FILE=${BOT_FILE:-bot/app.py}  # default bot file path

# Entrypoint
CMD ["sh", "-c", "python $BOT_FILE"]
