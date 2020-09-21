
import discord
import checks
import random

import time
import pytz

from discord.ext import commands
from common import RAINBOW_PALETTE, FIELD_BREAK

from peewee import *
from datetime import datetime

# from tarot.cards import cards
# from tarot.readings import readings

cards = [

    [0, 'The Fool', 'U', ['Innocence', 'New Beginnings', 'Spontaneity'],

'''Kind of like that feeling you get the morning of the first day of school, there's nothing like the sense that you're about to embark on a new adventure. You're feeling that right now: the vast possibilities of the roads you haven't taken yet, just on the horizon. Go into it with an open mind and an open heart (cheesy, but so is taking a leap!).

Could there be bumps in the road you haven't planned for? Mmmmm maybe most definitely. But hey, don't worry about that now! Ignorance is bliss!''',
     'https://i.imgur.com/Vgaw5Hf.png', 0xF26663],


    [0, 'The Fool', 'R', ['Recklessness', 'Risk Taking ', 'Foolhardiness'],
'''You know when you have this idea, and you know it's _awesome_, and you know it's gonna change the world, or at the very least your world, but something is stopping you from putting it on the page? You're pumping the brakes before you've even gotten started, but why? Take a step back from the expectations and let yourself reflect on what's stoppin' ya from moving forward.

Alternatively, the reversed Fool can be telling you that you're driving TOO FAST. Don't book a show before you've even finished the lyrics of your songs. Don't count your Triceratops eggs before they've hatched. In other words: don't let your eagerness make you turn your back on the potential consequences of your actions. ''',
     'https://i.imgur.com/2AkkZn3.png', 0xF26663],


    [1, 'The Magician', 'U', ['Creation', 'Manifestation', 'Inspired Action'],
'''This is a powerful card, friend! You've planted the seeds of an idea, and with that comes the knowledge that you have the tools to make it possible. But it's up to you to make sure that you're following this particular path for the right reasons: is it important to you in your heart, in your soul? Or do you just want to get famous, become a rock and roll legend and never have to go to school again or something?

Concentrate on whatever this seed is, whether it's a friendship or a creative endeavor, and really commit to understanding what you want it to grow into in the future.''',
     'https://i.imgur.com/vexHsrB.png', 0xFFC42C],


    [1, 'The Magician', 'R', ['Illusion', 'Manipulation', 'Untapped Talents'],
'''It's not that you're not making progress on your goals, it's just that maybe you're still uncertain on how to get there. You're flapping your wings a bit, or you're treading water. Maybe you've lost sight of the deeper meaning behind something that was once really compelling to you, or you're finding that you're focusing too much on how to do something, instead of why you're doing it. You have so much to give to the world, but you have to believe in yourself first.

Alternatively, this card holds an understanding that there may be—however unintentional—some underlying malice to something in your actions. You may be using your authority or knowledge for self-gain at the expense of others. Keep an eye on your priorities and make sure you're acting with generosity and kindness towards those around you!''',
     'https://i.imgur.com/4vutxrh.png', 0xFFC42C],


    [2, 'The High Priestess', 'U', ['Sacred Energy', 'Subconscious Mind', 'Intuition'],
'''Look, I know this stuff can get a bit hippie-dippy but stick with me: the High Priestess is here to tell you that right now is a good time to tap into your inner emotional gunk.

Clear off the cobwebs of your intuition and try trusting it! You could start journaling, or meditation, or sitting with your thoughts on top of a hill while staring into the middle distance. Your subconscious is trying to pass you a note in the middle of class: will you take a minute to read it? You might learn something about yourself.''',
     'https://i.imgur.com/4EXJk7w.png', 0x5B3271],


    [2, 'The High Priestess', 'R', ['Secrets', 'Disconnection from the Self', 'Repressed Feelings'],
'''If the upright High Priestess is about submerging yourself in the subconscious, its reversed position is letting you know that you might be struggling with trusting your ability to flap your tail in those waters. Something is holding you back...  maybe you're keeping something from yourself, or maybe you're afraid of what you might find when you stop rejecting your intuition. Believe in your ability to look within yourself for answers. They're often there.''',
     'https://i.imgur.com/XGj8Q77.png', 0x5B3271],


    [3, 'The Empress', 'U', ['Nature', 'Abundance', 'Feminine Energy'],
'''Alright so the ole' Tarot set is getting a bit binary here with the Empress and the Emperor, but let's try to look at it as a connection to certain types of energies instead.

The Empress is a card of riches, whatever that may mean to you. It's a buffet of gratitude, a bite of self-expression, a nom of creative discovery. If this has made you hungry, go enjoy a gratuitous meal and really bask in it: that type of abundance is what the Empress is all about!

Things you have been dreaming of are coming into fruition. Enjoy them with your loved ones, or reflect on what you're thankful for on your own in the woods or at the beach. ''',
     'https://i.imgur.com/g14c88k.png', 0x679FB0],


    [3, 'The Empress', 'R', ['Dependence', 'Creative Block', 'Emptiness'],
'''Maybe you've been inside too long, or maybe you're just in a rut, but the reversed Empress is letting you know, you could use a little more focus on yourself.

This might be a time to do something just for you: write a song you don't need to show anyone, go for a walk, do 25 raptor-jacks out in the park just for the kick of it. You might just jostle out a few ideas, or shift out of the creative block you've been feeling. ''',
     'https://i.imgur.com/AS2nVP6.png', 0x679FB0],


    [4, 'The Emperor', 'U', ['Authority', 'Structure', 'Masculine Energy'],
'''Like we said with the Empress, the Tarot gets a bit binary here with the Empress and the Emperor, but I know you contain multitudes so don't even worry about it.

The Emperor deals with a feeling of stability and structure. It may be letting you know that you're feeling good about a leadership role, or that you feel particularly equipped to deal with conflict. Like a good student body president or a particularly adept cafeteria worker, you are ruling with wisdom and organization.

Use this organization to break down complex issues into bite-sized nuggets, and once you've learned how to do it, pass that info along to someone else!''',
     'https://i.imgur.com/7cqfnJG.png', 0x79C3FF],


    [4, 'The Emperor', 'R', ['Domination', 'Lack of Discipline', 'Aloofness'],
'''Someone in another universe once said that with great power comes great responsibility. Don't ask me what universe, it came to me in a dream!

What's important here is looking at your own relationship to power—whether you're not exerting it enough and feeling your tail get trod on or you're exerting it too much and roaring in people's faces, you owe it to yourself and those around you to think about how you wield authority. Is someone or something making you feel like you can't speak up?

Are you having trouble giving up control or delegating? Power is a, well, powerful thing. It must be distributed fairly and carefully.''',
     'https://i.imgur.com/gPdo4fH.png', 0x79C3FF],


    [5, 'The Hierophant', 'U', ['Conformity', 'Tradition', 'Morality and Ethics'],
'''Even though the Hierophant has its origins in religion and spiritual beliefs, in an interpersonal, day-to-day sort of way, it's more about engrained knowledge and a tried and true system that's been working for you. It's about acquiring wisdom from someone or something you trust and believe in.

And if you are spiritually leaning... hi, hello, welcome to my home: the Hierophant is also asking you to honor that spirituality and any rituals that may come with it. ''',
     'https://i.imgur.com/kyzosXi.png', 0xFF6763],


    [5, 'The Hierophant', 'R', ['Freedom', 'Challenging Institutions', 'New Approaches'],
'''So the upright Hierophant is about institutions that you trust and feel held by and the wisdom that comes with learning from someone. WELL FLIP THE TABLE 'cause when the Hierophant is reversed it's about being your _own_ teacher, headbutting convention, and going your own way.

When your teachers don't believe you or your parents keep trying to control you or your boss is making you feel like you're bad at your job, you have to say, "I'm going to grab life by the horns and break outta this joint!" This joint being societal norms. ;)''',
     'https://i.imgur.com/m8dd17Z.png', 0xFF6763],


    [6, 'The Lovers', 'U', ['Partnerships', 'Harmony', 'Duality'],
'''Ooooh, you are out here vibing with someone!!! (Please dish on who it is, I won't gossip.) I for one hope you are getting to engage in a little... anky-panky. You're an ankylosaurus, right? Don't throw your shoe at me!

Look, the Lovers don't have to be romantic in nature. You could be on the same wavelength with a bandmate, or a coworker, or a best friend. At the end of the day, it's about a connection forged in trust and love. Someone you can tell everything to, even your most vulnerable truths.

You can also be forging a deeper connection to yourself, and looking at the dualities within you that create a more cohesive whole. Deep, I know.''',
     'https://i.imgur.com/GaPUWGD.png', 0xFCC5BE],


    [6, 'The Lovers', 'R', ['Disharmony', 'Imbalance', 'One-Sidedness'],
'''Maybe you're out of sync with the people around you, maybe you're having trouble communicating, or maybe you're in a relationship that's feeling kind of one-sided... regardless, something feels off. So what's a lovelorn dino to do in such a situation? I recommend taking a look under your headplate and seeing if you can find the source of the imbalance. If the conflict is interpersonal, maybe there is room for mutual growth. If the conflict is with yourself, this may be a time to reflect on how you can find balance with the many facets that make you you!''',
     'https://i.imgur.com/WyRDsts.png', 0xFCC5BE],


    [7, 'The Chariot', 'U', ['Action', 'Determination', 'Willpower'],
'''Grab that tyrannosaurus by the reins and take charge!! The Chariot signifies that you have found order and understanding on a subject in your life and are now ready for action. The energy here is all about keeping you on focus, keeping you bold, and reminding you to have faith in yourself. Now is a time of determination!!

Alternatively, this card may signify actual travel, and if that's the case, I call shotgun.''',
     'https://i.imgur.com/ZLGrzhb.png', 0xCE913E],


    [7, 'The Chariot', 'R', ['Lack of Direction', 'Opposition', 'Intensity'],
'''Hold your horns there, friend. You gotta check the map for directions before you get on the highway. The reversed Chariot is telling you that you may not have as firm of a grasp on the direction a project is heading in than you thought and that ya might want to take a second look. That might be too hard to do right now, but that's normal! Bumps in the road are a part of life.

Maybe you're having trouble seeing a path ahead because you have two separate ideas pulling you in different directions. You gotta get those wheels facing in the same direction or you won't go anywhere. The extended metaphor is rolling away from me, somebody stop it!!!''',
     'https://i.imgur.com/raVub03.png', 0xCE913E],


    [8, 'Strength', 'U', ['Inner Strength', 'Persuasion', 'Compassion'],
'''Inner strength is so hot! There's nothing like when you meet someone and you can tell their emotional core is rooted—they're not gonna blow away in a storm. Too metaphorical? The Strength card is about that knowledge that you are capable or determined, and calm in that determination.

Your power is not aggressive, but persuasive, you are alluring right now and effortlessly in control. You don't need to grab a sabretooth by the fangs, because it's already eating out of your hand.''',
     'https://i.imgur.com/eyRsYWy.png', 0x8ABA7F],


    [8, 'Strength', 'R', ['Self Doubt', 'Low Energy', 'Insecurity'],
'''When we doubt ourselves, it can make us lose balance. It's disorienting and exhausting to lose touch with what we most love about ourselves, and it can affect our self-esteem. Try to touch base with all the times you totally crushed it. You already know you rule—a moment in time where you're not sure about it will pass.

Try to be kind to yourself; just because you didn't get an A on your English assignment doesn't mean you're a failure. Lay your weary self to rest for a bit! You deserve it.''',
     'https://i.imgur.com/PQWkorp.png', 0x8ABA7F],


    [9, 'The Hermit', 'U', ['Introspection', 'Inner Guidance', 'Being Alone'],
'''Think druid in a game of L&L: off in nature, communing with the griffinflies, wearing your cloak, and listening to the sounds of a distant waterfall. You're on your own, but certainly not in a bad way. You're simply vibing with yourself and ruminating on your place in the universe.

You're getting to know yourself better on your own terms, not those set by society (individualism, capitalism, greed, all that bad stuff!) and it's giving you the guidance you deserve. Be your own pathfinder.''',
     'https://i.imgur.com/2Yh8GQJ.png', 0x889EED],


    [9, 'The Hermit', 'R', ['Isolation', 'Withdrawal', 'Lost Your Way'],
'''Your phone and your laptop are bleep blooping with notifications, the TV's on, and for some reason the radio's blasting from the other room. It's enough to give even the most hardcore multitasker a headache! You're juggling more tasks than an Arthropleura has legs! All of this is sending you mixed signals, and you're unable to focus on what's important to you.

Try to pluck off a few of your tasks for right now and focus on yourself and what's most important to you. You can get back to the rest later.

Alternatively, you may be feeling intentionally left out of things, or feeling alone. If that's the case, maybe pick up the phone and call a loved one you haven't been in touch with in a while. It'll probably do you both some good!''',
     'https://i.imgur.com/uesqWjJ.png', 0x889EED],


    [10, 'Wheel of Fortune', 'U', ['Cycles', 'Destiny', 'Turning Point'],
'''Ever since that like, ancient dinosaur or whoever invented the wheel, we have understood that what goes around comes around. And that whatever's down will come up again!

The Wheel of Fortune tells you to keep sight of those natural cycles, and the changes they bring. If you're on a roll (heh...) right now, then appreciate that feeling as something that may not last forever. If you're stuck in the mud, just know you won't be there forever.

This card is about going with the flow, and letting the universe guide you as much as possible. 😎 This may be a big turning point for you.''',
     'https://i.imgur.com/8SbA3rW.png', 0x3CBBFD],


    [10, 'Wheel of Fortune', 'R', ['Bad Luck', 'Clinging to Control', 'Resistance to Change'],
'''You can't stop a rolling wheel! Well, actually I guess you can but it's not a good idea. You ever tried to grab someone's bike while they were ridin' by you? Ya. Not good.

You can't stop the change that's already on its way, and you'll only hurt yourself by trying. Alternatively, the reversed Wheel of Fortune shows bad luck that is out of your control and may be making you feel like you have nowhere to turn. But you could try to summon up a timeline of what got you here, and see how you can learn from past experiences.

Maybe in identifying the patterns, you can make... A NEW WHEEL. A NEW FORTUNE. The power is in your hands.''',
     'https://i.imgur.com/LlPeq6z.png', 0x3CBBFD],


    [11, 'Justice', 'U', ['Clarity', 'Truth', 'Cause and Effect'],
'''You reap what you sow! Currently, I'm reaping some greens for my friend (she's a sauropod) from the conifers I planted. They're so pretty all bundled up in a little care package, I love it!! Omg sorry got carried away with garden talk...

The Justice card tells you that a verdict is on its way. You're thinking of your past actions and wondering what the karmic retribution will be. Have you been sour to the people around you and are now feeling isolated?

Maybe you've been kind to everyone as much as possible, even when it's been hard, and you're feeling the rewards that being fair and generous with people can bring.''',
     'https://i.imgur.com/ljZZqkd.png', 0x782222],


    [11, 'Justice', 'R', ['Lack of Accountability', 'Dishonesty', 'Unfairness'],
'''You may have done something wrong, but for whatever reason, you can't own it. Your ego is making it so hard to take accountability. Maybe you don't even recognize that you've hurt someone, because you've been spinning your narrative out in your mind so much you fully believe it!

Try acknowledging any and all internalized prejudices you may be holding, and really be honest with yourself about how your actions may be affecting others.

Alternatively, you may be going through a period in your life where you're being excessively hard on yourself, to the point where you've lost sight of objectivity. Either way, there is a sense of one-sidedness here, in one direction or another, and you need to find some harmony in your perspective on it.''',
     'https://i.imgur.com/qbkt3vs.png', 0x782222],


    [12, 'The Hanged Man', 'U', ['Letting Go', 'Surrender', 'New Perspectives'],
'''My best friend Sage always says, \"If you're having trouble figuring something out, try a handstand!\" It's about like, getting a new perspective?

The Hanged Man always looks so freaky! But it's actually just about taking a breather on your journey. When you take a break sometimes new ideas flow through you, where there wasn't time or room for them to exist before. Don't push yourself when the world is asking you to pause, or you could risk giving yourself a real headache later down the road.

Surrender to rest instead, and let the blood rush to your head with new ideas instead.''',
     'https://i.imgur.com/JqmRJVh.png', 0xFFC5AE],


    [12, 'The Hanged Man', 'R', ['Indecision', 'Fear of Sacrifice', 'Delays'],
'''You're not letting yourself take a break, but why? Don't you know that when you stop charging recklessly towards your goal, things can put themselves in focus more easily? Don't let life blur by you thoughtlessly when your body and mind are begging for a break.

The reversed Hanged Man (so wait, would that just be like... a Standing Man?) can mean you did pause, or you did sacrifice something to a greater goal, and it didn't feel like it went anywhere. Try to forgive and forget, so you can more easily continue on your journey.''',
     'https://i.imgur.com/wWuzdrb.png', 0xFFC5AE],


    [13, 'Death', 'U', ['Endings', 'Metamorphosis ', 'Transition'],
'''Everyone always looks at me like they just saw a ghost when I draw this card.

There's nothing to fear, though! Ultimately all the Death card is trying to say is that change is coming. Ya, maybe that means closing a door, but maybe that door needs to close! We can't stay in high school forever, or stay the same dinos: we have to evolve. Something good is on the other side.

And maybe that comes with some mourning, but as a wise philosopher once said, "Every new beginning comes from some other beginning's end." Mmm maybe that's from a song. Please don't sue me.''',
     'https://i.imgur.com/ookiYB6.png', 0x2E303C],


    [13, 'Death', 'R', ['Stagnation', 'Resistance', 'Fear of Change'],
'''Let go or be dragged, that's what I always say! The reversed Death card is revealing to you that there's something from your past you're having trouble releasing. Maybe someone hurt you and that pain still lives inside you. Maybe you hurt someone and it's closing you off to the possibility of forgiveness. But holding on to stale food is only gonna stink up your emotional fridge!

You don't want to become a fossil of your old self. Ungrip those talons, babes, surrender to the future, and fly!''',
     'https://i.imgur.com/JCzEpGj.png', 0x2E303C],


    [14, 'Temperance', 'U', ['Balance', 'Moderation', 'Patience'],
'''You're smooth, you're zen, you're water dripping slowly in an Arganodus fish pond. It feels like even with a million things going on around you, you're able to remain calm and balanced.

Maybe your friends are asking for your advice on a dispute because you're so objective and patient. You know nothing comes from rushing things, or trying to force someone to hatch who's not ready yet.

You can hold on to many ideas at once right now, and blend them into something totally new. Like a divine smoothie.''',
     'https://i.imgur.com/AoFK5Qa.png', 0xFFA664],


    [14, 'Temperance', 'R', ['Imbalance', 'Re-alignment', 'Extremes'],
'''You're shaking your soul's bones back into the right position. It may be a bit uncomfortable, but it's needed!

Maybe you've been bingeing anime for 3 days straight or maybe you've been spending too much time with dinos who deplete you of your energy. Whatever's been weighing you down, it's time to rid yourself of it. If you ignore the warning signs that something is off for too long, you'll risk feeling stuck, or your soul's misaligned bones will start to fossilize... you don't want a fossilized soul!!''',
     'https://i.imgur.com/dbSVG0N.png', 0xFFA664],


    [15, 'The Devil', 'U', ['Excess', 'Shadow Self', 'Playfulness'],
'''Oh sweetie, you are going through it, aren't you! This card is revealing that the darker forces in your life are coming to the forefront and dominating you like lava covering the terrain of your soul. 💔

With toxic patterns and habits influencing your behavior, you may find yourself rehashing the same fights with a loved one, unable to stop yourself from making that little jab, or rolling your eyes, because you've gotten so used to your defenses that not having them up makes you feel like you're walking around without scales... just a raw nerve!

An alternate interpretation of this card is that the time has come for you to have a little fun! If you're normally risk-averse, you could try playing with (safely) trying something new and unlike you. You may enjoy it!''',
     'https://i.imgur.com/Qdmdioa.png', 0xF5483C],


    [15, 'The Devil', 'R', ['Release', 'Detachment', 'Exploring Dark Thoughts'],
'''You're looking to plant a garden that you can truly tend to, where everything that you sow can live in harmony together. But before you can do that, you have to weed out the ferns to make space for what you really want to plant. Does my garden analogy make sense? Hee hee!!

What I'm saying is there's some major emotional exploration that has to happen before you can get to where you're going. Some of that exploration may be of some pretty dark thoughts or fears: you may not realize you've been clipping your wings until you look back at them! ''',
     'https://i.imgur.com/xBUj4Ch.png', 0xF5483C],


    [16, 'The Tower', 'U', ['Upheaval', 'Chaos', 'Revelation'],
'''It feels like the universe has or is about to throw you a real curve ball... the Tower is the tarot equivalent of trying to do the "rip the tablecloth off without disturbing the cutlery" trick and having the whole table fall down on you. Something is breaking down, and it's something you thought was stable.

This sense of disintegration is good though (stick with me), because it may reveal some bogus assumptions you'd been making. You were flying too close to the sun, and while you may have experienced a setback, the Tower also represents epiphanies and new ways of thinking.''',
     'https://i.imgur.com/MWL7wSH.png', 0xBE4D40],


    [16, 'The Tower', 'R', ['Personal Transformation', 'Fear of Change', 'Crisis Averted'],
'''So where the upright Tower is very much about an unexpected occurrence, often outside your control, the reversed Tower shows you on the precipice of a personal evolution—if you can allow it into your life.

You could be questioning a large part of your identity, or how you see others, or what you want for your future. I'm sure it's stomachache-inducing to think so much about that type of revelation, but it's an important step in your growth. There's no point in resisting it... oh ya, that's another meaning of this card by the way: a resistance to change, especially when you have a feeling it may be negative.

Better to go headfirst into the challenge with your eyes open than get caught unawares by it!''',
     'https://i.imgur.com/QC3V7j6.png', 0xBE4D40],


    [17, 'The Star', 'U', ['Hope', 'Purpose', 'Renewal'],
'''Hoooo! You've been through the lava and you're still keeping cool. The Star, coming as the follow-up to the Tower, is about rest and renewal. It's about the understanding that even though you've had setbacks, you're still on your way up. You've lost a battle but you haven't lost sight of your dreams.

Maybe you totally bombed on a college application essay, but there's another school you just know will want you. Or maybe you're just removing the protective plates that aren't serving you anymore in service of a more "you-ey" you. Hehe... "you-ey"''',
     'https://i.imgur.com/bGoYhkG.png', 0x504567],


    [17, 'The Star', 'R', ['Discouragement', 'Insecurity', 'Disconnection'],
'''You may have recently faced a major setback (remember, the Star card follows the Tower, which is all about setbacks with a capital S).

You can't seem to take it all in: it doesn't feel fair. It may feel like the end of the world, or like you have nothing left to give. Try to have faith. Maybe it is the end of the world, but if it is, don't you owe it to yourself to take care of yourself and the ones you love? Try to engage with the things that make you feel present in whatever is most important to you. All is not lost!''',
     'https://i.imgur.com/9axSDgi.png', 0x504567],


    [18, 'The Moon', 'U', ['Illusion', 'Intution', 'Anxiety'],
'''A lot of us can put on a brave face in front of others, but when we're alone in our room and the lights are off, all we're left with are our anxieties and worries.

Those fears could be about the past, something stupid we said or how we laughed in that weird way in homeroom. Or it could be a worry for the uncertainty of the future... But being in the dark isn't something you should fear!

Harness that solitude and use it for introspection! The night air in Caldera Bay is as re-invigorating as anything I've ever felt; go for a walk and see if it gives you a fresh, crisp insight on your issues. And let the night guide you into fruitful dreams that may shed light on your subconscious. 😴 Just don't lose your way!''',
     'https://i.imgur.com/huaAuy4.png', 0x232C82],


    [18, 'The Moon', 'R', ['Repressed Emotion', 'Fear', 'Confusion'],
'''When the Moon card is reversed, it means you've been in your head for so long, you don't know which way is up—you may be in denial about something, or convinced that something is going on based on nothing but your gut.  But while you're all like, "La la la la la I'm not listening to you, reality," you may be missing out on what's really important.

It's not that you need to stop listening to your subconsious, it just means your subconscious could use a bit of a leash to the real world.''',
     'https://i.imgur.com/I6h1NEv.png', 0x232C82],


    [19, 'The Sun', 'U', ['Positivity', 'Vitality', 'Joy'],
'''The sun is shining, you're relaxing, the birds are chirping, and it feels like everything's comin' up.... YOU!

The sun is a sign that your inner warmth and happiness is taking center stage, and that joyous vibe is infectious! You're shootin' rays of positivity out of your headplate! Maybe you just gave up smoking and you're full of a renewed sense of energy, or maybe you just learned a new skill and are bursting at the scales to show it off. Alternatively, you could be going through a hard time, and the Sun card is here to give you a pep talk, that the sun is rising for you soon. Just hold on!''',
     'https://i.imgur.com/AKWzQhy.png', 0xFFED79],


    [19, 'The Sun', 'R', ['Negativity', 'Inner Child', 'Sadness'],
'''Sigh.... you know when you plan a beach trip and then the day of it's suddenly like, totally rainy and cloudy and you just wanna stomp your feet and chomp someone's head off?

The reversed Sun card is the rain on your parade, the C you got in Math class, the mites on your favorite plant's leaves! Any of those things are enough to discourage someone, and it's normal to feel disappointed or pessimistic.

But you know what all those things are? Temporary setbacks! You'll find your way through the fog soon enough, sweetie!''',
     'https://i.imgur.com/umq2bAD.png', 0xFFED79],


    [20, 'Judgement', 'U', ['Inner Calling', 'Reflection', 'Rebirth'],
'''Ahh, you may be getting close to a milestone in a personal journey. You've put together a bunch of disparate notes into a beautiful song, gathered the ingredients together for a delicious meal.

You're finding yourself in a period of acceptance and understanding. You can see your mistakes and your triumphs in the distance behind you, and you're taking this time to share that love and peace with your loved ones. What do we owe each other at the end of a journey? What do we need from each other to keep soaring even higher?''',
     'https://i.imgur.com/jCHOcBF.png', 0xC2ECD8],


    [20, 'Judgement', 'R', ['Inner Critic', 'Self-doubt', 'Avoidance'],
'''You're seeing a lot of disparate puzzle pieces, but unfortunately the puzzle is of a blue sky, so it's a bit hard to put together. No matter! You know what you're doing, and I believe in you! But first you have to actually look at your journey so far, and what you still have to do.

You can't forgive yourself for past mistakes if you don't take accountability for them. You can't achieve your goals if you're constantly doubting yourself. Easier said than done, I know, but looking at your life and your choices—really digging in the mud of it—is the only way to come to a place of peace.''',
     'https://i.imgur.com/z7bb72A.png', 0xC2ECD8],


    [21, 'The World', 'U', ['Accomplishment', 'Travel', 'Fulfillment'],
'''You are at the top of the volcano! You are a mighty beast! You are at the end of a montage of a lot of hard work and close-ups of you looking cute and determined, and now everyone around you is clapping and throwing their hats in the air! You feel a sense of completion and extreme purpose!!

Ok, maybe it doesn't feel as momentous as all that, but it's like, definitely the end of an era. Whether it's graduation, a creative accomplishment, or a relationship breakthrough, you are achieving something long envisioned.

If you're not quite at this point of accomplishment, this card is letting you know that now is the time to get your microraptors in a row and reflect on what has brought you to where you are. Maybe that's just the push you need to bring yourself full circle.''',
     'https://i.imgur.com/e2MxWpc.png', 0x3CC5FF],


    [21, 'The World', 'R', ['Delays', 'Incomplete Goals', 'Unfulfillment'],
'''Sometimes we crave closure on a situation, but we're not taking all the steps we could be to get there. We may be waiting on someone else to do the work we know is ours to do, or feeling like our goal is too large or nebulous to see an end to.

This card is letting us know that we may need to do some personal work—whether it's through writing down your feelings or talking to someone—to sharpen our understanding of where we want to be. When the World card is reversed, it can mean that you're at the end of a marathon of sorts, but for whatever reason, you can't get your claws over the finish line. But think of what's on the other side!! Gatorade! High fives! Celebration! So don't stop now, friend, keep going!''',
     'https://i.imgur.com/t3FQeaO.png', 0x3CC5FF],
]

daily_reading = {
    'title': 'Daily Reading',
    'emoji': '<:stella:749318176508215367>',
    'text': 'Draw your daily card!',
    'unrevealed': 'https://i.imgur.com/nQqpDXC.png',
    'cards': [
        {
            'title': 'Draw ',
            'emoji': '<:tarot:748903972928094360>',
            'text': '''Contemplate the day ahead of you, or reflect on the day in the motion. What are your challenges? What are your highlights?''',
        }
    ]
}

readings = {


    'yes_no': {
        'title': 'Yes or No',
        'emoji': '<:naserconfused:720394002595315763>',
        'text': '''Single card reading''',
        'unrevealed': 'https://i.imgur.com/nQqpDXC.png',
        'cards': [
            {
                'title': 'Single Card',
                'emoji': '<:tarot:748903972928094360>',
                'text': '''Put all your focus on the question you're asking: what are the broad strokes surrounding this situation? What influences are at work here?''',
            }
        ]
    },

    'past_present_future': {
        'title': 'Past, Present, Future',
        'emoji': '<:fangthinking:720394002636996698>',
        'text': '''3 card reading to give a general comprehension''',
        'unrevealed': 'https://i.imgur.com/R3ZlZeV.png',
        'cards': [
            {
                'title': 'Past',
                'emoji': '☀',
                'text': "What attitudes, feelings, or beliefs in the past (usually recent past, but the Tarot is all about your own interpretation, so feel free to take it further back) have shaped your current situation?"
            },
            {
                'title': 'Present',
                'emoji': '✨',
                'text': "What forces are at play right now? What's going on around you in the present moment that is like, influencing this situation?"
            },
{
                'title': 'Future',
                'emoji': '🌙',
                'text': "What are some possibilities for the future? When I pulled this card, what did it make you think about the possible outcomes of the situation this reading is for?"
            },
        ]
    },

    'sac': {
        'title': 'Situation, Action, Outcome',
        'emoji': '<:trishplotting:720394002339201075>',
        'text': '''3 card spread to understand how you can affect a particular situation''',
        'unrevealed': 'https://i.imgur.com/R3ZlZeV.png',
        'cards': [
            {
                'title': 'Situation',
                'emoji': '🌱',
                'text': "What attitudes, feelings, or beliefs in the past (usually recent past, but the Tarot is all about your own interpretation, so feel free to take it further back) have shaped your current situation?"
            },
            {
                'title': 'Action',
                'emoji': '💧',
                'text': "What forces are at play right now? What's going on around you in the present moment that is like, influencing this situation?"
            },
            {
                'title': 'Outcome',
                'emoji': '🌸',
                'text': "What are some possibilities for the future? When I pulled this card, what did it make you think about the possible outcomes of the situation this reading is for?"
            },
        ]
    },

    'celtic': {
        'title': 'Celtic Cross',
        'emoji': '<:scared:720394002808963082>',
        'text': '''Comprehensive 10 card reading to get a thorough feel of the issue''',
        'unrevealed': 'https://i.imgur.com/HmwJV9i.png', # 'https://i.imgur.com/uqZl0Bc.png',
    },
}

celtic_steps = [
    'The Present',
    'The Problem',
    'The Past',
    'The Future',
    'Conscious',
    'Unconscious',
    'Your Influence',
    'External Influence',
    'Hopes and Fears',
    'Outcome\n',
]

nums = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

readings['celtic']['cards'] = []
for i, step in enumerate(celtic_steps):
    readings['celtic']['cards'].append({
        'title': step,
        'emoji': nums[i]
    })


reactions_format_map = {}

formats_text = ''
for key, format in readings.items():

    reactions_format_map[format['emoji']] = format
    formats_text += f'''{format['emoji']} **{format['title']}**
_{format['text']}_

'''

# member = discord.utils.get(message.guild.members, name='Foo')

# ICON_BACK = '◀️'
# ICON_FORWARD = '▶️'
ICON_BACK = '<:navarrowleft:748735550206378116>'
ICON_FORWARD = '<:navarrowright:748735550260772905>'
ICON_CLOSE = '❌'
# ICON_SHUFFLE = '<:reshuffle:748912920016191711>'
ICON_SHUFFLE = '<:shuffle:750389681400840192>'
ICON_FAVORITE = '⭐'
ARROW = '<:arrow:745744683040243782>'
CHECK = '<:checkfilled:750234516462895104>'

ROMANS = ['0', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI']


roles = {}

db = SqliteDatabase('gvh.db')


class BaseModel(Model):
    class Meta:
        database = db


class Tarot(BaseModel):
    discord_id = IntegerField(unique=True)
    handle = CharField(null=True)
    guild_id = IntegerField()
    favorite = CharField(null=True)
    daily_draw = CharField(null=True)
    daily_time = IntegerField(null=True)
    daily_streak = IntegerField(default=0)
    best_streak = IntegerField(default=0)
    n = IntegerField(default=0)
    n_daily = IntegerField(default=0)


def create_tables():
    with db:
        db.create_tables([Tarot])


class Stella(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.paused = False

        if self.bot.is_ready():
            self.bot.loop.create_task(self.on_load())

    @commands.Cog.listener()
    async def on_ready(self):
        await self.on_load()

    # @checks.is_jacob()
    # @commands.command()
    # async def catchup(self, ctx):
    #     role_reflective = self.bot.guild.get_role(751480955365228694)
    #
    #     for row in Tarot.select():
    #         if row.best_streak >= 7:
    #             member = self.bot.guild.get_member(row.discord_id)
    #             if member:
    #                 await self.bot.achievements.award_role_achievement(self.bot.get_channel(720742722155315331), member, role_reflective,
    #                                                                how='_Get a daily `.tarot` streak of at least **7**_')

    async def on_load(self):
        for card in cards:
            name = card[1]
            if name not in roles:
                roles[name] = discord.utils.get(self.bot.guild.roles, name=name)

            roles['Upright'] = discord.utils.get(self.bot.guild.roles, name='Upright')
            roles['Reversed'] = discord.utils.get(self.bot.guild.roles, name='Reversed')

    # @checks.is_mod()
    @commands.command()
    async def tarot(self, ctx, *, arg=''):
        if self.paused:
            await ctx.send('oh sorry! i’m adding some new features to my deck so i’ll be back soon!')
            return

        session = TarotSession(self.bot, ctx.author)
        session.load_from_db()
        await session.send_initial_prompt(ctx)

    @checks.is_jacob()
    @commands.command(name='tarotpause')
    async def tarot_pause(self, ctx):
        self.paused = not self.paused
        await ctx.send(f'`paused = {self.paused}`')

    @checks.is_jacob()
    @commands.command()
    async def make_db(self, ctx):
        create_tables()

    @checks.is_jacob()
    @commands.command()
    async def db(self, ctx):
        try:
            tarot_row = Tarot.select().where(Tarot.discord_id == ctx.author.id).get()
        except Tarot.DoesNotExist:
            guild_id = ctx.guild.id if ctx.guild is not None else None
            tarot_row = Tarot(discord_id=ctx.author.id,
                              handle=str(ctx.author),
                              guild_id=guild_id)

            tarot_row.save()

    # @checks.is_jacob()
    # @commands.command()
    # async def tarot_roles(self, ctx):
    #     names = {}
    #     for card in cards:
    #         names[card[1]] = card[6]
    #
    #     for name, color in names.items():
    #         await self.bot.guild.create_role(name=name, color=discord.Color(color))
    #
    #     await self.bot.guild.create_role(name='Upright')
    #     await self.bot.guild.create_role(name='Reversed')
    #
    #     print('Done')
    #     await ctx.send('Done')


class TarotSession(object):
    def __init__(self, bot, member):
        self.bot = bot
        self.member = member
        self.format = None
        self.n = None
        self.draw = None
        self.card_reactions = None
        self.revealed = False
        self.tarot_row = None

        self.wfr_message = None

    def load_from_db(self):
        try:
            self.tarot_row = Tarot.select().where(Tarot.discord_id == self.member.id).get()
        except Tarot.DoesNotExist:
            guild_id = self.member.guild.id if self.member.guild is not None else None
            self.tarot_row = Tarot(discord_id=self.member.id,
                              handle=str(self.member),
                              guild_id=guild_id)

            self.tarot_row.save()

    async def handle_reaction(self, reaction, user):
        emoji = str(reaction.emoji)
        if self.format is None:
            if emoji == '❓':
                await self.wfr_message.edit(embed=self.make_help_embed())
            elif emoji == daily_reading['emoji']:
                if not self.daily_claimed():
                    await self.update_prompt_to_readings(emoji)
                else:
                    # TODO single card
                    pass
            elif emoji in reactions_format_map:
                await self.update_prompt_to_readings(emoji)

        else:
            if emoji in self.card_reactions:
                n = self.card_reactions.index(emoji)
                await self.load_card(n)
            elif emoji == ICON_SHUFFLE:
                await self.restart()
            elif emoji == ICON_BACK:
                if self.n is None:
                    await self.load_card(0)
                else:
                    await self.load_card(self.n - 1)
            elif emoji == ICON_FORWARD:
                if self.n is None:
                    await self.load_card(0)
                else:
                    await self.load_card(self.n + 1)
            elif emoji == ICON_FAVORITE:
                if self.revealed:
                    await self.mark_favorite()

    async def send_initial_prompt(self, ctx):
        e = self.make_prompt_embed()
        if not self.wfr_message:
            self.wfr_message = await ctx.send(f'<@{ctx.author.id}>', embed=e)
        else:
            await self.wfr_message.edit(embed=e)
        reactions = ['❓']
        # if not self.daily_claimed():
        reactions += [daily_reading['emoji']]
        reactions += list(reactions_format_map.keys())
        for reaction in reactions:
            await self.wfr_message.add_reaction(reaction.strip('<>'))
            self.bot.wfr[self.member.id] = self


    async def restart(self):
        await self.wfr_message.clear_reactions()
        self.format = None
        self.n = None
        self.draw = None
        self.card_reactions = None
        self.revealed = False
        await self.send_initial_prompt(None)

    def daily_claimed(self):
        t = int(time.time())
        last_midnight = datetime.now(pytz.timezone('US/Eastern')) \
            .replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

        return self.tarot_row.daily_time is not None and self.tarot_row.daily_time > last_midnight

    '''
    intro
    '''
    def make_prompt_embed(self):


        desc = f'''Hiiiiiiii how are you!? I've been honing my Tarot skills over summer break and I wanna test 'em out on all you sweeties 😍 Don't be shy, I can explain how it works 😇

'''
        if not self.daily_claimed():
            desc += f'''{daily_reading['emoji']} **{daily_reading['title']}**
_Ohh, you haven't drawn your daily card yet! Let's do that first? You'll get a pretty role and everything!_

Current Streak: **{self.tarot_row.daily_streak}**
Best Streak: **{self.tarot_row.best_streak}**

'''

        else:
            desc += f'''{daily_reading['emoji']} **{daily_reading['title']}**
[{self.tarot_row.daily_draw}]
_Come back again tomorrow! The day resets at midnight, EST._

Current Streak: **{self.tarot_row.daily_streak}**
Best Streak: **{self.tarot_row.best_streak}**

'''

        desc += f'''{formats_text}❓ if you need an explanation!
'''

        e = discord.Embed(title='Stella\'s Tarot')
        # e.color = 0x77559F
        e.description = desc
        e.set_image(url='https://i.imgur.com/EyiF4Do.pngs')
        # e.set_footer(text='🦕 Goodbye Volcano High')
        return e

    '''
    # help
    '''
    def make_help_embed(self):
        desc = f'''Are you new to Tarot? Or maybe you just need a little refresher? I'd love to show you the ropes!
        
At its core, the Tarot is all about trusting your intuition and tapping into what's on your mind in a way you may not have thought to. **You think about a situation, and pull a card, and then see how that card's interpretation makes you feel. You may agree with it, or disagree with it, but ideally it should make you _think_.**

I can do a few types of readings! As an example, one of the ferns in my garden died recently and I was like, so unbearably sad, like sobbing all day. When I did my Tarot reading — a `yes/no` style reading — I pulled the reversed _Lovers_ and realized I was feeling guilty about being too busy to be there for my friends, and my dead plant made me scared of what could happen to my relationships if I ignored them! Huge revelation for me.

TMI though, sorry. Where was I? What I'm trying to say is that **the Tarot can be a powerful tool to tap into thoughts, and self-reflect**, which I don't think we do _nearly_ enough as a dinociety! Or, if you think it's all a bunch of hooey, it's a good way to kill 5 minutes and look at some pretty art, hee hee! Life is a rich tapestry, and I'm not here to force my thinking on you.

{formats_text}'''

        e = discord.Embed(title='How Tarot Works')
        # e.color = 0x77559F
        e.description = desc
        # e.set_footer(text='🦕 Goodbye Volcano High')
        return e

    async def update_prompt_to_readings(self, emoji):
        daily = emoji == daily_reading['emoji']
        if daily:
            format = self.format = daily_reading
        else:
            format = self.format = reactions_format_map[emoji]

        self.card_reactions = []
        self.draw = random.sample(range(0, 22), len(format['cards']))
        self.draw = [n * 2 + random.choice([0, 1]) for n in self.draw]

        self.tarot_row.n += 1
        self.tarot_row.save()

        await self.wfr_message.clear_reactions()
        reactions = []

        if len(format['cards']) > 1:
            reactions += [ICON_BACK]
            desc = f'''I've drawn a {format['text'].lower()}. Select a card to reveal it:\n'''
        else:
            if daily:
                desc = f'''I've drawn your daily card! Select it to reveal it.\n'''
            else:
                desc = f'''I've drawn a single card. Select it to reveal it.\n'''

        e = discord.Embed(title=format['title'])

        for card in format['cards']:
            reactions += [card['emoji']]
            self.card_reactions += [card['emoji']]
            desc += f'''
{card['emoji']} **{card['title']}**'''
            if 'text' in card:
                desc += f'''\n{card['text']}\n'''

        if len(format['cards']) > 1:
            desc += f'''\n_You may also use {ICON_BACK} and {ICON_FORWARD} to cycle through your cards or {ICON_SHUFFLE} to reshuffle and start again._'''
            reactions += [ICON_FORWARD, ICON_SHUFFLE]
        else:
            reactions += [ICON_SHUFFLE]
            desc += f'''\n_You may also use {ICON_SHUFFLE} to reshuffle and start again._'''

        e.description = desc
        e.set_image(url=format['unrevealed'])
        # e.set_footer(text='🦕 Goodbye Volcano High')
        await self.wfr_message.edit(embed=e)

        for reaction in reactions:
            await self.wfr_message.add_reaction(reaction.strip('<>'))
            self.bot.wfr[self.member.id] = self

    '''
    card reveal
    '''
    async def load_card(self, n):
        if self.n == n:
            return

        if n < 0:
            n = len(self.draw) - 1
        elif n >= len(self.draw):
            n = 0

        self.n = n

        note = None

        daily = self.format['title'] == 'Daily Reading'
        if daily:
            card = cards[self.draw[n]]
            no, name, orientation, tags, explanation, image, color = card
            orientation = 'Upright' if orientation == 'U' else 'Reversed'
            card_name = f'{name} • {orientation}'

            last_midnight = datetime.now(pytz.timezone('US/Eastern')) \
                .replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

            for role in roles.values():
                if role in self.member.roles:
                    await self.member.remove_roles(role)

            await self.member.add_roles(roles[name], roles[orientation])

            self.tarot_row.daily_draw = card_name
            if self.tarot_row.daily_time is not None:

                daily_midnight = datetime.fromtimestamp(self.tarot_row.daily_time, pytz.timezone('US/Eastern')) \
                    .replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
                days_missed = int((last_midnight - daily_midnight) / (3600 * 24)) - 1
                if days_missed > 0:
                    note = f'Streak reset after missing {days_missed} day(s)!'
                    self.tarot_row.daily_streak = 0

            self.tarot_row.daily_time = int(time.time())
            self.tarot_row.daily_streak += 1

            if self.tarot_row.daily_streak == 7:
                role_reflective = self.bot.guild.get_role(751480955365228694)
                await self.bot.achievements.award_role_achievement(self.wfr_message.channel, self.member, role_reflective,
                                                                   how='_Get a daily `.tarot` streak of at least **7**_')

            self.tarot_row.best_streak = max(self.tarot_row.daily_streak, self.tarot_row.best_streak)
            self.tarot_row.save()

        e = self.make_reading_embed(n, note)
        await self.wfr_message.edit(embed=e)

        if not self.revealed:
            self.revealed = True
            await self.wfr_message.add_reaction(ICON_FAVORITE)

    '''
    face up card embed
    '''
    def make_reading_embed(self, n, note=None):

        daily = self.format['title'] == 'Daily Reading'
        reading = self.format['cards'][n]

        card = cards[self.draw[n]]
        no, name, orientation, tags, explanation, image, color = card
        tags = '\n'.join([f'`{tag}`' for tag in tags])
        orientation = 'Upright' if orientation == 'U' else 'Reversed'

        e = discord.Embed(title=f'''{reading['emoji']} {reading['title']} ({n+1} of {len(self.draw)})''', color=color)

        notes = ''
        if note:
            notes += f'''{note}\n\n'''

        if 'text' in reading:
            e.description = f"{notes}_{reading['text']}_"

        if daily:
            explanation += f'''_You have been awarded the **{name} • {orientation}** role. Your daily streak is now **{self.tarot_row.daily_streak}**. Your card of the day resets at midnight, EST._'''

        explanation += f'''\n\n_Use {ICON_FAVORITE} to mark this card as your **favorite**._'''
        e.add_field(name=f'{ROMANS[no]}. {name} • {orientation}', value=f'''{tags}\n\n{explanation}'''[:1024], inline=False)
        e.set_image(url=image)
        e.set_footer(text=f'🦕 {ROMANS[no]}. {name} • {orientation}')
        return e

    async def mark_favorite(self):
        card = cards[self.draw[self.n]]
        no, name, orientation, tags, explanation, image, color = card
        orientation = 'Upright' if orientation == 'U' else 'Reversed'
        card_name = f'{name} • {orientation}'

        if self.tarot_row.favorite != card_name:
            await self.wfr_message.channel.send(f'''<@{self.member.id}> Updated your favorite card: **{self.tarot_row.favorite}** {ARROW} **{card_name}**''')
            self.tarot_row.favorite = card_name
            self.tarot_row.save()




def setup(bot):
    stella = Stella(bot)
    bot.add_cog(stella)
    bot.stella = stella


