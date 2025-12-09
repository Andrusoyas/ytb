import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv

# ── LOAD ENV ──
load_dotenv()  # load variables from .env

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")  # default to "!" if not set

# ── INTENTS / BOT ──
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}


# ───────── YT-DLP HELPER ─────────

async def ytdlp_get_audio(query: str):
    """Use yt-dlp in a thread, return (audio_url, title)."""
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch",
        "nocheckcertificate": True,
    }

    def _run():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if "entries" in info:
                info = info["entries"][0]
            return info["url"], info.get("title", "Unknown title")

    loop = asyncio.get_running_loop()
    audio_url, title = await loop.run_in_executor(None, _run)
    return audio_url, title


# ───────── EVENTS ─────────

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """Show real command errors in console and in chat."""
    original = getattr(error, "original", error)
    import traceback
    print("=== COMMAND ERROR START ===")
    traceback.print_exception(type(original), original, original.__traceback__)
    print("=== COMMAND ERROR END ===")
    await ctx.send(f"❌ {original}")


# ───────── VOICE HELPERS ─────────

async def connect_to_user_voice(ctx: commands.Context) -> discord.VoiceClient:
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ You must be in a voice channel to use this.")
        return None

    user_channel = ctx.author.voice.channel
    vc = ctx.voice_client

    if vc is None:
        try:
            vc = await user_channel.connect()
        except Exception as e:
            print("VOICE CONNECT ERROR:", repr(e))
            await ctx.send(
                "❌ I couldn't join your voice channel. "
                "This is a **hosting / server voice issue**. "
                f"Error: `{e}`"
            )
            return None
    elif vc.channel != user_channel:
        try:
            await vc.move_to(user_channel)
        except Exception as e:
            print("VOICE MOVE ERROR:", repr(e))
            await ctx.send(
                "❌ I couldn't move to your voice channel. "
                f"Error: `{e}`"
            )
            return None

    if not vc.is_connected():
        await ctx.send(
            "❌ I'm still not connected to voice. "
            "Your host likely does not support Discord voice in this container."
        )
        return None

    return vc


# ───────── COMMANDS ─────────

@bot.command()
async def join(ctx: commands.Context):
    vc = await connect_to_user_voice(ctx)
    if vc is not None:
        await ctx.send(f"✅ Joined **{vc.channel}**")


@bot.command()
async def leave(ctx: commands.Context):
    vc = ctx.voice_client
    if vc is None:
        return await ctx.send("❌ I'm not in a voice channel.")
    await vc.disconnect()
    await ctx.send("👋 Disconnected.")


@bot.command()
async def play(ctx: commands.Context, *, query: str):
    vc = await connect_to_user_voice(ctx)
    if vc is None:
        return

    if vc.is_playing() or vc.is_paused():
        vc.stop()

    status_msg = await ctx.send("🔎 Fetching audio from YouTube, please wait...")

    try:
        audio_url, title = await ytdlp_get_audio(query)
        print("Got audio URL:", audio_url)

        source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)

        def after_play(err):
            if err:
                print("Playback error:", err)

        vc.play(source, after=after_play)
        await status_msg.edit(content=f"🎶 Now playing: **{title}**")

    except Exception as e:
        print("ERROR in play():", repr(e))
        await status_msg.edit(content=f"❌ Play failed: `{e}`")


@bot.command()
async def stop(ctx: commands.Context):
    vc = ctx.voice_client
    if vc is None:
        return await ctx.send("❌ I'm not in a voice channel.")
    vc.stop()
    await ctx.send("⏹️ Stopped.")


# ───────── RUN BOT ─────────

bot.run(TOKEN)
