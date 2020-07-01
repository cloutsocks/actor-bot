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

samples = '''errmm
please don't use slurs on the server
I'm pretty sure in any language you can change or add letters in words to get a swear
that's literally how letters work
Yeah
I mean in heats of arguments you could just mispell words and make it a curse
please don't use slurs on the server
@yaffle23  Sorry it was only for an example
The one that throws me off the most in spanish is ñ vs. n. Because I don't have a ñ key on my keyboard, but it can change the meaning of a sentence a lot.
Same with Russian weird
In mandarin too
yeah, I understand, it's just not a good example at all..
K
Like same words but if its a different.. heightness?
I mean even if you're typing in English, you need to be really careful when typing "duck" for example
Lol
año means year in Spanish. Ano means...something less appropriate.
Also the way you say your age is by saying "I have 30 years" or something like that.
Like my techer told a story where a guy tried asking wheres the toilet in mandarin and he said it abit different so it became “can i kiss you?” Or something like that
He didnt get the directions
Lol
But got a slap straight to the face
Oof
inflection languages are hard!
There was a point when I was in Japan where I was starting to get the hang of Japanese inflection, but I didn't have the vocabulary to actually practice it.
Like "I know how I would say this thing, I just don't know which words I would use."
Well...Japanese "inflection" is very...monotone?
I learn arabic too
I can read it but dont know a single thing about what it means
It's more like a lack of inflection in Japanese.
My first job I had was as a "translator"
And I translated things from arabic. But the thing is, I don't know arabic. So my job was basically profreader.
I worked with the translators who spoke arabic to make sure their words made sense in English.
That's actually what a lot of translation work is.
Oof
It's a really interesting job. You learn a lot!
Oh yeah i kinda do something like that with what my spanish speaking classmates write in english?
If they ask me, i can check if what they wrote is good'''.split('\n')


def typing_time(msg, seconds_per_char):
    return len(msg) * seconds_per_char


actors = [
    'fang',
    'naomi',
    'naser',
    'rosa',
    'stella',
    'trish',
    'tester'
]


async def actor_send(cn, msg, delay, typing):
    if delay:
        await asyncio.sleep(delay)

    async with cn.typing():
        await asyncio.sleep(typing)
        await cn.send(msg)

    # self.bot.loop.


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

        t = 0
        msg_queue = []

        for line in lines:
            line = line.strip()
            for actor in actors:
                label = f'{actor}:'
                if line.lower().startswith(label):
                    dialog = line[len(label):].strip()
                    mine = actor == self.bot.config["actor"]
                    r = random.uniform(0.8, 1.2)
                    typing = typing_time(dialog, 0.05) * r
                    msg_queue.append((mine, t, typing, dialog))

                    t += typing * 2
                    t += random.uniform(1.25, 2)

        if not msg_queue:
            return

        im_sending = False
        for entry in msg_queue:
            mine, t, typing, dialog = entry
            if mine:
                im_sending = True
                self.bot.loop.create_task(actor_send(cn, dialog, t, typing))

        if im_sending:
            await message.add_reaction('✅')

    # @checks.is_jacob()
    # @commands.command()
    # async def dx(self, ctx):
    #     ns = list(range(1, 4))
    #     for n in ns:
    #         # await actor_send(ctx.channel, str(n) + ' a passing message here', 2, 0.1)
    #         self.bot.loop.create_task(actor_send(ctx.channel, str(n) + ' a passing message here', 2, 0.1))

    # @checks.is_jacob()
    # @commands.command()
    # async def dt(self, ctx, n:int, spc:float):
    #     print('-----')
    #     for i in range(n):
    #         msg = random.choice(samples)
    #         r = random.uniform(0.8, 1.2)
    #         # spc = 0.025
    #         t = min(typing_time(msg, spc) * r, 2.5)
    #         print(msg, len(msg), t, r)
    #         async with ctx.channel.typing():
    #             await asyncio.sleep(t)
    #             await ctx.channel.send(msg) # + f' [{len(msg)}, {spc}, {t}]')
    #         await asyncio.sleep(random.uniform(0.5, 2))
    #     print('====')

def setup(bot):
    actor = Actor(bot)
    bot.add_cog(actor)
    bot.actor = actor
