
import discord
import checks
import random
import asyncio
import io
import time
import os
import math
import sqlite3
import json
import secrets

from discord.ext import commands
from common import DBL_BREAK, RAINBOW_PALETTE, FIELD_BREAK

from PIL import Image
from peewee import *
from datetime import datetime


ICON_BACK = '<:navarrowleft:748735550206378116>'
ICON_FORWARD = '<:navarrowright:748735550260772905>'
ICON_CLOSE = '❌'

ICON_BOOK = '📕'
ICON_STICKERS = '🖼️'

SLOT = '<:slot:765974192607854683>'

user_db = SqliteDatabase('yb_users.db')

class BaseModel(Model):
    class Meta:
        database = user_db


class Stickers(BaseModel):
    discord_id = IntegerField(unique=True)
    handle = CharField(null=True)
    guild_id = IntegerField()
    stickers = CharField(null=True)


def create_tables():
    with user_db:
        user_db.create_tables([Stickers])


class Yearbook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.paused = False
        self.stickers = {}
        self.nos = {}
        self.sets = {}
        self.load_stickers()
        self.render = Render()

    @commands.command(aliases=['yb'])
    async def yearbook(self, ctx, *, arg=''):
        if self.paused:
            await ctx.send('yearbook paused')
            return

        session = YearbookSession(self.bot, ctx.author)
        session.load_from_db()

        if session.sticker_row.stickers is None:
            sticker_pull = secrets.choice(self.sets[1])
            session.sticker_row.stickers = json.dumps([sticker_pull])
            session.sticker_row.save()
            await self.sticker_notification(ctx.channel, ctx.author, sticker_pull, how='Open your yearbook for the very first time.')

        await ctx.trigger_typing()
        await session.build_and_send_message(ctx)

    @checks.is_jacob()
    @commands.command()
    async def make_stickers_db(self, ctx):
        create_tables()

    def load_stickers(self):
        db = sqlite3.connect('yb_readonly.db')
        c = db.cursor()
        rows = c.execute('select * from stickers order by no asc').fetchall()
        fields = list(map(lambda d: d[0], c.description))
        db.close()

        self.stickers = {}
        self.sets = {}
        for row in rows:
            data = {}
            no, key = row[0], row[3]
            for i, value in enumerate(row):
                if i == 0:
                    continue
                data[fields[i]] = value

            self.stickers[no] = data
            self.nos[key] = no

            if not data['set'] in self.sets:
                self.sets[data['set']] = []

            self.sets[data['set']].append(no)

    async def sticker_notification(self, channel, member, sticker, msg=None, how=None):

        description = msg
        if msg is None:
            description = f'{member.mention} earned a sticker!!'

        if how is not None:
            description = f'{description}{DBL_BREAK}_{how}_'

        color = random.choice(RAINBOW_PALETTE)
        e = discord.Embed(description=description, color=color)
        image = self.stickers[sticker]['image']
        e.set_thumbnail(url=image)

        sent = await channel.send('', embed=e)

        achievement_cn = self.bot.get_channel(753419964035235890)
        if achievement_cn is not None:
            log = await achievement_cn.send('', embed=e)

            for reaction in ['<:GVHtrishyay:721410319494152243>', '<:lovehonk:722884312378376192>']:
                # await sent.add_reaction(reaction.strip('<>'))
                await log.add_reaction(reaction.strip('<>'))

    @commands.command(aliases=['tr'])
    async def test_render(self, ctx, *, arg=''):

        if not arg:
            stickers = list(positions.keys())
        else:
            stickers = arg.split(' ')

        await ctx.trigger_typing()
        t = time.time()
        png = self.render.render_stickers('memories_page', stickers)
        e = discord.Embed(description='text').set_image(url='attachment://yb.png').set_footer(text='footer')
        sent = await ctx.send(f'Took {time.time() - t:.3f} seconds', embed=e,
                                          file=discord.File(png, 'yb.png'))

    # async def view_sticker_page(self):
    #     uid = message.author.id
    #     userPc = self.cache[uid]
    #     page = page or userPc['page']
    #     ns, text = self.page_text(page, userPc['badges'], userPc['sort'])
    #
    #     await message.channel.trigger_typing()
    #     t = time.time()
    #     footer = 'Type `z` to go back, `x` to go forward, or a page # such as `4`'
    #
    #     if not uid in self.imgcache:
    #         self.imgcache[uid] = {}
    #
    #     if page in self.imgcache[uid]:
    #         cacheImg, cacheNs = self.imgcache[uid][page]
    #
    #         # async with self.bot.session.head(self.imgcache[uid][page]) as resp:
    #         #     print(resp)
    #
    #         if ns == cacheNs:
    #             e = discord.Embed(description=text).set_image(url=cacheImg).set_footer(text=footer)
    #             await message.channel.send(f'<@{uid}> Took {time.time() - t:.3f} seconds [link]', embed=e)
    #             return
    #
    #     png = self.bot.render.render_pc(ns)
    #     e = discord.Embed(description=text).set_image(url='attachment://pc.png').set_footer(text=footer)
    #     sent = await message.channel.send(f'<@{uid}> Took {time.time() - t:.3f} seconds', embed=e, file=discord.File(png, 'pc.png'))
    #     self.imgcache[uid][page] = (sent.embeds[0].image.url, ns)



    async def view_stickers(self, ctx, member=None):
        member = member or ctx.author

        # await ctx.trigger_typing()

        n = 9
        total = 9

        description = f'''_Memories_
Collected: **{9}** / **{9}** (**{(n / total) * 100:.1f}**%) ✨
Sets: **{2}** / **{2}** (**{(2 / 2) * 100:.1f}**%) ✨'''

        # .set_image(url=img) \

        __ = '    \u200b'

        e = discord.Embed(title=f'{member.name}\'s Yearbook', description=description)
            # .add_field(name=f'Base Set{__}', value='''<:FlamingGuitar:765958443558633502> <:slot:765974192607854683> <:FangHorns:765958443357437952>''', inline=True) \
            # .add_field(name=f'VVORM DRAMA{__}', value='<:reed_base:765975294082678845> <:slot:765974192607854683> <:trish_base:765975294069833749> <:naser_base:765975294237868062> <:slot:765974192607854683> <:slot:765974192607854683>', inline=True) \

        e.add_field(name=f'Base Set',
                   value='<:fang_base:766314258589810729> <:trish_base:766314258777505792> <:naomi_base:766314258715508736> <:naser_base:766314258362925166> <:reed_base:766314258689556500> <:rosa_base:766314258681692170> <:stella_base:766314258765709402>',
                   inline=False)
        e.add_field(name=f'VVORM DRAMA',
                       value='<:FangHorns:765958443357437952> <:FlamingGuitar:765958443558633502> <:VVORMDRAMA:765958443416682556>',
                       inline=False)

        e.set_image(url='https://cdn.discordapp.com/attachments/765955427594403900/766317825068498965/unknown.png')
        e.set_footer(text='🦖 Memories • Page 80')

        msg = await ctx.send(f'<@{ctx.author.id}>', embed=e)

        for reaction in [ICON_BOOK, ICON_STICKERS, ICON_BACK, ICON_FORWARD]:
            await msg.add_reaction(reaction.strip('<>'))


class YearbookSession(object):
    def __init__(self, bot, member):
        self.bot = bot
        self.member = member
        self.sticker_row = None
        # page info etc

        self.wfr_message = None

    def load_from_db(self):
        try:
            self.sticker_row = Stickers.select().where(Stickers.discord_id == self.member.id).get()
        except Stickers.DoesNotExist:
            guild_id = self.member.guild.id if self.member.guild is not None else None

            # todo sticker award
            self.sticker_row = Stickers(discord_id=self.member.id,
                              handle=str(self.member),
                              guild_id=guild_id)

            self.sticker_row.save()

            # todo update after

    async def handle_reaction(self, reaction, user):
        emoji = str(reaction.emoji)
        pass

    async def build_and_send_message(self, ctx):
        e, file = self.make_stickers_embed()
        text = '''Oh! Here are the stickers you've collected so far! You can get them all sorts of ways—achievements, being nice, participating in events, and more.'''
        self.wfr_message = await ctx.send(f'<@{ctx.author.id}> {text}', embed=e, file=file)

        # if not self.wfr_message:
        #     self.wfr_message = await ctx.send(f'<@{ctx.author.id}>', embed=e, file=file)
        # else:
        #     await self.wfr_message.edit(embed=e)
        # reactions = ['❓']
        # # if not self.daily_claimed():
        # reactions += [daily_reading['emoji']]
        # reactions += list(reactions_format_map.keys())
        # for reaction in reactions:
        #     await self.wfr_message.add_reaction(reaction.strip('<>'))
        #     self.bot.wfr[self.member.id] = self

    def make_stickers_embed(self):

        self.load_from_db()

        if self.sticker_row.stickers is None:
            stickers = []
        else:
            stickers = json.loads(self.sticker_row.stickers)
            stickers.sort()

        total_stickers = len(self.bot.yearbook.stickers)
        total_sets = len(self.bot.yearbook.sets)
        collected = len(stickers)
        completed = 0


        field_texts = []
        for set_no, set_contents in self.bot.yearbook.sets.items():
            complete = all(no in stickers for no in set_contents)
            if complete:
                completed += 1

            emojis = []
            for no in set_contents:
                if no in stickers:
                    emojis.append(self.bot.yearbook.stickers[no]['emoji'])
                else:
                    emojis.append(SLOT)

            field_texts.append(' '.join(emojis))

        description = f'''_Memories_
Collected: **{collected}** / **{total_stickers}** (**{(collected / total_stickers) * 100:.1f}**%) ✨
Sets: **{completed}** / **{total_sets}** (**{(completed / total_sets) * 100:.1f}**%) ✨'''
        # .set_image(url=img) \

        __ = '    \u200b'

        e = discord.Embed(title=f'{self.member.name}\'s Yearbook', description=description)

        e.add_field(name=f'Base Set',
                    value=field_texts[0],
                    inline=False)
        e.add_field(name=f'VVORM DRAMA',
                    value=field_texts[1],
                    inline=False)

        # e.set_image(url='https://cdn.discordapp.com/attachments/765955427594403900/766317825068498965/unknown.png')
        e.set_footer(text='🦖 Memories • Page 80')

        sticker_keys = [self.bot.yearbook.stickers[sticker]['key'] for sticker in stickers]

        png = self.bot.yearbook.render.render_stickers('memories_page', sticker_keys)
        e.set_image(url='attachment://yb.png')

        return e, discord.File(png, 'yb.png')


positions = {
    'fang': [1101, 729],
    'trish': [1415, 1368],
    'naomi': [1493, 398],
    'naser': [1492, 904],
    'reed': [1865, 1123],
    'rosa': [1937, 636],
    'stella': [1911, 123],
    'fang_horns': [324, 1068],
    'flaming_guitar': [534, 1321],
    'vvormdrama': [642, 1083],
}

class Render():
    def __init__(self):
        self.images = {}

        self.images['memories_page'] = Image.open(f'yearbook/tiny/memories_page.png').convert('RGBA')
        path = 'yearbook/tiny/common'
        for fn in os.listdir(path):
            self.images[fn[:-4] + '_common'] = Image.open(f'{path}/{fn}').convert('RGBA')

    def render_stickers(self, canvas, stickers):

        canvas = self.images[canvas].copy()

        for i, sticker in enumerate(stickers):
            try:
                img = self.images[f'{sticker}_common']
                position = positions[sticker]
            except KeyError:
                continue

            canvas.paste(img, position, img)

        png = io.BytesIO()
        canvas.save(png, format='PNG', optimize=False)
        png.seek(0)
        return png

def setup(bot):
    yearbook = Yearbook(bot)
    bot.add_cog(yearbook)
    bot.yearbook = yearbook
