import discord, datetime, message_embeds
from discord.ext import commands, tasks
from discord_components import Button, ButtonStyle
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType

async def update_suggestion(self, ctx, suggestion_id, comment, color, action):
    suggestion = await self.bot.db.suggestions.find_one({"id": str(suggestion_id)})
    if suggestion is None:
        return await ctx.send("That is not a valid Suggestion ID!", hidden=True)
    msg = await self.bot.get_channel(self.suggestion_channel).fetch_message(int(suggestion['message']))
    embed = msg.embeds[0]
    embed.color = color
    embed.title = f"{action.capitalize()} Suggestion (#{suggestion['id']})"
    if comment is not None:
        embed.add_field(name=f"Comment from {ctx.author.display_name}", value=str(comment), inline=False)
    await msg.edit(embed=embed)
    user = self.bot.get_user(int(suggestion['user']))
    if user is not None:
        try:
            await user.send(f"Your suggestion has been {action.lower()} by {ctx.author.display_name}!", embed=embed)
        except:
            pass
    await msg.clear_reactions()
    await ctx.send(f"{action.capitalize()} Suggestion {suggestion_id}!", embed=embed, hidden=True)

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.suggestion_channel = 865920296660500552

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.suggestion_channel or message.author.bot:
            return
        suggestion_id = str(len(await self.bot.db.suggestions.find({}).to_list(None)) + 1)
        embed = discord.Embed(title=f"New Suggestion (#{suggestion_id})", description=str(message.content), color=discord.Color.blue())
        embed.set_author(name=str(message.author.display_name), icon_url=str(message.author.avatar_url), url=f"https://discordrep.com/u/{message.author.id}#")
        await message.delete()
        msg = await message.channel.send(embed=embed)
        await self.bot.db.suggestions.insert_one({"id": suggestion_id, "user": str(message.author.id), "message": str(msg.id)})
        await msg.add_reaction(self.bot.get_emoji(866363506071437352))
        await msg.add_reaction(self.bot.get_emoji(865733569003782194))
        await msg.add_reaction(self.bot.get_emoji(866348776851111936))

    @cog_ext.cog_subcommand(base="suggestion", name="approve", description="Approve a suggestion!", guild_ids=[865711881075163166], base_default_permission=False,
    options=[{"name": "suggestion_id", "description": "The id of the suggestion.", "type": 4, "required": True},
    {"name": "comment", "description": "A suggestion comment to be added when approving.", "type": 3, "required": False}])
    @cog_ext.permission(guild_id=865711881075163166, permissions=[create_permission(865905302003646484, SlashCommandPermissionType.ROLE, True)])
    async def suggestion_approve(self, ctx, suggestion_id, comment=None):
        await update_suggestion(self, ctx, suggestion_id, comment, discord.Color.green(), 'approved')

    @cog_ext.cog_subcommand(base="suggestion", name="deny", description="Deny a suggestion!", guild_ids=[865711881075163166], base_default_permission=False,
    options=[{"name": "suggestion_id", "description": "The id of the suggestion.", "type": 4, "required": True},
    {"name": "comment", "description": "A suggestion comment to be added when approving.", "type": 3, "required": False}])
    @cog_ext.permission(guild_id=865711881075163166, permissions=[create_permission(865905302003646484, SlashCommandPermissionType.ROLE, True)])
    async def suggestion_deny(self, ctx, suggestion_id, comment=None):
        await update_suggestion(self, ctx, suggestion_id, comment, discord.Color.red(), 'denied')

    @cog_ext.cog_subcommand(base="suggestion", name="implemented", description="Mark a suggestion as implemented!", guild_ids=[865711881075163166], base_default_permission=False,
    options=[{"name": "suggestion_id", "description": "The id of the suggestion.", "type": 4, "required": True},
    {"name": "comment", "description": "A suggestion comment to be added when denying.", "type": 3, "required": False}])
    @cog_ext.permission(guild_id=865711881075163166, permissions=[create_permission(865905302003646484, SlashCommandPermissionType.ROLE, True)])
    async def suggestion_implemented(self, ctx, suggestion_id, comment=None):
        await update_suggestion(self, ctx, suggestion_id, comment, discord.Color.light_magenta(), 'implemented')

    @cog_ext.cog_subcommand(base="suggestion", name="inprogress", description="Mark a suggestion as in progress!", guild_ids=[865711881075163166], base_default_permission=False,
    options=[{"name": "suggestion_id", "description": "The id of the suggestion.", "type": 4, "required": True},
    {"name": "comment", "description": "A suggestion comment to be added when marking as in progress.", "type": 3, "required": False}])
    @cog_ext.permission(guild_id=865711881075163166, permissions=[create_permission(865905302003646484, SlashCommandPermissionType.ROLE, True)])
    async def suggestion_inprogress(self, ctx, suggestion_id, comment=None):
        suggestion = await self.bot.db.suggestions.find_one({"id": str(suggestion_id)})
        if suggestion is None:
            return await ctx.send("That is not a valid Suggestion ID!", hidden=True)
        msg = await self.bot.get_channel(self.suggestion_channel).fetch_message(int(suggestion['message']))
        embed = msg.embeds[0]
        embed.color = discord.Color.dark_yellow()
        embed.title = f"In Progress Suggestion (#{suggestion['id']})"
        if comment is not None:
            embed.add_field(name=f"Comment from {ctx.author.display_name}", value=str(comment), inline=False)
        await msg.edit(embed=embed)
        await msg.clear_reactions()
        await ctx.send(f"Marked Suggestion {suggestion_id} as in progress!", embed=embed, hidden=True)

    @cog_ext.cog_subcommand(base="suggestion", name="comment", description="Add a comment to a suggestion!", guild_ids=[865711881075163166],
    options=[{"name": "suggestion_id", "description": "The id of the suggestion.", "type": 4, "required": True},
    {"name": "comment", "description": "The comment you'd like to add to the suggestion.", "type": 3, "required": True}])
    @cog_ext.permission(guild_id=865711881075163166, permissions=[ create_permission(865905302003646484, SlashCommandPermissionType.ROLE, True)])
    async def suggestion_comment(self, ctx, suggestion_id, comment):
        suggestion = await self.bot.db.suggestions.find_one({"id": str(suggestion_id)})
        if suggestion is None:
            return await ctx.send("That is not a valid Suggestion ID!", hidden=True)
        msg = await self.bot.get_channel(self.suggestion_channel).fetch_message(int(suggestion['message']))
        embed = msg.embeds[0]
        embed.add_field(name=f"Comment from {ctx.author.display_name}", value=str(comment), inline=False)
        await msg.edit(embed=embed)
        await ctx.send(f"Added a comment to suggestion {suggestion_id}!", embed=embed, hidden=True)

def setup(bot):
    bot.add_cog(Suggestions(bot))
