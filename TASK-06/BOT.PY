import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import aiohttp
import asyncio
import requests
import json

load_dotenv()

# Set up bot intents and token
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
bot.remove_command('help')  # Override default help command
token = os.getenv('DISCORD_BOT_TOKEN')

#  Bot Commands 

@bot.command()
async def hello(ctx):
    await ctx.reply("Hello!!")

@bot.command()
async def bye(ctx):
    await ctx.reply("Bye Bye!")

@bot.command()
async def help(ctx):
    await ctx.typing()
    embed = discord.Embed(
        title='BOT COMMANDS',
        description='This section will let you know about all the commands for this bot.',
        color=discord.Color.green()
    )
    embed.add_field(name='/help', value='Shows this message.', inline=False)
    embed.add_field(name='/track <song> - <artist>', value='Get info about a specific track.', inline=False)
    embed.add_field(name='/lyrics <song> - <artist>', value='Fetch lyrics of a song.', inline=False)
    embed.add_field(name='/playlist [add/remove/view/clear] [song]', value='Manage your personal playlist.', inline=False)
    embed.add_field(name='/trending', value='Show top 10 trending songs.', inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def track(ctx, *, query: str):
    if '-' not in query:
        await ctx.reply("Please use the format: `/track <song> - <artist>`")
        return

    song, artist = map(str.strip, query.split('-', 1))
    url = f"https://musicbrainz.org/ws/2/recording?query=recording:\"{song}\" AND artist:\"{artist}\"&fmt=json&inc=tags+releases"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"User-Agent": "DiscordBot/1.0 (your@email.com)"}) as resp:
            if resp.status != 200:
                await ctx.reply("Failed to fetch data from MusicBrainz.")
                return
            s = await resp.json()

    if "recordings" not in s or not s["recordings"]:
        await ctx.send("No results found.")
        return

    data = s["recordings"][0]
    title = data.get("title", "Unknown Title")
    duration = data.get("length", None)
    time = f"{duration / 60000:.2f} minutes" if duration else "Unknown"
    artist_credit = data.get("artist-credit", [])
    artist_name = artist_credit[0]["name"] if artist_credit else "Unknown Artist"
    releases = data.get("releases", [])
    album_name = releases[0]["title"] if releases else "Unknown Album"
    release_date = releases[0].get("date", "Unknown") if releases else "Unknown"
    tags = data.get("tags", [])
    genre_list = [tag["name"] for tag in tags] if tags else ["Unknown"]
    genres = ", ".join(genre_list)

    embed = discord.Embed(title="Track Info", color=discord.Color.green())
    embed.set_thumbnail(url='https://media.istockphoto.com/id/1431567498/vector/vector-illustration-of-musical-notes-on-white-background.jpg')
    embed.add_field(name="Title", value=title, inline=False)
    embed.add_field(name="Artist", value=artist_name, inline=False)
    embed.add_field(name="Album", value=album_name, inline=False)
    embed.add_field(name="Duration", value=time, inline=False)
    embed.add_field(name="Release Date", value=release_date, inline=False)
    embed.add_field(name="Genre(s)", value=genres, inline=False)

    await ctx.send(embed=embed)

# Helper function for splitting lyrics
def chunk_text(text, chunk_size=1024):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

@bot.command()
async def lyrics(ctx, *, query: str):
    if '-' not in query:
        await ctx.reply("Please use the format: `/lyrics <song> - <artist>`")
        return

    song, artist = map(str.strip, query.split('-', 1))
    url = f"https://lrclib.net/api/search?q={song} {artist}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    if not data:
        await ctx.reply("Lyrics not found.")
        return

    lyrics_text = data[0].get("plainLyrics", "Lyrics not available")
    chunks = chunk_text(lyrics_text, 1024)

    embed = discord.Embed(title=f"Lyrics of {song} by {artist}", color=discord.Color.green())
    embed.set_thumbnail(url='https://media.istockphoto.com/id/1431567498/vector/vector-illustration-of-musical-notes-on-white-background.jpg')

    for i, chunk in enumerate(chunks[:5], start=1):  # Limit to 5 parts
        embed.add_field(name=f"Part {i}", value=chunk, inline=False)

    await ctx.reply(embed=embed)

# Updated File Path 
os.makedirs("data", exist_ok=True)
file_path = os.path.join("data", "playlist_data.txt")

@bot.command()
async def playlist(ctx, *, query: str):
    command_parts = query.strip().split(' ', 1)
    action = command_parts[0].lower()
    song = command_parts[1].strip() if len(command_parts) > 1 else ""

    if action == "add" and song:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = [line.strip() for line in f]
        else:
            lines = []

        if song in lines:
            await ctx.send(f"'{song}' is already in your playlist.")
        else:
            with open(file_path, 'a') as f:
                f.write(song + '\n')
            await ctx.send(f"'{song}' has been added to your playlist.")

    elif action == "view":
        if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
            await ctx.send("Your playlist is empty!")
        else:
            with open(file_path, 'r') as f:
                songs = f.read()
            embed = discord.Embed(title="Your Playlist", description=songs, color=discord.Color.green())
            await ctx.send(embed=embed)

    elif action == "remove" and song:
        if not os.path.exists(file_path):
            await ctx.send("Your playlist is empty!")
            return

        with open(file_path, 'r') as f:
            lines = f.readlines()

        with open(file_path, 'w') as f:
            removed = False
            for line in lines:
                if line.strip() != song:
                    f.write(line)
                else:
                    removed = True

        if removed:
            await ctx.send(f"'{song}' has been removed from your playlist.")
        else:
            await ctx.send(f"'{song}' was not found in your playlist.")

    elif action == "clear":
        open(file_path, 'w').close()
        await ctx.send("Your playlist has been cleared.")

    else:
        await ctx.send("Invalid playlist command. Use add, remove, view, or clear.")

@bot.command()
async def trending(ctx):
    url = 'https://api.deezer.com/chart/0/tracks'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            tracks = data.get("data", [])

    embed = discord.Embed(title="Top 10 Trending Tracks", color=discord.Color.green())

    for i, track in enumerate(tracks[:10], start=1):
        title = track.get("title", "Unknown")
        artist = track["artist"].get("name", "Unknown")
        embed.add_field(name=f"{i}. {title}", value=artist, inline=False)

    await ctx.send(embed=embed)

# Events 

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general") or member.guild.text_channels[0]
    if channel:
        await channel.send(f"Welcome to the server, {member.mention}! Use /help to learn about the bot commands.")

# Run the Bot 
bot.run(token)
