
import discord
from discord.ext import commands
import checks
from common import DBL_BREAK, send_message, get_member_or_search


class Halloween(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.is_jacob()
    @commands.command()
    async def hw(self, ctx):
        print('run')
        await self.bot.get_channel(self.bot.config['interop_cn']).send(f'.give {ctx.author.id} naser {ctx.channel.id} An account of a Count\'s counting: helped the Count count.')

    @checks.is_jacob()
    @commands.command()
    async def parse(self, ctx, *, arg):
        try:
            query, pool_query, rest = arg.split(' ', 2)
            pool_query = pool_query.lower().strip()
        except ValueError:
            await send_message(ctx, 'f', error=True)
            return

        # find member
        success, result = await get_member_or_search(self.bot, ctx.guild, query, include_pings=False, members_only=True)
        if not success:
            await send_message(ctx, f'{result}{DBL_BREAK}f', error=True)
            return
        member = result

        reason = None
        channel = None
        print('rest', rest)
        try:
            cid, reason = rest.split(' ', 1)
            print('cid', cid)
            channel = self.bot.get_channel(int(cid))
        except (ValueError, TypeError) as e:
            pass

        print('channel', channel)

        if channel is None:
            reason = rest
            channel = ctx.channel

def setup(bot):
    hw = Halloween(bot)
    bot.add_cog(hw)
    bot.hw = hw
