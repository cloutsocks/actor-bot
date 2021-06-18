
import discord
import gspread

from discord.ext import commands

from common import apply_emoji

arrow = '<:arrow:727614211932291183>'
welcome_text = f'''Oh! A new student! Welcome to KO_OP, a place to chat about _Goodbye Volcano High_ and hang out with friends. I'll give you a quick tour:

{arrow} <#372482304867827714>
Read the rules before posting

{arrow} <#720741732698030090>
Customize your Student ID with roles

{arrow} <#487721645738426371>
Keep up with announcements

{arrow} <#720742318331658261>
Find out about _Goodbye Volcano High_

{arrow} <#489895795705905178>
Chat with other students

Wishlist *Goodbye Volcano High* here!
https://store.steampowered.com/app/1310330/Goodbye_Volcano_High/

Be sure to invite your friends!
http://discord.gg/ko-op

<https://goodbyevolcanohigh.com/>'''

class Naomi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.approve_text = None
        self.member_role = None

        if self.bot.is_ready():
            self.bot.loop.create_task(self.on_load())

    @commands.Cog.listener()
    async def on_ready(self):
        await self.on_load()

    async def on_load(self):
        self.member_role = self.bot.guild.get_role(self.bot.config['member_role_id'])
        gc = gspread.service_account(filename='../config/service_account.json')
        spreadsheet = gc.open_by_key(self.bot.config['sheets']['data'])
        sheet = spreadsheet.worksheet('approve_message')
        lines = sheet.col_values(1)

        self.approve_text = []
        msg = ''

        for line in lines:
            line = apply_emoji(self.bot, line[:1990])
            if len(msg) + len(line) > 1990:
                self.approve_text.append(msg)
                msg = ''
            else:
                msg += line + '\n'

        if msg:
            self.approve_text.append(msg)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.guild == self.bot.guild:
            if self.member_role in after.roles and self.member_role not in before.roles:
                if not self.approve_text:
                    await self.bot.mod_cn.send(f'❌ **Could not load the approval message, so none was sent to recently approved member!**')
                    return

                for text in self.approve_text:
                    await after.send(text)

    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     if member.guild == self.bot.guild:
    #         await member.send(approve_text)


def setup(bot):
    naomi = Naomi(bot)
    bot.add_cog(naomi)
    bot.naomi = naomi
