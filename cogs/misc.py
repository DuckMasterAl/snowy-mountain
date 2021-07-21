import discord, datetime, message_embeds
from discord.ext import commands, tasks
from discord_components import Button, ButtonStyle

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def source(self, ctx):
        await ctx.send("You can view the source code here: https://github.com/DuckMasterAl/snowy-mountain")

def setup(bot):
    bot.add_cog(Misc(bot))
