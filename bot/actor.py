import re

import discord
import random

import discord
from discord.ext import commands

import checks

from common import cn_id_pattern

class Actor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        uid = message.author.id
        if uid not in self.bot.config['admin_ids']:
            return

        content = message.content
        if (match := re.match(cn_id_pattern, content)) is None:
            return

        channel_id = int(match.group(1))
        cn = self.bot.guild.get_channel(channel_id)

        if not isinstance(cn, discord.TextChannel):
            await message.channel.send(f'Could not find channel {match}')
            return

        content = content[len(match.group(0)):]
        lines = content.split('\n')
        sent = False
        for line in lines:
            line = line.strip()
            actor = f'{self.bot.config["actor"]}:'
            if line.lower().startswith(actor):
                dialog = line[len(actor):].strip()
                sent = True
                await cn.send(dialog)

        if sent:
            await message.add_reaction('✅')



    # @checks.is_bot_admin()
    # @commands.command()
    # async def _test(self, ctx, channel: discord.TextChannel, *, arg):
    #     print(f'{channel} {arg}')
    #     await ctx.message.add_reaction('✅')

def setup(bot):
    actor = Actor(bot)
    bot.add_cog(actor)
    bot.actor = actor
