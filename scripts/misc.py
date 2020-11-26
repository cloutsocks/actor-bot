import re

valid_chars = re.compile(r'[^a-g\s{}\[\]()+]')

def parse_melody(text):
    if re.search(valid_chars, text):
        return False

    notes = []
    current_chord = None

    for c in text.lower():
        if c in '[{(':
            if current_chord is not None:
                return False
            current_chord = ''

        elif c in ']})':
            if not current_chord:
                return False

            notes.append(current_chord[:5])
            current_chord = None

        elif c in 'abcdefg+':
            if current_chord is not None:
                current_chord += c
            else:
                notes.append(c)

    return notes


