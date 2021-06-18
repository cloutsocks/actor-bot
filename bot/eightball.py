import re

import discord
import random
import asyncio
import pprint

import discord
from discord.ext import commands
from pprint import pprint

import json
import gspread

import checks

from common import cn_id_pattern


def typing_time(msg, seconds_per_char):
    return len(msg) * seconds_per_char


actors = [
    'fang',
    'trish',
    'naomi',
    'naser',
    'reed',
    'rosa',
    'stella'
]

filter_hw = re.compile(r'\bhw\b|home\s?work')


async def actor_send(cn, msg, delay, typing):
    if delay:
        await asyncio.sleep(delay)

    async with cn.typing():
        await asyncio.sleep(typing)
        await cn.send(msg)

def load_8ball_answers(bot_id):
    with open('config/config_8ball.json') as f:
        config_8ball = json.load(f)

    gc = gspread.service_account(filename='config/service_account.json')
    spreadsheet = gc.open_by_key(config_8ball['sheet_key'])
    worksheet = spreadsheet.worksheet('8ball')

    bot_ids = [int(val) for val in worksheet.row_values(2)]

    try:
        cell = worksheet.find(str(bot_id))
    except gspread.exceptions.CellNotFound:
        print(f"Couldn't load 8ball values for id {bot_id}")
        return bot_ids, []

    answers = worksheet.col_values(cell.col)
    return bot_ids, [a for a in answers[2:] if a]


class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_mentions = []
        self.answers = []
        self.load_answers()

    @checks.is_mod()
    @commands.command(name='reload8ball')
    async def reload_answers(self, ctx):
        self.load_answers()
        if not self.answers:
            await ctx.send(f"Couldn't find any answers for {self.bot.config['id']}")
        else:
            await ctx.send(f'✅ Loaded {self.answers}')

    def load_answers(self):
        bot_ids, answers = load_8ball_answers(self.bot.config['id'])
        self.bot_mentions = [f'<@!{bot_id}>' for bot_id in bot_ids]
        self.answers = answers

    @commands.command(name='8ball')
    async def eightball(self, ctx, *, arg):

        if not self.answers:
            return

        if (match := filter_hw.search(arg)) is not None:
            return

        should_answer = False

        if any(bot_mention in ctx.message.content for bot_mention in self.bot_mentions):
            if str(self.bot.config['id']) in ctx.message.content:
                should_answer = True
        else:
            r = random.Random(ctx.message.id)
            actor = r.choice(actors)
            if actor == self.bot.config['actor']:
                should_answer = True

        if should_answer:
            response = random.choice(self.answers)
            typing = typing_time(response, 0.05) * random.uniform(0.8, 1.2)
            await actor_send(ctx.channel, response, 0, typing)

            # if actor == 'trish':
            #     response = random.choice([
            #         'hmmmmmm',
            #         '8ball,,',
            #         'idk what do u think?',
            #         'maybe!!',
            #         'hard 2 say',
            #         'lmfao',
            #         'askdlfj;sdf no',
            #         'yaaaAAA A A  A  A'
            #     ])
            #     typing = typing_time(response, 0.05) * random.uniform(0.8, 1.2)
            #     await actor_send(ctx.channel, response, 0, typing)
            #     return
            #
            # if actor == 'fang':
            #     response = random.choice([
            #         'sure.',
            #         'could be cool.',
            #         'hell. yes.',
            #         'I mean. I guess?',
            #         'who cares.',
            #         'no. what? no.',
            #         'no way.',
            #         '........'
            #     ])
            #     typing = typing_time(response, 0.05) * random.uniform(0.8, 1.2)
            #     await actor_send(ctx.channel, response, 0, typing)
            #     return
            #
            # if actor == 'naomi':
            #     response = random.choice([
            #         'Absolutely.',
            #         'I think so, yes!',
            #         'Oh! That sounds right.',
            #         'I\'m not sure I have an opinion on the matter.',
            #         'I\'m so sorry, I\'m afraid I don\'t know!',
            #         'I don\'t think so.',
            #         'I would have to say no.',
            #         'Absolutely not.',
            #     ])
            #     typing = typing_time(response, 0.05) * random.uniform(0.8, 1.2)
            #     await actor_send(ctx.channel, response, 0, typing)
            #     return




def setup(bot):
    eightball = EightBall(bot)
    bot.add_cog(eightball)
    bot.eightball = eightball
