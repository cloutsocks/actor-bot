
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
import re

from discord.ext import commands
from common import DBL_BREAK, RAINBOW_PALETTE, FIELD_BREAK, send_message, clamp, ERROR_RED, get_member_or_search

from PIL import Image
from peewee import *
from datetime import datetime

import random
import sqlite3
import difflib

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from fractions import Fraction

ICON_BACK = '<:navarrowleft:748735550206378116>'
ICON_FORWARD = '<:navarrowright:748735550260772905>'
ICON_CLOSE = '❌'
ICON_REFRESH = '♻'
ICON_CONFIRM = '✅'

ICON_BOOK = '📕'
ICON_STICKERS = '🖼️'

SLOT = '<:slot:765974192607854683>'

IMG_YB_FRONT = 'https://i.imgur.com/YoP3j3r.png' #'https://i.imgur.com/NTG5s8n.png'

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

def load_stickers_for(member, create_on_fail):
    try:
        sticker_row = Stickers.select().where(Stickers.discord_id == member.id).get()
    except Stickers.DoesNotExist:
        if not create_on_fail:
            return None

        guild_id = member.guild.id if member.guild is not None else None
        sticker_row = Stickers(discord_id=member.id,
                               handle=str(member),
                               guild_id=guild_id)
        sticker_row.save()

    if sticker_row.stickers is None:
        stickers = []
    else:
        stickers = json.loads(sticker_row.stickers)
        stickers.sort()

    return sticker_row, stickers


class Yearbook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.paused = False
        self.stickers = {}
        self.nos = {}
        self.sets = {}
        self.names = {}
        self.sticker_names_lower = {}
        self.load_stickers()
        self.render = Render()
        self.img_cache = {
            'stickers': {}
        }

        self.toc_cache = {}

        self.trades = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.author.id not in self.trades:
            return

        trade = self.trades[message.author.id]
        if message.channel != trade.wfr_message.channel:
            return

        text = message.content.lower().strip()
        if text in self.sticker_names_lower:
            no = self.sticker_names_lower[text]
            await trade.attempt_to_add(message.author, no)
            await message.delete()

    @checks.is_jacob()
    @commands.command(name='ybpause')
    async def yearbook_pause(self, ctx):
        self.paused = not self.paused
        await ctx.send(f'`paused = {self.paused}`')

    @commands.command(aliases=['yb', 'memories', 'stickers'])
    async def yearbook(self, ctx, *, arg=''):
        if self.paused:
            await ctx.send('Oh! Apologies, I\'m organizing a couple of things! Yearbooks will be back soon.')
            return

        session = YearbookSession(self.bot, ctx.author)
        session.load_from_db()

        if session.sticker_row.stickers is None:
            sticker_pull = secrets.choice(self.sets[1])
            session.sticker_row.stickers = json.dumps([sticker_pull])
            session.sticker_row.save()
            await self.sticker_notification(ctx.channel, ctx.author, sticker_pull, how='Open your yearbook for the very first time.')

        session.update_toc()
        await ctx.trigger_typing()

        if ctx.invoked_with == 'memories' or ctx.invoked_with == 'stickers':
            target_page = session.find_page_by_section_name('memories')
            await session.view_page_no(target_page, ctx)
            return

        # toc
        if not arg:
            await session.view_page_no(0, ctx)
            return

        # page number
        target_page = None
        try:
            target_page = int(arg) - 1
        except ValueError:
            pass

        if target_page is not None:
            await session.view_page_no(target_page, ctx)
            return

        # category search
        target_page = session.find_page_by_section_name(arg)
        if target_page is not None:
            await session.view_page_no(target_page, ctx)
            return

        # sticker search
        matches = process.extractBests(re.sub(r'[().\- ]', '', arg), self.names.keys(), limit=15,
                                       score_cutoff=50,
                                       processor=lambda x: re.sub(r'[().\- ]', '', x))
        top_matches = [match for match in matches if match[1] > 85]
        if top_matches and (len(top_matches) == 1 or top_matches[0][1] > 98):
            no = self.names[top_matches[0][0]]
        else:
            matches = '\n'.join([f'_{match[0]}_' for match in matches])
            text = f'''<@{ctx.author.id}> I couldn't find that page!'''
            if matches:
                text = f'{text} Did you mean:{DBL_BREAK}{matches}'
            # await send_message(ctx, text, color=ERROR_RED, expires=15)
            await ctx.send(text, delete_after=15)
            return

        await session.view_page_no(no + 100, ctx)

    @checks.is_mod()
    @commands.command()
    async def give(self, ctx, *, arg):
        if self.paused:
            await ctx.send('Oh! Apologies, I\'m organizing a couple of things! Yearbooks will be back soon.')
            return

        set_keys = ['base', 'vvordrama']
        sticker_keys = list(self.nos.keys())

        set_text = ' '.join(f'`{key}`' for key in set_keys)
        sticker_text = ' '.join(f'`{key}`' for key in sticker_keys)

        how_to = f'''Proper usage: `.give <user> <any|base|fang> <reason>`
e.g. `.give @jacob trish Always a delight and exceedingly handsome.`

Current Sets: {set_text}
Current Stickers: {sticker_text}'''

        try:
            query, pool_query, rest = arg.split(' ', 2)
            pool_query = pool_query.lower().strip()
        except ValueError:
            await send_message(ctx, how_to, error=True)
            return

        # find member
        success, result = await get_member_or_search(self.bot, ctx.guild, query, include_pings=False, members_only=True)
        if not success:
            await send_message(ctx, f'{result}{DBL_BREAK}{how_to}', error=True)
            return
        member = result

        reason = None
        channel = None
        try:
            cid, reason = rest.split(' ', 1)
            channel = self.bot.get_channel(int(cid))
        except (ValueError, TypeError) as e:
            pass

        if channel is None:
            reason = rest
            channel = ctx.channel

        # load member sticker data
        sticker_row, stickers = load_stickers_for(member, True)

        # todo update toc without session

        # any
        if pool_query == 'any':
            pool = list(set(self.stickers.keys()) - set(stickers))
            if not pool:
                await send_message(ctx, f'{member} already has every sticker!', error=True)
                return

            sticker_pull = secrets.choice(pool)
            stickers.append(sticker_pull)
            stickers.sort()
            sticker_row.stickers = json.dumps(stickers)
            sticker_row.save()
            await self.sticker_notification(channel, member, sticker_pull, how=reason)
            return

        # specific sticker
        elif pool_query in self.nos:
            sticker_pull = self.nos[pool_query]
            if sticker_pull in stickers:
                await send_message(ctx, f'{member} already has the {pool_query} sticker :(', error=True)
                return
            stickers.append(sticker_pull)
            stickers.sort()
            sticker_row.stickers = json.dumps(stickers)
            sticker_row.save()
            await self.sticker_notification(channel, member, sticker_pull, how=reason)
            return

        # from set
        elif pool_query in set_keys:
            set_no = set_keys.index(pool_query) + 1
            pool = list(set(self.sets[set_no]) - set(stickers))
            if not pool:
                await send_message(ctx, f'{member} already has every sticker in the {pool_query} set :(', error=True)
                return

            sticker_pull = secrets.choice(pool)
            stickers.append(sticker_pull)
            stickers.sort()
            sticker_row.stickers = json.dumps(stickers)
            sticker_row.save()
            await self.sticker_notification(channel, member, sticker_pull, how=reason)
            return

        await send_message(ctx, f'''Couldn't find the sticker or set named `{pool_query}`{DBL_BREAK}{how_to}''', error=True)
        return

    @commands.command()
    async def trade(self, ctx, *, arg=''):
        if self.paused:
            await ctx.send('Oh! Apologies, I\'m organizing a couple of things! Yearbooks will be back soon.')
            return

        how_to = 'Type `.trade <user>` to begin a trade with them!'
        if not arg:
            await send_message(ctx, f'<@{ctx.author.id}> {how_to}', error=True)
            return

        success, result = await get_member_or_search(self.bot, ctx.guild, arg, include_pings=False, members_only=True)
        if not success:
            await send_message(ctx, f'<@{ctx.author.id}> {result}{DBL_BREAK}{how_to}', error=True)
            return

        member_a = ctx.author
        member_b = result

        # stop if in trade that isn't stale
        t = time.time()
        if member_a.id in self.trades:
            old_trade = self.trades[member_a.id]
            if t > old_trade.expires:
                del self.trades[old_trade.member_a.id]
                del self.trades[old_trade.member_b.id]
            else:
                await ctx.send(f'<@{ctx.author.id}> You already have an active trade here: {old_trade.wfr_message.jump_url}{DBL_BREAK}Either cancel it with {ICON_CLOSE}, complete it, or wait for time to run out.')
                return

        if member_b.id in self.trades:
            old_trade = self.trades[member_b.id]
            if t > old_trade.expires:
                del self.trades[old_trade.member_a.id]
                del self.trades[old_trade.member_b.id]
            else:
                await ctx.send(f'<@{member_b.id}> already has an active trade here: {old_trade.wfr_message.jump_url}{DBL_BREAK}Either cancel it with {ICON_CLOSE}, complete it, or wait for time to run out.')
                return

        # load stickers for each party
        result = load_stickers_for(member_a, False)
        if result is None:
            # await send_message(ctx, f'<@{ctx.author.id}> You don\'t have any stickers to trade :( Why not try opening your `.yearbook`?', error=True)
            await ctx.send(f'<@{ctx.author.id}> You don\'t have any stickers to trade :( Why not try opening your `.yearbook`?')
            return
        sticker_row_a, inv_a = result

        result = load_stickers_for(member_b, False)
        if result is None:
            # await send_message(ctx, f'<@{member_b.id}> doesn\'t have any stickers to trade :( Why not try opening your `.yearbook`?', error=True)
            await ctx.send(f'<@{member_b.id}> doesn\'t have any stickers to trade :( Why not try opening your `.yearbook`?')
            return
        sticker_row_b, inv_b = result

        trade = Trade(self.bot, member_a, member_b)
        await trade.make_and_send(ctx, inv_a, inv_b)
        self.trades[member_a.id] = self.trades[member_b.id] = trade


    # @commands.command(name='lookup', aliases=['l'])
    # async def lookup(self, ctx, *, arg=''):
    #     if not arg:
    #         return
    #
    #     matches = process.extractBests(re.sub(r'[().\- ]', '', arg), self.names.keys(), limit=15,
    #                                    score_cutoff=50,
    #                                    processor=lambda x: re.sub(r'[().\- ]', '', x))
    #     top_matches = [match for match in matches if match[1] > 85]
    #     if top_matches and (len(top_matches) == 1 or top_matches[0][1] > 98):
    #         no = self.names[top_matches[0][0]]
    #     else:
    #         matches = '\n'.join([f'_{match[0]}_' for match in matches])
    #         await send_message(ctx, f'''I couldn't find that page! Did you mean:{DBL_BREAK}{matches}''', color=ERROR_RED, expires=15)
    #         return
    #
    #     await send_message(ctx, top_matches[0][0])
    #
    #     # await self.view_entry(ctx, no)

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
            self.names[data['name']] = no
            self.sticker_names_lower[data['name'].lower()] = no

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
        e = discord.Embed(title=self.stickers[sticker]['name'], description=description, color=color)
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

        # for reaction in [ICON_BOOK, ICON_STICKERS, ICON_BACK, ICON_FORWARD]:
        #     await msg.add_reaction(reaction.strip('<>'))


class YearbookSession(object):
    def __init__(self, bot, member):
        self.bot = bot
        self.yb = bot.yearbook
        self.member = member
        self.sticker_row = None
        self.page_no = None
        # page info etc

        self.wfr_message = None

    def load_from_db(self):
        sticker_row, stickers = load_stickers_for(self.member, True)
        self.sticker_row = sticker_row

    def update_toc(self):
        if not self.sticker_row:
            self.load_from_db()

        toc = [
            ('toc', None),
            ('memories', 0)
        ]

        if self.sticker_row.stickers is not None:
            stickers = json.loads(self.sticker_row.stickers)
            stickers.sort()

            for s in stickers:
                toc.append(('stickers', s))

        self.yb.toc_cache[self.member.id] = toc

    async def handle_reaction(self, reaction, user):
        emoji = str(reaction.emoji)
        channel = reaction.message.channel

        # if emoji == ICON_STICKERS:
        #     await self.show_stickers(channel)
        # elif emoji == ICON_BACK:
        #     if self.page_no == 101:
        #         await self.show_stickers(channel)
        #     elif self.page_no > 101:
        #         self.page_no -= 1
        #         e = self.make_individual_sticker_embed(self.page_no - 100)
        #         await self.wfr_message.edit(embed=e, file=None)
        # elif emoji == ICON_FORWARD:
        #     if self.page_no < 110:
        #         if self.page_no < 101:
        #             self.page_no = 101
        #         else:
        #             self.page_no += 1
        #         e = self.make_individual_sticker_embed(self.page_no - 100)
        #         await self.wfr_message.edit(embed=e, file=None)


        # if emoji == ICON_STICKERS:
        #     await self.view_page_no(80, channel)
        # elif emoji == ICON_BACK:
        #     target_page = self.page_no - 1
        #     if target_page < 101:
        #         target_page = 80
        #     await self.view_page_no(target_page, channel)
        # elif emoji == ICON_FORWARD:
        #     target_page = self.page_no + 1
        #     if target_page < 101:
        #         target_page = 101
        #     await self.view_page_no(target_page, channel)

        if emoji == ICON_BOOK:
            await self.view_page_no(0, channel)
        elif emoji == ICON_STICKERS:
            await self.view_page_no(self.find_page_by_section_name('memories'), channel)
        elif emoji == ICON_BACK:
            await self.view_page_no(self.page_no - 1, channel)
        elif emoji == ICON_FORWARD:
            await self.view_page_no(self.page_no + 1, channel)

        # if emoji == ICON_STICKERS:
        #     await self.view_page_no(80, channel)
        # elif emoji == ICON_BACK:
        #     target_page = self.page_no - 1
        #     if target_page < 101:
        #         target_page = 80
        #     await self.view_page_no(target_page, channel)
        # elif emoji == ICON_FORWARD:
        #     target_page = self.page_no + 1
        #     if target_page < 101:
        #         target_page = 101
        #     await self.view_page_no(target_page, channel)

    def find_page_by_section_name(self, name):
        name = name.lower().strip()
        if self.member.id not in self.yb.toc_cache:
            self.update_toc()

        # todo proper search, return and combine results

        toc = self.yb.toc_cache[self.member.id]
        for index, page_data in enumerate(toc):
            if page_data[0] == name:
                return index

        return None

    async def view_page_no(self, page_no, messageable):

        if self.member.id not in self.yb.toc_cache:
            self.update_toc()

        toc = self.yb.toc_cache[self.member.id]

        target_page_no = clamp(page_no, 0, len(toc) - 1)

        if target_page_no != self.page_no:
            self.page_no = target_page_no
            category, data = toc[target_page_no]

            if category == 'toc':
                # show toc
                e = self.make_toc_embed()
                text = f'''This is your very own yearbook! It'll expand over time.{DBL_BREAK}You can use the arrows or icons to navigate pages and sections, or also jump to or search for individual pages with `.yb 105` / `.yb memories` / `.yb Fang`!'''
                await self.send_or_edit_message(e, text, messageable)

            elif category == 'memories':
                e = await self.make_stickers_embed()
                text = f'''Oh! Here are the stickers you've collected so far! You can get them all sorts of ways—achievements, being nice, participating in events, and more.{DBL_BREAK}You can also use `.memories` to jump here directly.'''
                await self.send_or_edit_message(e, text, messageable)

            elif category == 'stickers':
                e = self.make_individual_sticker_embed(int(data))
                text = '''You can also jump to or search for individual pages with `.yb 105` or `.yb Fang`!'''
                await self.send_or_edit_message(e, text, messageable)


    # async def view_page_no_old(self, page_no, messageable):
    #
    #     target_page = page_no
    #     # show stickers
    #     if target_page < 101:
    #         target_page = 80
    #         if target_page != self.page_no:
    #             self.page_no = target_page
    #             e = await self.make_stickers_embed()
    #             text = '''Oh! Here are the stickers you've collected so far! You can get them all sorts of ways—achievements, being nice, participating in events, and more.'''
    #             await self.send_or_edit_message(e, text, messageable)
    #     else:
    #         target_page = min(110, target_page)
    #         if target_page != self.page_no:
    #             self.page_no = target_page
    #             e = self.make_individual_sticker_embed(self.page_no - 100)
    #             text = '''You can also jump to or search for individual pages with `.yb 105` or `.yb Fang`!'''
    #             await self.send_or_edit_message(e, text, messageable)


    async def send_or_edit_message(self, embed, text, messageable):
        # sending for the first time
        if not self.wfr_message:
            self.wfr_message = await messageable.send(f'<@{self.member.id}> {text}', embed=embed)
            for reaction in [ICON_BOOK, ICON_STICKERS, ICON_BACK, ICON_FORWARD]:
                await self.wfr_message.add_reaction(reaction.strip('<>'))
            self.bot.wfr[self.member.id] = self
        else:
            await self.wfr_message.edit(content=f'<@{self.member.id}> {text}', embed=embed)

    async def show_stickers_old(self, messageable):

        self.page_no = 80
        # e, file, stickers = self.make_stickers_embed()
        e = await self.make_stickers_embed()
        text = '''Oh! Here are the stickers you've collected so far! You can get them all sorts of ways—achievements, being nice, participating in events, and more.'''

        # sending for the first time
        if not self.wfr_message:
            self.wfr_message = await messageable.send(f'<@{self.member.id}> {text}', embed=e)  # , file=file)
            for reaction in [ICON_STICKERS, ICON_BACK, ICON_FORWARD]:
                await self.wfr_message.add_reaction(reaction.strip('<>'))
            self.bot.wfr[self.member.id] = self
        else:
            await self.wfr_message.edit(content=text, embed=e)

        # update cache image regardless
        # self.yb.img_cache['stickers'][self.member.id][self.page_no] = (self.wfr_message.embeds[0].image.url, stickers)

    def make_toc_embed(self):
        if self.member.id not in self.yb.toc_cache:
            self.update_toc()

        toc = self.yb.toc_cache[self.member.id]
        section = None
        parts = []
        for index, page_data in enumerate(toc):
            if section is None or page_data[0] != section:
                section = page_data[0]
                if section == 'toc':
                    parts.append((index, 'TOC', ICON_BOOK))
                elif section == 'memories':
                    parts.append((index, 'Memories', ICON_STICKERS))
                elif section == 'stickers':
                    parts.append((index, 'Stickers', '<:FlamingGuitar:765958443558633502>'))

        lines = []
        for part in parts:
            index, name, emoji = part
            line = f'`{name: <22}{index+1}` {emoji}'
            lines.append(line)

        lines = '\n'.join(lines)
        description = f'''Table of Contents
{lines}'''

        e = discord.Embed(title=f'{self.member.name}\'s Yearbook', description=description)
        e.set_footer(text=f'{ICON_BOOK} Table of Contents • Page {self.page_no + 1}')
        e.set_image(url=IMG_YB_FRONT)
        return e

    async def make_stickers_embed(self):

        self.load_from_db()

        if self.sticker_row.stickers is None:
            stickers = []
        else:
            stickers = json.loads(self.sticker_row.stickers)
            stickers.sort()

        total_stickers = len(self.yb.stickers)
        total_sets = len(self.yb.sets)
        collected = len(stickers)
        completed = 0

        field_texts = []
        for set_no, set_contents in self.yb.sets.items():
            complete = all(no in stickers for no in set_contents)
            if complete:
                completed += 1

            emojis = []
            for no in set_contents:
                if no in stickers:
                    emojis.append(self.yb.stickers[no]['emoji'])
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

        e.set_footer(text=f'🖼️ Memories • Page {self.page_no + 1}')

        if self.member.id not in self.yb.img_cache['stickers']:
            self.yb.img_cache['stickers'][self.member.id] = {}

        if self.page_no in self.yb.img_cache['stickers'][self.member.id]:
            cache_img, cache_stickers = self.yb.img_cache['stickers'][self.member.id][self.page_no]

            if stickers == cache_stickers:
                e.set_image(url=cache_img)
                # print('found in cache, set image to ', cache_img)
                return e

        sticker_keys = [self.yb.stickers[sticker]['key'] for sticker in stickers]
        png = self.yb.render.render_stickers('memories_page', sticker_keys)
        file = discord.File(png, 'yb.png')
        cache_msg = await self.bot.get_channel(self.bot.config['interop_cn']).send(f'Cache for {str(self.member)}', file=file)
        self.yb.img_cache['stickers'][self.member.id][self.page_no] = (cache_msg.attachments[0].url, stickers)

        # print('set image to ', cache_msg.attachments[0].url)
        e.set_image(url=cache_msg.attachments[0].url)
        return e

        # e.set_image(url='attachment://yb.png')

        # # workaround upload
        # if file is not None:
        #     await self.bot.get_channel(self.bot.config['interop_cn']).send(f'Cache for {str(self.member)}', file=file)
        #     self.yb.img_cache['stickers'][self.member.id][self.page_no] = (
        #     self.wfr_message.attachments[0].url, stickers)

        # return e, discord.File(png, 'yb.png'), stickers

    def make_individual_sticker_embed(self, no):

        sticker = self.yb.stickers[no]
        set_name = ['Base Set', 'VVORMDRAMA Set'][sticker['set'] - 1]
        # {sticker['emoji']}
        description = f'''_{sticker['name']}_
[No. {no} / {set_name}]
'''

        e = discord.Embed(title=f'{self.member.name}\'s Yearbook', description=description)
        e.set_image(url=sticker['image'])
        e.set_footer(text=f'''🖼️ Series {sticker['series']} • Page {self.page_no + 1}''')

        return e

class Trade:
    def __init__(self, bot, member_a, member_b):
        self.bot = bot
        self.yb = bot.yearbook
        self.member_a = member_a
        self.member_b = member_b
        self.offer_a = []
        self.offer_b = []
        self.confirmed_a = False
        self.confirmed_b = False
        self.code = None
        self.wfr_message = None
        self.expires = time.time() + 15 * 60
        self.completed = False

    async def handle_reaction(self, reaction, user):

        if self.completed:
            self.clear_wfr()
            return

        emoji = str(reaction.emoji)
        if user.id not in [self.member_a.id, self.member_b.id]:
            return

        is_a = user.id == self.member_a.id
        if emoji == ICON_CONFIRM:
            if not self.offer_a or not self.offer_b:
                await self.wfr_message.channel.send(f'{ICON_CLOSE} <@{user.id}>, both users must be offering something before you can accept the trade.', delete_after=10)
                return

            if is_a:
                if not self.confirmed_a:
                    self.confirmed_a = True
                    await self.update_message(self.member_a, 'confirm')
            elif not self.confirmed_b:
                self.confirmed_b = True
                await self.update_message(self.member_b, 'confirm')

            if self.confirmed_a and self.confirmed_b:
                await self.execute_trade()

        elif emoji == ICON_REFRESH:
            if is_a:
                if self.offer_a:
                    self.offer_a = []
                    self.confirmed_a = self.confirmed_b = False
                    await self.update_message(self.member_a, 'remove')
            elif self.offer_b:
                self.offer_b = []
                self.confirmed_a = self.confirmed_b = False
                await self.update_message(self.member_b, 'remove')

        elif emoji == ICON_CLOSE:
            # todo add "with other user"
            self.clear_wfr()
            del self.yb.trades[self.member_a.id]
            del self.yb.trades[self.member_b.id]
            await self.wfr_message.channel.send(f'{ICON_CLOSE} <@{user.id}> has cancelled the trade.')
            await self.wfr_message.delete()

    async def execute_trade(self):
        self.clear_wfr()
        del self.yb.trades[self.member_a.id]
        del self.yb.trades[self.member_b.id]
        self.completed = True

        sticker_row_a, inv_a = load_stickers_for(self.member_a, False)
        if not all(sticker in inv_a for sticker in self.offer_a):
            await self.wfr_message.channel.send(f'{ICON_CLOSE} The trade could not be completed, <@{self.member_a.id}> no longer has some of the offered stickers.')
            return

        sticker_row_b, inv_b = load_stickers_for(self.member_b, False)
        if not all(sticker in inv_b for sticker in self.offer_b):
            await self.wfr_message.channel.send(f'{ICON_CLOSE} The trade could not be completed, <@{self.member_b.id}> no longer has some of the offered stickers.')
            return

        inv_a = sorted([no for no in inv_a if no not in self.offer_a] + self.offer_b)
        inv_b = sorted([no for no in inv_b if no not in self.offer_b] + self.offer_a)

        sticker_row_a.stickers = json.dumps(inv_a)
        sticker_row_b.stickers = json.dumps(inv_b)
        sticker_row_a.save()
        sticker_row_b.save()

        await self.wfr_message.channel.send(f'<@{self.member_a.id}> <@{self.member_b.id}> {ICON_CONFIRM} Trade completed successfully!')

    def stickers_as_text(self, stickers):
        if not stickers:
            return 'None'
        return', '.join([f"{self.yb.stickers[sticker]['emoji']} `{self.yb.stickers[sticker]['name']}`" for sticker in stickers])

    async def make_and_send(self, ctx, inv_a, inv_b):
        if self.wfr_message is not None:
            return

        color = random.choice(RAINBOW_PALETTE) #0xe2eeff
        e = discord.Embed(title=f'Trade Start!', color=color,
                          description=f'''<@{self.member_a.id}> has offered to trade with <@{self.member_b.id}>

Type and send the name of a sticker e.g. `Fang Horns` to offer it for trade. You can add up to 6 at a time.

{ICON_REFRESH}️ to remove all offered stickers
{ICON_CONFIRM}️ to confirm the trade (must be repeated whenever the trade changes)
{ICON_CLOSE}️ to cancel/reject the trade

🕑 _This trade will expire in 15 minutes._''')

        e.add_field(name=f'{self.member_a.display_name}\'s Offer', value=self.stickers_as_text(self.offer_a), inline=False)
        e.add_field(name=f'{self.member_b.display_name}\'s Offer', value=f'{self.stickers_as_text(self.offer_b)}{FIELD_BREAK}', inline=False)
        e.add_field(name=f'📦 {self.member_a.display_name}\'s Inventory', value=self.stickers_as_text(inv_a), inline=False)
        e.add_field(name=f'📦 {self.member_b.display_name}\'s Inventory', value=self.stickers_as_text(inv_b), inline=False)

        self.wfr_message = await ctx.send(f'<@{self.member_a.id}> <@{self.member_b.id}>', embed=e)

        for reaction in [ICON_REFRESH, ICON_CONFIRM, ICON_CLOSE]:
            await self.wfr_message.add_reaction(reaction.strip('<>'))

        self.bot.wfr[self.member_a.id] = self
        self.bot.wfr[self.member_b.id] = self

    async def attempt_to_add(self, member, sticker):
        if self.completed:
            return

        sticker_row, stickers = load_stickers_for(member, False)
        if sticker not in stickers:
            await self.wfr_message.channel.send(f"<@{member.id}>, you do not have a {self.yb.stickers[sticker]['emoji']} `{self.yb.stickers[sticker]['name']}` sticker to trade.", delete_after=15)
            return

        offer_pool = self.offer_a if member == self.member_a else self.offer_b
        if sticker in offer_pool:
            await self.wfr_message.channel.send(f"<@{member.id}>, you've already offered that sticker.", delete_after=15)
            return

        self.confirmed_a = self.confirmed_b = False
        offer_pool.append(sticker)
        offer_pool.sort()

        await self.update_message(member, 'add')

    async def update_message(self, updater, action='add'):

        # todo remove duplicate load
        sticker_row_a, inv_a = load_stickers_for(self.member_a, False)
        sticker_row_b, inv_b = load_stickers_for(self.member_b, False)

        other = self.member_a if updater == self.member_b else self.member_b

        action_text = {
            'add': 'added a sticker to trade with',
            'confirm': 'confirmed a trade with',
            'remove': 'cleared all stickers in their trade with'
        }[action]

        title = 'Trade Set!'
        if self.confirmed_a and self.confirmed_b:
            title = 'Trade Complete!'

        color = random.choice(RAINBOW_PALETTE)  # 0xe2eeff
        e = discord.Embed(title=title, color=color,
                          description=f'''<@{updater.id}> {action_text} <@{other.id}>.

**Status**
{self.member_a.display_name}: {f'{ICON_CONFIRM} _Accepted_' if self.confirmed_a else '_Waiting for confirmation_'}
{self.member_b.display_name}: {f'{ICON_CONFIRM} _Accepted_' if self.confirmed_b else '_Waiting for confirmation_'}

Type and send the name of a sticker e.g. `Fang Horns` to offer it for trade. You can add up to 6 at a time.

{ICON_REFRESH}️ to remove all offered stickers
{ICON_CONFIRM}️ to confirm the trade (must be repeated whenever the trade changes)
{ICON_CLOSE}️ to cancel/reject the trade''')

        e.add_field(name=f'{self.member_a.display_name}\'s Offer', value=self.stickers_as_text(self.offer_a), inline=False)
        e.add_field(name=f'{self.member_b.display_name}\'s Offer', value=f'{self.stickers_as_text(self.offer_b)}{FIELD_BREAK}', inline=False)
        e.add_field(name=f'📦 {self.member_a.display_name}\'s Inventory', value=self.stickers_as_text(list(set(inv_a) - set(self.offer_a))), inline=False)
        e.add_field(name=f'📦 {self.member_b.display_name}\'s Inventory', value=self.stickers_as_text(list(set(inv_b) - set(self.offer_b))), inline=False)

        if self.confirmed_a and self.confirmed_b:
            e.set_footer(text='This trade has ended.')

        await self.wfr_message.edit(embed=e)

    def clear_wfr(self):
        self.bot.clear_wait_fors(self.member_a.id)
        self.bot.clear_wait_fors(self.member_b.id)


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

class Render:
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
    create_tables()
    yearbook = Yearbook(bot)
    bot.add_cog(yearbook)
    bot.yearbook = yearbook
