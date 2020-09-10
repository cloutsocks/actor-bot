import re

import discord
import random
import os
import discord
import json
from discord.ext import commands

import checks


class Achievements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def award_role_achievement(self, channel, member, role, msg=None, how=None):

        if role in member.role:
            return

        await member.add_role(role)

        if msg is None:
            msg = f'{member.mention} has earned the **{role.name}** achievement role!'

        if how is not None:
            msg = f'{msg}\n*{how}'

        await channel.send(msg)
        await self.bot.get_channel(753419964035235890).send(msg)

def setup(bot):
    config_cog = Achievements(bot)
    bot.add_cog(config_cog)
