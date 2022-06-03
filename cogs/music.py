import discord, datetime, wavelink
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rythm_bot = 252128902418268161
        self.voice_channel = 865917963873943582
        self.youtube_playlist = "https://www.youtube.com/playlist?list=PLJOPfulPgJe5EjMv38cJmwz48kN3H_Hpi"

    @commands.Cog.listener('on_voice_state_update')
    async def pause_when_rythm(self, member, before, after):
        if before == after or member.id == self.bot.user.id:
            return
        if member.id == self.rythm_bot:
            if before.channel is None:
                player = self.bot.wavelink.get_player(member.guild.id)
                await player.set_pause(True)
            elif after.channel is None or after.channel.id != self.voice_channel:
                player = self.bot.wavelink.get_player(member.guild.id)
                await player.set_pause(False)
        else:
            if before.channel is not None and before.channel.id == self.voice_channel:
                if len(before.channel.members) == 1:
                    player = self.bot.wavelink.get_player(member.guild.id)
                    await player.set_pause(True)
            elif after.channel is not None and after.channel.id == self.voice_channel:
                player = self.bot.wavelink.get_player(member.guild.id)
                await player.set_pause(False)


    @commands.Cog.listener('on_ready')
    async def connect_to_vc(self):
        await self.bot.wavelink.initiate_node(host='lava.link', port=80, rest_uri='http://lava.link:80', password='bremea smell', identifier='i am duck man', region='us_east')
        player = self.bot.wavelink.get_player(865711881075163166)
        await player.connect(self.voice_channel)
        playlist = await self.bot.wavelink.get_tracks(self.youtube_playlist)
        for x in playlist.tracks:
            await player.play(x)

def setup(bot):
    bot.add_cog(Music(bot))
