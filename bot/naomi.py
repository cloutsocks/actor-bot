
import discord
from discord.ext import commands

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

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild == self.bot.guild:
            await member.send(welcome_text)


def setup(bot):
    naomi = Naomi(bot)
    bot.add_cog(naomi)
    bot.naomi = naomi
