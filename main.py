import discord, tokens, os, sys, wavelink
from discord.ext import commands
from discord_slash import SlashCommand
from motor.motor_asyncio import AsyncIOMotorClient

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(
                    command_prefix=commands.when_mentioned_or('s!'),
                    status=discord.Status.online,
                    activity=discord.Activity(type=discord.ActivityType.watching, name='the snow fall!'),
                    case_insensitive=True,
                    allowed_mentions=discord.AllowedMentions.none(),
                    reconnect=True,
                    intents=intents,
                    max_messages=100
                    )
slash = SlashCommand(client=client, sync_commands=True, override_type=True, sync_on_cog_reload=True, delete_from_unused_guilds=True)

db_client = AsyncIOMotorClient(tokens.mongo)# Mongo
client.db = db_client.bot
client.wavelink = wavelink.Client(bot=client)# Wavelink

client.load_extension('jishaku')# Load Cogs
for x in os.listdir('/root/Snow/cogs' if sys.platform == 'linux' else '/Users/duckmasteral/Documents/Github.nosync/snowy-mountain/cogs'):
    if x.endswith('.py'):
        try:
            client.load_extension(f'cogs.{x[:-3]}')
        except Exception as e:
            print(f'{x[:-3]} could not be loaded!')
            print(f"{type(e).__name__}: {e}")

if __name__ == '__main__':
    client.run(tokens.bot)
