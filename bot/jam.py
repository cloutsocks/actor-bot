import asyncio
import copy
import math

import discord
from discord.ext import commands

import checks, re

from synthplayer.sample import Sample

from PIL import Image, ImageDraw, ImageFont, ImageColor

import os
import subprocess


__ = '    \u200b'
ARROW = '<:arrow:745744683040243782>'

REST_NOTE = '-'
C3 = '+'
scale = 'cdefgabCDEFGAB' + C3

KICK = 'k'
SNARE = 's'
CLAP = 'x'

non_melody = re.compile(fr'[^a-g\s{{}}\[\](){C3}{REST_NOTE}]', re.IGNORECASE)
non_drums = re.compile(fr'[^\s{{}}\[\](){KICK}{SNARE}{CLAP}{REST_NOTE}]', re.IGNORECASE)
# non_kick = re.compile(fr'[^{KICK}\s]', re.IGNORECASE)
# non_snare = re.compile(fr'[^{SNARE}\s]', re.IGNORECASE)
# non_clap = re.compile(fr'[^{CLAP}\s]', re.IGNORECASE)

def parse_melody(text):
    if re.search(non_melody, text):
        return False

    melody = []
    current_chord = None

    for c in text:
        if c in '[{(':
            if current_chord is not None:
                return False
            current_chord = ''

        elif c in ']})':
            if not current_chord:
                return False

            melody.append(current_chord[:5])
            current_chord = None

        elif c == REST_NOTE:
            melody.append(REST_NOTE)

        elif c in scale:
            if current_chord is not None and c not in current_chord:
                current_chord += c
            else:
                melody.append(c)

    return melody[:16]

def parse_drums(text):
    if re.search(non_drums, text):
        return False

    drums = []
    current_chord = None

    for c in text:
        if c in '[{(':
            if current_chord is not None:
                return False
            current_chord = ''

        elif c in ']})':
            if not current_chord:
                return False

            drums.append(current_chord[:5])
            current_chord = None

        elif c == REST_NOTE:
            drums.append(REST_NOTE)

        elif c in [KICK, SNARE, CLAP]:
            if current_chord is not None and c not in current_chord:
                current_chord += c
            else:
                drums.append(c)

    return drums[:16]

# def parse_drums(text, char):
#     drums = []
#     for c in text:
#         if c == REST_NOTE:
#             drums.append(REST_NOTE)
#         elif c == char:
#             drums.append(char)
#
#     return drums[:16]


def make_vid(song, uid, play, render):
    render.render(song, uid=uid)
    play.record_to_file(song, uid=uid)

    # subprocess.check_output(['git', 'log', '--quiet', '-n', str(n), '--pretty=format:%H|%at|%an|%s']).decode(
    #     'UTF-8').split('\n')

    # subprocess.call(f'ffmpeg -y -i jam/tmp/song_{uid}.wav -loop 1 -i jam/tmp/render_{uid}.png -c:v libx264 -tune stillimage -pix_fmt yuv420p -shortest jam/tmp/rendered_song_{uid}.mp4',
    #                 shell=True,
    #                 stdout=subprocess.DEVNULL,
    #                 stderr=subprocess.DEVNULL)

    subprocess.call(['ffmpeg', '-y', '-i', f'jam/tmp/song_{uid}.wav', '-loop', '1',
                     '-i', f'jam/tmp/render_{uid}.png', '-c:v', 'libx264',
                     '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-shortest',
                     f'jam/tmp/rendered_song_{uid}.mp4'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)

    # input_still = ffmpeg.input("render.png", stream_loop=1)
    # input_audio = ffmpeg.input("song.wav")
    #
    # # (
    # #     ffmpeg
    # #         # .concat(input_still, input_audio, v=1, a=1)
    # #         .output(input_still, input_audio, 'output.mp4', vcodec='libx264', pix_fmt='yuv420p', tune='stillimage', shortest=None)
    # #         .run(overwrite_output=True)
    # # )
    #
    # (
    #     ffmpeg
    #         .concat(input_still, input_audio, v=1, a=1)
    #         .output('output.mp4', vcodec='libx264', pix_fmt='yuv420p', tune='stillimage', shortest=None)
    #         .run(overwrite_output=True)
    # )

class Jam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessions = {}
        self.render = Render()
        self.play = Play()
        self.play.load_samples()

    @commands.command()
    async def play(self, ctx, *, arg=''):

        melody = parse_melody(arg)
        if not melody:
            await ctx.send('not a melody')
            return False

        song = Song()
        song.melody = melody
        await ctx.trigger_typing()

        make_vid(song, ctx.author.id, self.play, self.render)
        await ctx.send(file=discord.File(f'jam/tmp/rendered_song_{ctx.author.id}.mp4'))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.author.id not in self.sessions:
            return

        session = self.sessions[message.author.id]
        if message.channel != session.channel:
            return

        # parse
        lines = message.content.split('\n')
        updates = []
        new_song = copy.copy(session.song)

        for line in lines:
            try:
                n = int(line)
                if 1 <= n <= 8:
                    updates.append('🎼')
                    new_song.ticks = n
                    continue

                if 60 <= n <= 1000: #140:
                    updates.append('🕓')
                    new_song.bpm = n
                    continue

            except ValueError:
                pass

            if not re.search(non_melody, line):
                melody = parse_melody(line)
                if melody:
                    updates.append('🎸')
                    new_song.melody = melody
                    continue

            if not re.search(non_drums, line):
                drums = parse_drums(line)
                if drums:
                    updates.append('🥁')
                    new_song.drums = drums
                    continue

                return

            # if we get here, it's invalid
            return

        if not updates:
            return

        for reaction in updates:
            await message.add_reaction(reaction)

        session.song = new_song
        await session.try_to_update()


        # for char in [KICK, SNARE, CLAP]:
        #     if not re.search(fr'[^\s{char}{REST_NOTE}]', text, flags=re.IGNORECASE):
        #         drums = parse_drums(text, char)
        #         if drums:
        #             await message.add_reaction('🥁')
        #             session.song.drums[char] = drums
        #             # await message.channel.send(f'update drums to: {drums}')
        #             await session.try_to_update()
        #             return

    @commands.command()
    async def jam(self, ctx):
        session = JamSession(self.bot, ctx.author, ctx.channel)
        self.sessions[ctx.author.id] = session
        await session.send_initial()

    @commands.command(aliases=['how2jam'])
    async def howtojam(self, ctx):
        await self.send_help(ctx)

    async def send_help(self, channel):
        e = discord.Embed(title="how 2 jam", color=0x57AADE)
        e.description = help_text
        e.set_image(url='https://i.imgur.com/hNPNcdW.png')
        await channel.send(embed=e)

def melody_as_text(melody, ticks):
    if not melody:
        return 'None'

    chunks = []
    for i in range(0, len(melody), ticks):
        chunk = ''
        for j in range(i, min(len(melody), i+ticks)):
            if len(melody[j]) == 1:
                chunk += melody[j]
            else:
                chunk += f"[{melody[j]}]"

        chunks.append(f'`{chunk}`')

    # chunks = [f'`{melody[i:i + ticks]}`' for i in range(0, len(melody), ticks)]
    return ' '.join(chunks)

LABELS = {
    KICK: 'Kick',
    SNARE: 'Snare',
    CLAP: 'Clap',
}

def drums_as_text(drums, ticks):
    if not drums:
        return 'None'

    chunks = []
    for i in range(0, len(drums), ticks):
        chunk = ''
        for j in range(i, min(len(drums), i+ticks)):
            if len(drums[j]) == 1:
                chunk += drums[j]
            else:
                chunk += f"[{drums[j]}]"

        chunks.append(f'`{chunk}`')

    # chunks = [f'`{melody[i:i + ticks]}`' for i in range(0, len(melody), ticks)]
    return ' '.join(chunks)

# def drums_as_text(drums, ticks):
#     lines = []
#     for char in [KICK, SNARE, CLAP]:
#         pattern = drums[char]
#         if not pattern:
#             continue
#         chunks = [f'`{"".join(pattern[i:i + ticks])}`' for i in range(0, len(pattern), ticks)]
#         lines.append(f"{' '.join(chunks)} {LABELS[char]}")
#
#     if not lines:
#         return 'None'
#
#     return '\n'.join(lines)

class JamSession:
    def __init__(self, bot, member, channel):
        self.bot = bot
        self.member = member
        self.channel = channel
        self.song = Song()
        self.last_recorded = None
        self.last_jump = None

    async def send_initial(self):

        e = self.make_song_embed(with_fields=False)
        e.description = '''we're gonna make a song right here, right now! just start typing a melody like:
`aabgccc` `aaabgc`

or go crazy with chords and high-notes:
`[cG][aE][d+][cG][aE][d+]`

you can even add drums, rests and change the speed too! cool, right?
        
click ❓ or type `.howtojam` if this is your first time!

type `.jam` again to start over or ❌ to quit (or just wait awhile and it'll take care of itself)

bonus points if u can recreate constellations'''

        e.set_image(url='https://cdn.discordapp.com/attachments/781287336909733919/781601183483035668/strumming.gif')

        sent = await self.channel.send(embed=e)


#         sent = await self.channel.send('''we're gonna make a song right here, right now. cool, right?
#
# click ❓ or type `.howtojam` if this is your first time!''')
        reactions = ['❓', '❌'] #'🌈'

        for reaction in reactions:
            await sent.add_reaction(reaction.strip('<>'))

        def check(reaction, user):
            return reaction.message.id == sent.id and str(reaction.emoji) in reactions and user.id == self.member.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=180, check=check)
        except asyncio.TimeoutError:
            return

        if str(reaction.emoji) == '❓':
            await self.bot.jam.send_help(self.channel)
            return

        if str(reaction.emoji) == '❌':
            self.bot.jam.sessions.pop(self.member.id, None)
            await self.channel.send('hope u had fun jamming!')
            return

    async def try_to_update(self):
        if self.song == self.last_recorded:
            await self.channel.send(f"ur song didn't change, so u can play the old one here: {self.last_jump}")
            return

        if not self.song.is_playable():
            await self.channel.send(f"cool! but ull need to add some instruments to play this song.")
            return

        self.last_recorded = copy.copy(self.song)

        await self.channel.trigger_typing()
        make_vid(self.song, self.member.id, self.bot.jam.play, self.bot.jam.render)
        sent = await self.channel.send(embed=self.make_song_embed(), file=discord.File(f'jam/tmp/rendered_song_{self.member.id}.mp4'))

        self.last_jump = sent.jump_url

        reactions = ['❓', '❌']  # '🌈'

        for reaction in reactions:
            await sent.add_reaction(reaction.strip('<>'))

        # cleanup
        # paths = [
        #     f'jam/tmp/rendered_song_{self.member.id}.mp4',
        #     f'jam/tmp/song_{self.member.id}.wav',
        #     f'jam/tmp/render_{self.member.id}.png'
        # ]
        #
        # for file in paths:
        #     if os.path.isfile(file):
        #         os.remove(file)

        def check(reaction, user):
            return reaction.message.id == sent.id and str(reaction.emoji) in reactions and user.id == self.member.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=180, check=check)
        except asyncio.TimeoutError:
            return

        if str(reaction.emoji) == '❓':
            await self.bot.jam.send_help(self.channel)
            return

        if str(reaction.emoji) == '❌':
            self.bot.jam.sessions.pop(self.member.id, None)
            await self.channel.send('hope u had fun jamming!')
            return



#     async def send_initial_prompt(self, ctx):
#         e = self.make_embed()
#         self.wfr_message = await ctx.send(embed=e)
#         # reactions = ['❓', '🎸', '🥁', '⏯', '❌']
#         reactions = ['❓', '❌']
#
#         for reaction in reactions:
#             await self.wfr_message.add_reaction(reaction.strip('<>'))
#             self.bot.wfr[self.member.id] = self
#
    def make_song_embed(self, with_fields=True):
#         desc = '''we're gonna make a song right here, right now. cool, right?
#
# click ❌ or ❓ if you need some help!'''

        e = discord.Embed(title=f'{self.member.name}\'s song', color=0x57AADE)
        # e.description = desc

        if with_fields:

            e.add_field(name=f'🕗 BPM', value=f'{self.song.bpm}', inline=True)
            e.add_field(name=f'🎼 Ticks', value=f'{self.song.ticks} per bar', inline=True)
            e.add_field(name=f'🎸 Lead', value=melody_as_text(self.song.melody, 4), inline=False)
            e.add_field(name=f'🥁 Drums', value=drums_as_text(self.song.drums, 4), inline=False)

        return e


class Song:
    def __init__(self):
        self.bpm = 100
        self.ticks = 2
        self.melody = None
        self.drums = None
        # self.drums = {
        #     KICK: None,
        #     SNARE: None,
        #     CLAP: None,
        # }

    def is_playable(self):
        return self.melody or self.drums

    def __eq__(self, other):
        if isinstance(other, Song):
            return self.bpm == other.bpm and \
                   self.ticks == other.ticks and \
                   self.melody == other.melody and \
                   self.drums == other.drums
                   # self.drums[KICK] == other.drums[KICK] and \
                   # self.drums[SNARE] == other.drums[SNARE] and \
                   # self.drums[CLAP] == other.drums[CLAP]

    def __ne__(self, other):
        return not self.__eq__(other)


class Play:
    def __init__(self):
        self.samples = {}

    def load_samples(self):

        self.samples[KICK] = Sample(wave_file='jam/samples/kick.wav').normalize().make_32bit(scale_amplitude=True).lock()
        self.samples[SNARE] = Sample(wave_file='jam/samples/snare.wav').normalize().make_32bit(scale_amplitude=True).lock()
        self.samples[CLAP] = Sample(wave_file='jam/samples/clap.wav').normalize().make_32bit(scale_amplitude=True).lock()

        for note in scale:
            if note == C3:
                path = f'jam/samples/Lead C3.wav'
            elif note.islower():
                path = f'jam/samples/Lead {note.upper()}1.wav'
            else:
                path = f'jam/samples/Lead {note}2.wav'

            # print(path)
            self.samples[f'lead_{note}'] = Sample(wave_file=path).normalize().make_32bit(scale_amplitude=True).lock()

    def record_to_file(self, song, uid):

        mixed = self.mix(song)
        mixed.make_16bit()
        mixed.amplify(0.5)

        fn = f'jam/tmp/song_{uid}.wav'
        mixed.write_wav(fn)

    def mix(self, song):

        # kick = ('x-x-' * 4)[:len(melody)]
        # snare = ('-x-x' * 4)[:len(melody)]

        # total_seconds = len(melody) * 60.0 / self.bpm / self.ticks
        mixed = Sample().make_32bit()
        time_per_index = 60.0 / song.bpm / song.ticks

        # todo allow drums to go past melody

        for i, chord in enumerate(song.melody):
            timestamp = time_per_index * i

            if chord != REST_NOTE:
                for note in chord[:5]:
                    sample = self.samples[f'lead_{note}']
                    if len(chord) > 1: # 2
                        # volume = 1/(len(chord))
                        # volume = (1 / len(chord)) * 1.75
                        # volume = 1 - math.log10(len(chord) - 1)
                        # if len(chord) == 2:
                        #     volume = 0.7
                        # volume = 0.5
                        # print('notes/volume', len(chord), volume)

                        volume = [1, 0.9, 0.65, 0.6, 0.5][len(chord)-1]

                        mixed.mix_at(timestamp, sample.at_volume(volume))

                        # .mix_at(timestamp, sample.at_volume(1/len(chord)-1))
                    # elif len(chord) == 2:
                    #     mixed.mix_at(timestamp, sample.at_volume(0.75))
                    else:
                        mixed.mix_at(timestamp, sample)

            try:
                beat = song.drums[i]
            except (IndexError, TypeError) as e:
                continue

            if beat != REST_NOTE:
                for instrument in beat[:5]:
                    mixed.mix_at(timestamp, self.samples[instrument])

            # for instrument, pattern in song.drums.items():
            #     try:
            #         char = pattern[i]
            #     except (IndexError, TypeError) as e:
            #         continue
            #
            #     if char == instrument:
            #         mixed.mix_at(timestamp, self.samples[instrument])


        # chop/extend to get to the precise total duration (in case of silence in the last bars etc)
        # missing = total_seconds - mixed.duration
        # print('missing', missing)
        # if missing > 0:
        #     mixed.add_silence(missing)
        # elif missing < 0:
        #     mixed.clip(0, total_seconds)

        return mixed


class Render:
    def __init__(self):
        self.canvas = Image.open('jam/bass.png').convert('RGBA')
        self.font = ImageFont.truetype('jam/Mark-Black.ttf', 77) #100 #75

    def render(self, song, uid=1):

        melody = song.melody

        if len(melody) == 16:
            ox = 30
            oy = 270
            spacing = 49

        elif len(melody) > 8:
            ox = 40
            oy = 270
            spacing = 52
        else:
            ox = 80
            oy = 270
            spacing = 80

        canvas = self.canvas.copy()

        draw = ImageDraw.Draw(canvas)

        for i, chord in enumerate(melody):
            if chord == REST_NOTE:
                continue

            # oy = oy if i < 8 else oy2
            oy = oy
            # x = ox + (i % 8) * spacing
            x = ox + i * spacing

            # for note in reversed(chord) if len(chord) > 1 else chord:
            if len(chord) > 1:
                chord = sorted(chord, key=lambda note: scale.index(note))

            for note in chord:
                n = scale.index(note)
                # y = oy - n * 8 #6 #(18 if len(chord) > 1 else 6)
                # y = oy - n * (12 if len(chord) > 1 else 8)
                y = oy - n * 8

                hue = 800/len(scale) * (n % 7)
                color = ImageColor.getrgb(f'hsb({hue}, 81%, 99%)')

                # if note.islower():
                #     color = ImageColor.getrgb(f'#D7FA2D')
                # elif note == '!':
                #     color = ImageColor.getrgb(f'#F73F84')
                # else:
                #     color = ImageColor.getrgb(f'#F743D6')

                # D7FA2D
                # F743D6
                # F73F84

                shown_as = note
                if note == C3:
                    shown_as = 'C'

                draw.text((x, y), shown_as, font=self.font, fill=color, anchor='mm')

        canvas.save(f'jam/tmp/render_{uid}.png')

        # png = io.BytesIO()
        # draw.save(png, format='PNG', optimize=False)
        # png.seek(0)
        # return png



def setup(bot):
    jam = Jam(bot)
    bot.add_cog(jam)
    bot.jam = jam

help_text = f'''a song might look like this:

_Final Fantasy Prelude_
Melody: `CDEG` `+GED` `abCE` `AECb` 2 ticks per bar

_Doom Theme_
Melody: `eeE-eD-eC-ea-eab` 130 bpm, 4 ticks per bar
Drums: `kks-` `k-s-` `kks-` `k-s-`

so to make _Doom_ you type `eeE-eD-eC-ea-eab` to set the melody 🎸, `kks-` `k-s-` `kks-` `k-s-` to set the drums 🥁, `130` to set the bpm 🕗, `4` to double the ticks 🎼!

you can set them separately or type it all in one go as long as it's on **different lines** (shift+enter):
```kks- k-s- kks- k-s-
eeE-eD-eC-ea-eab
130
4```
but what does all that mean??

**melody**: the melody is the sequence of notes in your song! you can type up to two octaves
so that's `cdefgba` for the lower octave, `CDEFGBGA` for the higher one, and `+` for the high c (for you sopranos out there)

**rests**: a rest is ~simply~ the absence of sound. :shushing_face: __type `-` to add rests to your song.__ for example, if you want two rests after your low c note, you can type `c--`. just a heads up, this works for your melody _and_ your drums!

**chords**: a chord is a combination of notes that play simultaneously. any note that you type within `[ ]` or `( )` will play at the same time in your song! `ac[fA]` plays a, then c, then `f` & `a` together!

**drums**: work similar to your melody! you have a **k**ick drum, **s**nare drum, and clap (which uses `x` since `c` is taken)
you can type `ksksksks` to alternate kick and snare, or `k[sx]-k[sx]` to play a snare and clap together, just like a chord!
you'll wanna type these separately from your melody

**bpm**: this is how fast you're playing! __type any number between 60 and 140 to change the BPM__

**ticks**: this is just a music-ey-lingo way to track the timing of the notes (in what's called a bar). all you need to know is more ticks means MORE DRUMS :fire: (and faster shredding!). __type any number between 1 and 8 to change how many ticks are in a bar__, doubling from 2 to 4 lets us go wild!

got all that? if not, maybe a friend here can help!

...otherwise just start typing and jamming!'''

# help_text = f'''ok! so while we're jamming,
#
# {ARROW} type any number between 60 and 140 to change the **bpm** - how fast we're playing!
#
# {ARROW} type any number between 1 and 8 to change how many **ticks** are in a bar. doubling from 2 to 4 lets us go wild with drums. more ticks = more drums!
#
# ⏯ click this to record and play back your tune!
#
# got it? if not, maybe a friend here can help!
# '''