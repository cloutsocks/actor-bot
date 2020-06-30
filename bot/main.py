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
    return ['.', ';', ',']


# naomi invite https://discordapp.com/api/oauth2/authorize?client_id=720740582288261150&permissions=2146827601&scope=bot
# rosa invite https://discordapp.com/api/oauth2/authorize?client_id=720741045008072704&permissions=2146827601&scope=bot
# dev kooper invite https://discordapp.com/api/oauth2/authorize?client_id=727284999585267753&permissions=2146827601&scope=bot

class ActorBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=command_prefixes)

        self.help_command = None

        self.config = None
        self.actor = None

        self.wfr = {}
        self.wfm = {}

        load_config(self)

        self.bound_extensions = [
            'common',
            'error',
            'config',
            'actor'
        ]

        if self.config['actor'] == 'naomi':
            self.bound_extensions.append('naomi')

        for extension in self.bound_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

    def clear_wait_fors(self, uid):
        self.wfr.pop(uid, None)
        self.wfm.pop(uid, None)


bot = ActorBot()

# @bot.check
# async def debug_restrict_jacob(ctx):
#     return ctx.message.author.id == 232650437617123328 or ctx.message.author.id == 340838512834117632


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    status = bot.config['playing']
    playing = discord.Game(name=status)
    bot.guild = bot.get_guild(bot.config['guild'])
    await bot.change_presence(activity=playing)


@bot.command(name='reloadall', aliases=['reall', 'ra'])
@checks.is_jacob()
async def _reloadall(ctx, arg=None):
    """Reloads all modules."""

    bot.wfm = {}
    bot.wfr = {}
    try:
        for extension in bot.bound_extensions:
            bot.unload_extension(extension)
            bot.load_extension(extension)
    except Exception as e:
        await ctx.send(f'```py\n{traceback.format_exc()}\n```')
    else:
        await ctx.send('✅')


print('Starting')
bot.run(bot.config['token'])
