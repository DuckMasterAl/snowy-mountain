import discord, datetime, message_embeds, math
from discord.ext import commands, tasks
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption

async def update_selfrole_interaction(self, interaction, components, member_roles):
    buttons = []
    clicked_buttons = 0
    for a in components:
        if str(a) in member_roles:
            clicked_buttons += 1
            button_style = ButtonStyle.blue
        else:
            button_style = ButtonStyle.grey
        buttons.append(Button(style=button_style, id=f"ROLE_TOGGLE-{a}", label=interaction.guild.get_role(int(a)).name))

    if clicked_buttons == len(buttons):
        for b in buttons:
            b.style = ButtonStyle.green

    buttons = sorted(buttons, key=lambda q: q.label)
    total_buttons = []
    for c in range(math.ceil(len(buttons) / 5)):
        total_buttons.append(buttons[:5])
        buttons = buttons[5:]

    selects = []
    for x in self.bot.selfroles:
        selects.append(SelectOption(label=x['name'], value=f"ROLE_LIST-{x['name']}"))
    total_buttons = total_buttons + [Select(placeholder="Switch role categories", options=selects)]

    await interaction.respond(type=7, content="Please select the roles you want.", components=total_buttons)

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.member_role = 866019665502273586
        self.serious_access_role = 866362223000289310
        self.news_role = 866023627497406495
        self.serious_channels = [865918494791827536, 865918534177783808]
        self.introduction_channel = 866381489989222410
        self.clear_serious_chats.start()
        self.recache_selfroles.start()

    def cog_unload(self):
        self.clear_serious_chats.cancel()
        self.recache_selfroles.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        DiscordComponents(self.bot)
        print('\033[96m' + 'The snow is now falling!' + '\033[0m')

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot is True or before.content == after.content:
            return
        prefixes = self.bot.command_prefix(self.bot, after)
        if after.content.startswith(tuple(prefixes)):
            ctx = await self.bot.get_context(after)
            msg = await self.bot.invoke(ctx)

    @commands.Cog.listener('on_member_update')
    async def membership_screening_role(self, before, after):
        if before.pending is True and after.pending is False:
            await after.add_roles(after.guild.get_role(self.member_role), reason="Membership Screening Autorole")

    @tasks.loop(hours=1)
    async def clear_serious_chats(self):
        await self.bot.wait_until_ready()
        for x in self.serious_channels:
            channel = self.bot.get_channel(x)
            await channel.purge(limit=None, before=(datetime.datetime.now() - datetime.timedelta(days=7)), check=lambda k: not k.pinned)

    @tasks.loop(hours=12)
    async def recache_selfroles(self):
        await self.bot.wait_until_ready()
        self.bot.selfroles = await self.bot.db.roles.find({}).to_list(None)

    @commands.Cog.listener('on_message')
    async def introduction_reactions(self, message):
        if message.channel.id == self.introduction_channel and message.author.bot is False:
            await message.add_reaction(self.bot.get_emoji(865718455684562946))

    @commands.Cog.listener('on_message')
    async def feedback_dms(self, message):
        if message.guild is not None or message.content.startswith(tuple(self.bot.command_prefix(self.bot, message))) or message.author.bot:
            return
        await message.reply("This feedback DM system is coming soon! Please wait for excitement...\nYou can also contact <@443217277580738571> if you have any questions or concerns!")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(title='You broke it <:foxunamused:865733585600249876>', description=str(error), color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if interaction.component.id == "SERIOUS_ACCESS":
            member = interaction.guild.get_member(int(interaction.user.id))
            role = interaction.guild.get_role(self.serious_access_role)
            if role in member.roles:
                await member.remove_roles(role, reason="Serious Topic Access Button")
                await interaction.respond(content="You no longer have access to the Serious Topic channels! To get access again, press the button above.")
            else:
                await member.add_roles(role, reason="Serious Topic Access Button")
                await interaction.respond(content="You now have access to the Serious Topic channels! Please remember to follow the rules above or your access may be removed.")
        elif interaction.component.id == "MODERATION_POLICY":
            await interaction.respond(embed=message_embeds.moderation_policy)
        elif interaction.component.id == "NEWS_ROLE":
            member = interaction.guild.get_member(int(interaction.user.id))
            role = interaction.guild.get_role(self.news_role)
            if role in member.roles:
                await member.remove_roles(role, reason="News Button")
                await interaction.respond(content="You will no longer be pinged for updates in <#865915066032062464> :newspaper2:")
            else:
                await member.add_roles(role, reason="News Button")
                await interaction.respond(content="You will now be pinged for updates in <#865915066032062464> <:dogping:866348393893724160>")
        elif interaction.component.id == ("LIST_ROLES"):
            options = await self.bot.db.roles.find({}).to_list(None)
            selects = []
            for x in options:
                selects.append(SelectOption(label=x['name'], value=f"ROLE_LIST-{x['name']}"))
            await interaction.respond(content="Select the role category from the dropdown below.", components=[Select(placeholder="Select the category of roles you want to view.", options=selects)])
        elif interaction.component.id.startswith("ROLE_TOGGLE-"):
            member = self.bot.get_guild(int(interaction.guild.id)).get_member(int(interaction.user.id))
            role = interaction.guild.get_role(int(interaction.component.id.split('-')[1]))
            member_roles = [str(b.id) for b in member.roles]
            if role not in member.roles:
                await member.add_roles(role, reason="Pushed a Toggle Role Button")
                if str(role.id) not in member_roles:
                    member_roles.append(str(role.id))
            else:
                await member.remove_roles(role, reason="Pushed a Toggle Role Button")
                try:
                    member_roles.remove(str(role.id))
                except ValueError:
                    pass

            for x in self.bot.selfroles:
                if str(role.id) in x['roles']:
                    selfroles = x['roles']

            await update_selfrole_interaction(self, interaction, selfroles, member_roles)

    @commands.Cog.listener()
    async def on_select_option(self, interaction):
        if interaction.component.value.startswith("ROLE_LIST-"):
            for x in self.bot.selfroles:
                if x['name'] == interaction.component.value.split('-')[1]:
                    selfroles = x['roles']

            member_roles = [str(b.id) for b in (self.bot.get_guild(int(interaction.guild.id)).get_member(int(interaction.user.id))).roles]
            await update_selfrole_interaction(self, interaction, selfroles, member_roles)

def setup(bot):
    bot.add_cog(Events(bot))
