# ─── Base image ───
FROM python:3.12-slim

# ─── Set working directory ───
WORKDIR /app

# ─── Copy files ───
COPY . /app

# ─── Install dependencies ───
RUN pip install --no-cache-dir -r requirements.txt

# ─── Expose ports if needed (Discord bot usually does not need this) ───
# EXPOSE 8080

# ─── Set environment variables from .env automatically (optional) ───
# ENV DISCORD_TOKEN=${DISCORD_TOKEN}
# ENV PREFIX=${PREFIX}

# ─── Run bot ───
CMD ["python", "bot.py"]
