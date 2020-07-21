import re

import discord
import random
import asyncio
import pprint

import discord
from discord.ext import commands
from pprint import pprint

import checks

from common import cn_id_pattern


def typing_time(msg, seconds_per_char):
    return len(msg) * seconds_per_char


actors = [
    'fang',
    'trish',
]


async def actor_send(cn, msg, delay, typing):
    if delay:
        await asyncio.sleep(delay)

    async with cn.typing():
        await asyncio.sleep(typing)
        await cn.send(msg)


class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.is_mod()
    @commands.command(name='8ball')
    async def eightball(self, ctx, *, arg):
        r = random.Random(ctx.message.id)
        actor = r.choice(actors)
        if actor == self.bot.config['actor']:
            if actor == 'trish':
                response = random.choice([
                    'hmmmmmm',
                    '8ball,,',
                    'idk what do u think?',
                    'maybe!!',
                    'hard 2 say',
                    'lmfao',
                    'askdlfj;sdf no',
                ])
                typing = typing_time(response, 0.05) * random.uniform(0.8, 1.2)
                await actor_send(ctx.channel, response, random.uniform(0.5, 1.5), typing)
                return

            if actor == 'fang':
                response = random.choice([
                    'sure.',
                    'could be cool.',
                    'hell. yes.',
                    'I mean. I guess?',
                    'who cares.',
                    'no. what? no.',
                    'no way.',
                ])
                typing = typing_time(response, 0.05) * random.uniform(0.8, 1.2)
                await actor_send(ctx.channel, response, random.uniform(0.5, 1.5), typing)
                return



def setup(bot):
    eightball = EightBall(bot)
    bot.add_cog(eightball)
    bot.eightball = eightball
