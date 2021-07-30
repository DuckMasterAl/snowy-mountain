import discord
from discord.ext import commands
from discord_slash import cog_ext

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash()
    async def source(self, ctx):
        """ View the source code on GitHub """
        await ctx.send("You can view the source code here: https://github.com/DuckMasterAl/snowy-mountain", hidden=True)

def setup(bot):
    bot.add_cog(Misc(bot))
