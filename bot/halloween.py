
import discord
from discord.ext import commands
import checks
import time
import random
from common import DBL_BREAK, send_message, get_member_or_search

ingredients = {
    '🍄': 'a wild mushroom',
    '🐚': 'the shell of a sea snail',
    '🥀': 'the thorns of a dying rose',
    '🌷': 'a tulip bulb',
    '🧄': 'a garlic bulb',
    '✨': 'a sparkle of magic',
    '🔥': 'an enchanted flame'
}

class Halloween(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_encounters = {}
        self.messages_to_encounters = {}
        self.tt_claimed = []

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.reaction_action('add', payload)

    async def reaction_action(self, action, payload):
        if payload.message_id not in self.messages_to_encounters:
            return

        if payload.user_id == self.bot.user.id:
            return

        encounter = self.messages_to_encounters[payload.message_id]

        user = self.bot.get_user(payload.user_id)
        if not user:
            return

        emoji = str(payload.emoji)
        if encounter['name'] == 'rosa':
            if emoji not in encounter['needed']:
                del self.active_encounters[payload.channel_id]
                del self.messages_to_encounters[payload.message_id]
                await encounter['msg'].channel.send(f'''Oh no! <@{user.id}> added a {emoji} to the potion <:GVHrosasob:721410319469117520> I'm afraid this one's ruined...''')
                return

            if emoji not in encounter['added_by']:
                encounter['added_by'][emoji] = user.id
                if len(encounter['added_by']) == len(encounter['needed']):
                    del self.active_encounters[payload.channel_id]
                    del self.messages_to_encounters[payload.message_id]

                    helpers = {}
                    for emoji, uid in encounter['added_by'].items():
                        if uid not in helpers:
                            helpers[uid] = [emoji]
                        else:
                            helpers[uid].append(emoji)

                    parts = []
                    # todo make into english "and" etc
                    for uid, emojis in helpers.items():
                        if len(emojis) > 1:
                            text = ' '.join(emojis)
                            parts.append(f'<@{uid}> added  {text}')
                        else:
                            parts.append(f'<@{uid}> added a  {emojis[0]}')

                    text = f'Wonderful work! It\'s ready! <:GVHrosahappy:721410319427043448>{DBL_BREAK}' + '\n'.join(parts)
                    await encounter['msg'].channel.send(text)

                    for uid in helpers:
                        await self.bot.get_channel(self.bot.config['interop_cn']).send(f".give {uid} hw_rosa {encounter['msg'].channel.id} Potion mastery! Helped Rosa the Good Witch work her magic.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.channel is None:
            return

        if message.channel.id == 771481451337744384:
            text = message.content.lower()

            if 'trick' in text or 'treat' in text:
                if message.author.id in self.tt_claimed:
                    await message.channel.send(f"<@{message.author.id}> you've already claimed your treat! Come back in a little while to get another.")
                    return

                self.tt_claimed.append(message.author.id)
                await self.bot.get_channel(self.bot.config['interop_cn']).send(f".give {message.author.id} hw_items {message.channel.id} Trick-or-treat!")
                await message.channel.send(f"Happy Halloween from KO_OP, <@{message.author.id}>!")
                return


        if message.channel.id not in self.active_encounters:
            return

        encounter = self.active_encounters[message.channel.id]
        if encounter['name'] == 'naser':
            try:
                n = int(message.content)
            except ValueError:
                return

            if n < 1:
                return

            if n != encounter['current']:
                await message.channel.send(f'''{n}? <:GVHrosasob:721410319469117520> No! That\'s not right! Start over from **{encounter['min']}** and count to **{encounter['max']}**, taking turns with others.''')
                encounter['current'] = encounter['min']
                encounter['counters'] = []
                return

            if encounter['counters'] and encounter['counters'][-1] == message.author:
                await message.channel.send(
                    f'''<@{message.author.id}>, you have to take turns counting with _others_. <:GVHrosasob:721410319469117520> Start over from **{encounter['min']}** and count to **{encounter['max']}**!''')
                encounter['current'] = encounter['min']
                encounter['counters'] = []
                return

            encounter['counters'].append(message.author)
            if n == encounter['max']:
                del self.active_encounters[message.channel.id]
                del self.messages_to_encounters[encounter['msg'].id]

                uniques = []
                for member in encounter['counters']:
                    if member.id not in uniques:
                        uniques.append(member.id)

                text = f'Extremely good counting! <:GVHrosahappy:721410319427043448>{DBL_BREAK}'
                await encounter['msg'].channel.send(text)

                for uid in uniques:
                    await self.bot.get_channel(self.bot.config['interop_cn']).send(f".give {uid} hw_naser {encounter['msg'].channel.id} An encounter's account: helped the Count count. ")
                return

            encounter['current'] += 1
            return

    @checks.is_mod()
    @commands.command()
    async def reset_tt(self, ctx):
        self.tt_claimed = []
        await ctx.send('reset')

    @checks.is_mod()
    @commands.command()
    async def tc(self, ctx):
        await self.start_naser_encounter(ctx.channel)

    @checks.is_mod()
    @commands.command()
    async def hw(self, ctx, channel: discord.TextChannel, *, arg):
        if arg == 'naser':
            await self.start_naser_encounter(channel)
            await ctx.message.add_reaction('✅')
            return

        if arg == 'rosa':
            await self.start_rosa_encounter(channel)
            await ctx.message.add_reaction('✅')
            return

    '''
    naser
    '''
    async def start_naser_encounter(self, channel):
        if channel.id in self.active_encounters:
            if time.time() > self.active_encounters[channel.id]['expires']:
                encounter = self.active_encounters[channel.id]
                del self.active_encounters[channel.id]
                del self.messages_to_encounters[encounter['msg'].id]
            else:
                return

        encounter = self.active_encounters[channel.id] = {
            'name': 'naser',
            'min': 1,
            'max': random.randint(4, 10),
            'current': None,
            'cn': channel.id,
            'expires': time.time() + 5 * 60,
            'msg': None,
            'counters': []
        }

        if random.random() < 0.4:
            encounter['min'] = random.randint(1, 10000)
            encounter['max'] = encounter['min'] + random.randint(4, 10)

        encounter['current'] = encounter['min']

        description = f'''The Count Naser has emerged from a foggy vista, *gasp* !! You almost swoon at the sight of his fearsome elegance! But worry not, for he is not craving blood tonight, no… tonight he craves the simple joy of a good count! Count Naser is counting on you and your closest companions to count from **{encounter['min']}** to **{encounter['max']}**. Child's play, I hear you say?{DBL_BREAK}⚠️ _Instructions: You all must **take turns** counting from **{encounter['min']}** to **{encounter['max']}** without repeating a number, as fast as you can! You have 5 minutes! Blah! (That's a vampire sound, right?)_'''

        e = discord.Embed(title=f'Count Naser', description=description)
        e.set_footer(text=f'🎃 Happy Halloween from KO_OP!')
        e.set_image(url='https://i.imgur.com/szg7YJJ.png')

        msg = await channel.send(embed=e)
        self.active_encounters[channel.id]['msg'] = msg
        self.messages_to_encounters[msg.id] = self.active_encounters[channel.id]

    '''
    rosa
    '''
    async def start_rosa_encounter(self, channel):
        if channel.id in self.active_encounters:
            if time.time() > self.active_encounters[channel.id]['expires']:
                encounter = self.active_encounters[channel.id]
                del self.active_encounters[channel.id]
                del self.messages_to_encounters[encounter['msg'].id]
            else:
                return

        needed = random.sample(ingredients.keys(), random.randint(3, 5))
        needed_text = ''
        for i, emoji in enumerate(needed):
            if i < len(needed) - 1:
                needed_text += f'**{ingredients[emoji]}**, '
            else:
                needed_text += f'and **{ingredients[emoji]}**'

        self.active_encounters[channel.id] = {
            'name': 'rosa',
            'needed': needed,
            'added_by': {},
            'cn': channel.id,
            'expires': time.time() + 5 * 60,
            'msg': None,
        }

        description = f'''As you are watering your section of the community garden, you see the unmistakable point of a witch's hat in the pumpkin patch! "Halloo there!" you yell, your heart pounding. One never knows what to expect from a witch raiding one's garden this time of year, after all!{DBL_BREAK}"Oh! Oh my god hi, I'm sorry, everything in your garden just looked so luscious… I'm looking for some ingredients to help me craft a confidence potion for the big Chemistry exam tomorrow! I'll need {needed_text}!"{DBL_BREAK}⚠️ _Instructions: Innovate with Rosa the Good Witch on a spell to help her get a little confidence for her Chemistry test! Find her the right potion ingredients and let Rosa work her magic on the spell! Anyone can pitch in to help, but do it quickly! You have 5 minutes._"'''

        e = discord.Embed(title=f'Rosa the Good Witch', description=description)
        e.set_footer(text=f'🎃 Happy Halloween from KO_OP!')
        e.set_image(url='https://i.imgur.com/nGNODAu.png')

        msg = await channel.send(embed=e)
        self.active_encounters[channel.id]['msg'] = msg
        self.messages_to_encounters[msg.id] = self.active_encounters[channel.id]

        reactions = list(ingredients.keys())
        random.shuffle(reactions)
        for reaction in reactions:
            await msg.add_reaction(reaction.strip('<>'))




def setup(bot):
    hw = Halloween(bot)
    bot.add_cog(hw)
    bot.hw = hw
