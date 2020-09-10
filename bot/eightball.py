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
    'naomi'
]

filter_hw = re.compile(r'\bhw\b|home\s?work')


async def actor_send(cn, msg, delay, typing):
    if delay:
        await asyncio.sleep(delay)

    async with cn.typing():
        await asyncio.sleep(typing)
        await cn.send(msg)


class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='8ball')
    async def eightball(self, ctx, *, arg):

        if (match := filter_hw.search(arg)) is not None:
            return

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
                    'yaaaAAA A A  A  A'
                ])
                typing = typing_time(response, 0.05) * random.uniform(0.8, 1.2)
                await actor_send(ctx.channel, response, 0, typing)
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
                    '........'
                ])
                typing = typing_time(response, 0.05) * random.uniform(0.8, 1.2)
                await actor_send(ctx.channel, response, 0, typing)
                return

            if actor == 'naomi':
                response = random.choice([
                    'Absolutely.',
                    'I think so, yes!',
                    'Oh! That sounds right.',
                    'I\'m not sure I have an opinion on the matter.',
                    'I\'m so sorry, I\'m afraid I don\'t know!',
                    'I don\'t think so.',
                    'I would have to say no.',
                    'Absolutely not.',
                ])
                typing = typing_time(response, 0.05) * random.uniform(0.8, 1.2)
                await actor_send(ctx.channel, response, 0, typing)
                return




def setup(bot):
    eightball = EightBall(bot)
    bot.add_cog(eightball)
    bot.eightball = eightball
