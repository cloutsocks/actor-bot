from jam import *


render = Render()

song = Song()

# song.melody = parse_melody('''
# [DG]--- -[c+a][GB][AC+] [GB][DG]-[bD] -[DG]-[bD]
# [CF]-[ca+]-[CF][CE]-[bD]-[aC]-[gb]-[aC]-[bD]
# ''')
#
# render.render(song, uid=-1)


melody = parse_melody('''
ab b#f-- dA# f--dde[ab#b#][ab]

''')

print(melody)

# if result:
#     melody, sharps = result
#     print(melody)
#     print(sharps)

play = Play()
play.load_samples()