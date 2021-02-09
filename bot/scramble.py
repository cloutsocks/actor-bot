
import discord
from discord.ext import commands
import checks
import time
import random
from common import DBL_BREAK, send_message, get_member_or_search

sentences = [
    "Don't you like our old songs?",
    "Woah did you do something new with your hair?",
    "I bet Reed knows about wacky time signatures",
    "How many times do bands usually audition before they finally get a gig",
    "Who needs advanced Trig anyway",
    "I haven't seen you in forever",
    "I cannot wait to be done with all this school stuff",
    "We have to get some practice sessions in this week!",
    "If you want, I can explain the assignment to you",
    "I can't believe Mrs. Robers put me on the spot like that"
]

buttons = [
    '🇦',
    '🇧',
    '🇨',
    '🇩',
    '🇪',
    '🇫',
    '🇬',
    '🇭',
    '🇮',
    '🇯',
    '🇰',
    '🇱',
    '🇲',
    '🇳',
    '🇴',
    '🇵',
    '🇶',
    '🇷',
    '🇸',
    '🇹',
    '🇺',
    '🇻',
    '🇼',
    '🇽',
    '🇾',
    '🇿',
]

class Scramble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current = random.randint(0, len(sentences) - 1)
        self.active_msg = None

        self.sentence = None
        self.words = None
        self.used = []

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.reaction_action('add', payload)

    async def reaction_action(self, action, payload):
        if self.active_msg is None or payload.message_id != self.active_msg.id:
            return

        if payload.user_id == self.bot.user.id:
            return

        user = self.bot.get_user(payload.user_id)
        if not user:
            return

        emoji = str(payload.emoji)

        # remove it always
        await self.active_msg.remove_reaction(payload.emoji, user)

        try:
            index = buttons.index(emoji)
        except ValueError:
            return

        if index not in self.used:
            # add word
            self.used.append(index)
            await self.active_msg.edit(embed=self.make_embed())
            await self.active_msg.remove_reaction(payload.emoji, self.bot.user)

    @commands.command(aliases=['lore'])
    async def scramble(self, ctx, *, arg=''):
        # if self.active_msg:
        #     # todo already going
        #     return

        self.sentence = sentences[self.current]
        self.words = self.sentence.split(' ')
        random.shuffle(self.words)
        self.used = []

        e = self.make_embed()

        self.active_msg = await ctx.send(embed=e)

        for reaction in buttons[:len(self.words)]:
            await self.active_msg.add_reaction(reaction.strip('<>'))

    def make_embed(self):

        pool = '\n'.join([f'''{buttons[i]} `{self.words[i]}`''' for i in range(len(self.words))])

        # pool = ''
        # for i, word in enumerate(self.words):
        #     pool += buttons[i] + word + '\n'


        description = f'''(todo: introductory text)'''

        e = discord.Embed(title=f'Scramble Title', description=description)
        e.add_field(name='Word Pool', value=pool, inline=False)
        e.add_field(name='Current Sentence', value='--' + ' '.join([self.words[i] for i in self.used]), inline=False)
        return e


def setup(bot):
    scramble = Scramble(bot)
    bot.add_cog(scramble)
    bot.scramble = scramble
