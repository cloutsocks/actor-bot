
import re
import sys
import traceback

import discord

from datetime import datetime, timedelta

id_pattern = re.compile(r'<@!?(\d+?)>')
cn_id_pattern = re.compile(r'<#([0-9]+)>')

emojiPattern = u'(?:[\U00002600-\U000027BF])|(?:[\U0001f300-\U0001f64F])|(?:[\U0001f680-\U0001f6FF])'
customEmojiPattern = r'<.?:(?:.+?):(?:\d+?)>'

ERROR_RED = 0xD32F2F
INFO_BLUE = 0x3579f0

DBL_BREAK = '\n \n'
FIELD_BREAK = '\n\u200b'

TYPE_COLORS = (
    0xFFFFFF,
    0xE88158,
    0x57AADE,
    0x7FBF78,
    0x9C6E5A,
    0xF2CB6F,
    0x9DD1F2,
    0xAD70D5,
    0xF0A1C1,
    0x222222,
    0x646EAB
)

RAINBOW_PALETTE = (
    # 🍂 Autumn
    0xffb88c,

    # 🍎 Red Apple
    0xff9999,

    # 🍒 Cherries
    0xff6063,

    # 🍓 Strawberry
    0xfcbad3,

    # 🌸 Cherry Blossom
    0xf0cafc,

    # 🌷 Lilac
    0xa991e8,

    # 🌠 Midnight
    0x6772e5,

    # ⛅ Blue Skies
    0x99ccff,

    # 🌿 Bluegrass
    0x38b2a5,

    # 🌱 Baby Mint
    0x99ffdc,

    # 🌲 Evergreen
    0x62d2a2,

    # 🍃 Spearmint
    0x82ffb0,

    # 🍌 Banana
    0xffe676,

    # 🐝 Bumblebee
    0xffdd99,

    # 🌻 Sunflower
    0xffbb42,

    # 🍊 Tangerine
    0xff9e42,

    # ☕ Espresso
    0x9c6343,

    # 🍫 Pain au Chocolat
    0x8d6262,

    # 🌙 Night
    0x000000
)

ICON_ATTACK = '⚔'
ICON_CLOSE = '❌'
BLUE_HEART = '💙'
GREEN_HEART = '💚'
YELLOW_HEART = '💛'
SPY_EMOJI = '🕵️'



def strip_extra(s):
    return re.sub('[^\sA-Za-z]+', '', s)


def normalize(s):
    return s.lower().strip().replace(' ', '')

def pluralize(word, val):
    return word if val == 1 else f'{word}s'

def simplify_timedelta(d):
    if d.days > 0:
        return f'''{int(d.days)} **{pluralize('day', d.days)}**'''
    if d.seconds > 3600:
        hours = d.seconds // 3600
        return f'''{int(hours)} **{pluralize('hour', hours)}**'''
    if d.seconds > 60:
        mins = d.seconds / 60
        return f'''{int(mins)} **{pluralize('min', mins)}**'''

    return f'''{int(d.seconds)} **{pluralize('second', d.seconds)}**'''


class MemberNotFound(Exception):
    pass


def resolve_member(server, member_id):
    member = server.get_member(member_id)
    if member is None:
        raise MemberNotFound()
        # if server.chunked:
        #     raise MemberNotFound()
        # try:
        #     member = await server.fetch_member(member_id)
        # except discord.NotFound:
        #     raise MemberNotFound() from None
    return member


async def find_members(bot, server, query, get_ids=False, use_hackban=False, members_only=False):
    if not query:
        return None

    uid = None
    match = re.search(r'\b\d+?\b', query)
    if match:
        uid = int(match.group(0))

    match = id_pattern.search(query)
    if match:
        uid = int(match.group(1))

    if uid is not None:
        if get_ids:
            return [uid]
        try:
            member = resolve_member(server, uid)
            return [member]
        except MemberNotFound:
            if members_only:
                return None
            # hackban case
            if use_hackban:
                return [discord.Object(id=uid)]
            try:
                return [await bot.fetch_user(uid)]
            except (discord.NotFound, discord.HTTPException) as e:
                return None

    found = {}
    query = normalize(query)
    for m in server.members:
        if query == str(m.id) or normalize(str(m)).startswith(query) or query in normalize(m.name) or (m.nick and query in normalize(m.nick)):
            found[m.id] = m

    return list(found.keys()) if get_ids else list(found.values())


async def get_member_or_search(bot, server, query, include_pings=True, use_hackban=False, members_only=False):
    found = await find_members(bot, server, query, use_hackban=use_hackban, members_only=members_only)
    if found and len(found) == 1:
        return True, found[0]

    return False, whois_text(bot, found, include_pings=include_pings, show_extra=False)


def whois_text(bot, found, include_pings=True, show_extra=True, try_embed=False):
    if not found:
        return 'No matching users found.'

    make_embed = try_embed and len(found) == 1

    now = datetime.utcnow()
    out = []

    for m in found:
        is_staff = m.id in bot.config['admin_ids']
        name = f'{m} <:kooper:489893009228300303> [KO_OP]' if is_staff else str(m)
        if not make_embed and include_pings and not is_staff:
            parts = [f'<@{m.id}>', name]
        else:
            parts = [name]

        try:
            if m.nick:
                parts.append(f'Nickname: {m.nick}')
        except AttributeError:
            pass
        parts.append(str(m.id))

        if show_extra:
            if hasattr(m, 'created_at') and m.created_at:
                created_at = m.created_at
            else:
                created_at = discord.utils.snowflake_time(m.id)

            created_ago = now - created_at
            parts.append(f'Created: {simplify_timedelta(created_ago)} ago')

            if hasattr(m, 'joined_at') and m.joined_at:
                joined_ago = now - m.joined_at
                parts.append(f'Joined: {simplify_timedelta(joined_ago)} ago')

                if m.joined_at - created_at < timedelta(minutes=15):
                    parts.append('⚠ **Joined within 15 minutes of making an account.**')

        if isinstance(m, discord.User):
            parts.append('Joined: _Not found on this server._')

        out.append('\n'.join(parts))

    out = DBL_BREAK.join(out)
    if(len(found) > 1):
        out = f'_Multiple members found:_{DBL_BREAK}{out}'

    if len(out) > 1997:
        out = out[:1997] + '...'

    if make_embed:
        m, = found
        return f'<@{m.id}>', discord.Embed(description=out).set_thumbnail(url=m.avatar_url)

    return out


async def send_message(ctx, text, message=None, ping=True, error=False, color=None, image_url=None, expires=None):

    message = message or ctx.message

    # if(error):
    #     text = f"ERROR: {text}"

    e = discord.Embed(description=text)
    if color or error:
        e.color = color if color else ERROR_RED
    if expires is None and error:
        expires = 10
    if image_url is not None:
        e.set_image(url=image_url)

    header = '<@{}>'.format(message.author.id) if ping else ''
    sent = await message.channel.send(header, embed=e, delete_after=expires)
    return sent


async def send_user_not_found(ctx, arg):
    await send_message(ctx, f'''Couldn't find a trainer in this server by that name!''', error=True)


def enquote(text):
    return f'“{text}”'


def ordinal(num, bold=False):
    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')
    return f'**{num}**{suffix}' if bold else str(num) + suffix


def clamp(n, lo, hi):
    return max(min(n, hi), lo)


def print_error(ctx, error):
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

emoji_markup = re.compile(r'{(\w+?)}')

def apply_emoji(bot, text):
    for match in re.finditer(emoji_markup, text):
        try:
            emoji = bot.config['emoji'][match.group(1)]
        except KeyError:
            continue

        text = text.replace(match.group(0), emoji)

    return text

def setup(bot):
    pass




