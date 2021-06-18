import json
import os
import sys
import time
import traceback
import datetime
import asyncio
import re

import discord
from discord.ext import commands

import checks
from config import load_config


def command_prefixes(bot, message):
    if bot.user.id == 727284999585267753:
        return ['\'']
    return ['.', ';', ',']


# naomi invite https://discordapp.com/api/oauth2/authorize?client_id=720740582288261150&permissions=2146827601&scope=bot
# rosa invite https://discordapp.com/api/oauth2/authorize?client_id=720741045008072704&permissions=2146827601&scope=bot
# dev kooper invite https://discordapp.com/api/oauth2/authorize?client_id=727284999585267753&permissions=2146827601&scope=bot


class ActorBot(commands.Bot):
    def __init__(self):

        intents = discord.Intents.default()  # All but the two privileged ones
        intents.members = True  # Subscribe to the Members intent

        super().__init__(command_prefix=command_prefixes, intents=intents)

        self.help_command = None

        self.config = None
        self.actor = None
        self.achievements = None

        self.wfr = {}
        self.wfm = {}

        load_config(self)

        self.exts = [
            'common',
            'error',
            'config',
            'admin',
            'actor',
            'achievements',
        ]


        # todo move to extensions config
        if self.config['actor'] == 'tester':
            pass
            # self.exts.append('naomi')

        if self.config['actor'] == 'trish':
            self.exts.append('jam')

        if self.config['actor'] == 'rosa':
            self.exts.append('halloween')

        if self.config['actor'] == 'naomi':
            self.exts.append('naomi')
            self.exts.append('yearbook')

        if self.config['actor'] == 'stella':
            self.exts.append('stella')

        if 'eightball' in self.config:
            self.exts.append('eightball')


        for extension in self.exts:
            self.load(extension)

    def clear_wait_fors(self, uid):
        self.wfr.pop(uid, None)
        self.wfm.pop(uid, None)

    def load(self, extension):
        try:
            self.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

    async def process_commands(self, message):
        ctx = await self.get_context(message)
        await self.invoke(ctx)



bot = ActorBot()


# @bot.check
# async def debug_restrict_jacob(ctx):
#     return ctx.message.author.id == 232650437617123328 or ctx.message.author.id == 340838512834117632


@bot.check
async def no_dms(ctx):
    return ctx.guild is not None


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    status = bot.config['playing']
    playing = discord.Game(name=status)
    bot.guild = bot.get_guild(bot.config['guild'])
    await bot.change_presence(activity=playing)

    print(bot.exts)

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    if user.id in bot.wfr and bot.wfr[user.id].wfr_message.id == reaction.message.id:
        await bot.wfr[user.id].handle_reaction(reaction, user)
        await reaction.message.remove_reaction(reaction, user)


print('Starting')
bot.run(bot.config['token'])
