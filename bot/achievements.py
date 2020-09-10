import re

import discord
import random
import os
import discord
import json
from discord.ext import commands

import checks

from common import FIELD_BREAK, RAINBOW_PALETTE


class Achievements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def award_role_achievement(self, channel, member, role, msg=None, how=None):

        if role in member.roles:
            return

        await member.add_roles(role)

        description = msg
        if msg is None:
            description = f' 🎊 ✨   {member.mention} has earned the **{role.name}** achievement role!   ✨ 🎊 '

        if how is not None:
            description = f'{description}\n{how}'

        color = random.choice(RAINBOW_PALETTE)
        e = discord.Embed(description=description, color=color)

        sent = await channel.send('', embed=e)
        log = await self.bot.get_channel(753419964035235890).send('', embed=e)

        for reaction in ['<:GVHtrishyay:721410319494152243>', '<:lovehonk:722884312378376192>']:
            await sent.add_reaction(reaction.strip('<>'))
            await log.add_reaction(reaction.strip('<>'))



def setup(bot):
    achievements = Achievements(bot)
    bot.add_cog(achievements)
    bot.achievements = achievements
