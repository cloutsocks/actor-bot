import re

import discord
import random
import os
import discord
import json
from discord.ext import commands

import checks

from common import FIELD_BREAK


class Achievements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def award_role_achievement(self, channel, member, role, msg=None, how=None):

        if role in member.roles:
            return

        await member.add_roles(role)

        if msg is None:
            msg = f'{member.mention} has earned the **{role.name}** achievement role!'

        if how is not None:
            msg = f'{msg}\n{how}'

        msg = f'{msg}{FIELD_BREAK}'

        sent = await channel.send(msg)
        log = await self.bot.get_channel(753419964035235890).send(msg)

        for reaction in ['<:GVHtrishyay:721410319494152243>', '<:lovehonk:722884312378376192>']:
            await sent.add_reaction(reaction.strip('<>'))
            await log.add_reaction(reaction.strip('<>'))


def setup(bot):
    achievements = Achievements(bot)
    bot.add_cog(achievements)
    bot.achievements = achievements
