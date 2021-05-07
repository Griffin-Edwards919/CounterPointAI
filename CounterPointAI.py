from midiutil import MIDIFile

NOTES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


class CantusFirmus:
    def __init__(self, author, species, tonic, mode, cantus):
        self.author = author
        self.species = species
        self.tonic = tonic
        self.mode = mode
        self.cantus = cantus

    def __str__(self):
        return "Species " + self.species + " Cantus Firmus in " + self.tonic + " " + self.mode + " by " + self.author


class AI:
    def __init__(self, cantusfirmus):
        self.cantusfirmus = cantusfirmus

    def getDist(self, note1, note2):
        try:
            dist = NOTES.index(note2) - NOTES.index(note1)
            if dist < 0:
                dist += 12
        except:
            dist = -1
        return dist

    def getChoices(self, tonic, root, bass, mode):
        choices = []
        root = root[:-1]
        scale = self.getScale(tonic[:-1], mode)
        if bass:
            third = scale[(scale.index(root) + 5) % 7]
            fifth = scale[(scale.index(root) + 3) % 7]
            sixth = scale[(scale.index(root) + 2) % 7]
            notes = [root, third, fifth, sixth]
            for note in notes:
                for i in range(5):
                    if i > 1 and self.isHigher(note + str(i), "D2") and self.isLower(note + str(i), "A4"):
                        choices.append(note + str(i))
        else:
            third = scale[(scale.index(root) + 2) % 7]
            fifth = scale[(scale.index(root) + 4) % 7]
            sixth = scale[(scale.index(root) + 5) % 7]
            notes = [root, third, fifth, sixth]
            for note in notes:
                for i in range(6):
                    if i > 3 and self.isHigher(note + str(i), "B3") and self.isLower(note + str(i), "A5"):
                        choices.append(note + str(i))
        return choices

    def getDegree(self, note, octave):
        try:
            return NOTES.index(note) + octave * 12 + 12
        except:
            return None

    def isLower(self, note1, note2):
        return note1[-1] < note2[-1] or (note1[-1] == note2[-1] and NOTES.index(note1[:-1]) < NOTES.index(note2[:-1]))

    def isHigher(self, note1, note2):
        return self.isLower(note2, note1)

    def score(self, counterpoint, cantusfirmus, bass, mode):  # If bass is true, counterpoint is in the bass clef
        cp = []
        cf = []
        intervals = ""
        sdistances = ""
        bdistances = ""
        score = 0
        highest = counterpoint[0]
        lowest = counterpoint[0]
        for note in cantusfirmus:
            cf.append(note[:-1])
        for i in range(len(counterpoint)):
            cp.append(counterpoint[i][:-1])
            if i == len(cantusfirmus) - 2 and mode == "Minor":
                if cp[i] != self.getScale(cantusfirmus[0][:-1], mode)[-1]:
                    return -10000000 #Not ending with leading tone in minor
            if bass:
                if self.isLower(counterpoint[i], "E2") or self.isHigher(counterpoint[i], "G4") or \
                        self.isHigher(counterpoint[i], cantusfirmus[i]):
                    return -10000000  #Improper ranges
                if i > 0 and (self.isHigher(counterpoint[i], cantusfirmus[i - 1]) or
                              self.isHigher(counterpoint[i - 1], cantusfirmus[i])):
                    return -10000000  #Voice overlap
                intervals += str(hex(self.getDist(cp[i], cf[i])))[2:]
                if i > 0:
                    bdistances += str(hex(self.getDist(cp[i - 1], cp[i])))[-1]
                    sdistances += str(hex(self.getDist(cf[i - 1], cf[i])))[-1]
            else:
                if self.isLower(counterpoint[i], "C4") or self.isHigher(counterpoint[i], "G5") or \
                        self.isLower(counterpoint[i], cantusfirmus[i]):
                    return -10000000  # Improper ranges
                if i > 0 and (self.isHigher(cantusfirmus[i], counterpoint[i - 1]) or
                              self.isHigher(cantusfirmus[i - 1], counterpoint[i])):
                    return -10000000  #Voice overlap
                if self.isLower(counterpoint[i], lowest): lowest = counterpoint[i]
                if self.isHigher(counterpoint[i], highest): highest = counterpoint[i]
                intervals += str(hex(self.getDist(cf[i], cp[i])))[2:]
                if i > 0:
                    sdistances += str(hex(self.getDist(cp[i - 1], cp[i])))[-1]
                    bdistances += str(hex(self.getDist(cf[i - 1], cf[i])))[-1]
        if (intervals[0] != "0" and intervals[0] != "7") or \
                (len(intervals) == len(cf) and (intervals[-1] != "0" or intervals[-2] == "7")) or ("00" in intervals) or \
                ("77" in intervals) or ("6" in intervals):
            return -10000000  # Parallel octaves, parallel fifths, tri-tones, and improper opening and closing harmony
        tcounter = 0
        scounter = 0
        for interval in intervals:
            if interval == "3" or interval == "4":
                tcounter += 1
                scounter = 0
            if interval == "8" or interval == "9":
                scounter += 1
                tcounter = 0
            else:
                tcounter = 0
                scounter = 0
            if tcounter > 3 or scounter > 3:
                return -10000000  # Too many parallel imperfect consonances
        for i in range(len(cp) - 1):
            if not bass:
                if str(sdistances[i]) not in "0123489ab":  # Leap in the soprano
                    score -= 5
                    if sdistances[i] in "6":
                        return -10000000  # Leap of a tri-tone
                    if intervals[i + 1] == "0" or intervals[i + 1] == "7":
                        return -10000000  # Leap into a fifth or octave
                    if self.isHigher(counterpoint[i], counterpoint[i + 1]):
                        if i > 0 and str(sdistances[i - 1]) not in "01234":
                            return -10000000  # Leap not approached by contrary step/skip
                        if i < len(sdistances) - 1 and str(sdistances[i + 1]) not in "01234":
                            return -10000000  # Leap not followed by contrary step/skip
                    else:
                        if self.getDist(counterpoint[i][:-1], counterpoint[i + 1][:-1]) + 12 * (
                                int(counterpoint[i][-1]) - int(counterpoint[i + 1][-1])) > 11:
                            return -10000000
                        if i > 0 and sdistances[i - 1] not in "89ab0":
                            return -10000000  # Leap not approached by contrary step/skip
                        if i < len(sdistances) - 1 and sdistances[i + 1] not in "89ab0":
                            return -10000000  # Leap not followed by contrary step/skip
                elif self.isHigher(counterpoint[i], counterpoint[i + 1]) and str(sdistances[i]) in "89" and \
                        i < len(sdistances) - 1 and str(sdistances[i + 1]) in "89":
                    return -10000000  # Multiple skips in a row
                elif self.isLower(counterpoint[i], counterpoint[i + 1]) and str(sdistances[i]) in "34" and \
                        i < len(sdistances) - 1 and str(sdistances[i + 1]) in "34":
                    return -10000000
            elif bass and str(bdistances[i]) not in "0123489ab": score -= 5
            if (self.isHigher(counterpoint[i], counterpoint[i + 1]) and
                self.getDist(counterpoint[i + 1][:-1], counterpoint[i][:-1]) +
                12 * (int(counterpoint[i][-1]) - int(counterpoint[i + 1][-1])) > 11) or \
                    (self.isHigher(counterpoint[i + 1], counterpoint[i]) and
                     self.getDist(counterpoint[i][:-1], counterpoint[i + 1][:-1]) +
                     12 * (int(counterpoint[i + 1][-1]) - int(counterpoint[i][-1])) > 11):
                return -10000000 #Leap of an octave or more
        score += self.getDist(lowest[:-1], highest[:-1]) + 12 * (int(highest[-1]) - int(lowest[-1]))  #Scoring based on interest of melody
        return score

    def solve(self, counterpoint, cantus, bass, mode):
        global answer, highscore
        score = 0
        if len(counterpoint) == 0:
            answer = []
            highscore = -100
        choices = self.getChoices(cantus[0], cantus[len(counterpoint)], bass, mode)
        for choice in choices:
            cp = counterpoint.copy()
            cp.append(choice)
            if len(counterpoint) == 0:
                print(cp)
            score = self.score(cp, cantus, bass, mode)
            if score > -1000:
                if len(cp) == len(cantus): return cp, score
                temp, score = self.solve(cp, cantus, bass, mode)
                if score > highscore:
                    highscore = score
                    answer = temp
                    print(answer)
        return answer, highscore

    def getScale(self, tonic, mode):
        if mode == "Major":
            scale = [tonic, NOTES[(NOTES.index(tonic) + 2) % 12],
                     NOTES[(NOTES.index(tonic) + 4) % 12],
                     NOTES[(NOTES.index(tonic) + 5) % 12], NOTES[(NOTES.index(tonic) + 7) % 12],
                     NOTES[(NOTES.index(tonic) + 9) % 12], NOTES[(NOTES.index(tonic) + 11) % 12]]
        else:
            scale = [tonic, NOTES[(NOTES.index(tonic) + 2) % 12],
                     NOTES[(NOTES.index(tonic) + 3) % 12],
                     NOTES[(NOTES.index(tonic) + 5) % 12], NOTES[(NOTES.index(tonic) + 7) % 12],
                     NOTES[(NOTES.index(tonic) + 8) % 12], NOTES[(NOTES.index(tonic) + 10) % 12]]
        return scale

cantusfirmi = []
for line in open("Cantus Firmi.txt"):
    args = line.split(";")
    cantusfirmi.append(CantusFirmus(args[0], args[1], args[2], args[3], args[4][:-1].split(',')))

while True:
    print("Select a Cantus Firmus:")
    for i in range(len(cantusfirmi)):
        print(str(i + 1) + ") " + str(cantusfirmi[i]))
    try:
        ans = int(input())
        if 8 > ans > 0:
            cantus = cantusfirmi[ans - 1]
            break
        else:
            print("Error please enter valid input")
    except:
        print("Error please enter valid input")

while True:
    ans = input("Should the Cantus Firmus be in the bass clef (b) or treble clef (t)?\n").upper()
    if ans == "B" or ans == "T": break
    print("Error please enter valid input")

bass = ans == "T"

if bass:
    for i in range(len(cantus.cantus)):
        cantus.cantus[i] = cantus.cantus[i][:-1] + str(int(cantus.cantus[i][-1]) + 1)
ai = AI(cantus)
counterpoint = ai.solve([], cantus.cantus, bass, cantus.mode)
score = counterpoint[1]
counterpoint = counterpoint[0]
if cantus.mode == "Minor":  counterpoint[-2] = NOTES[(NOTES.index(counterpoint[-2][:-1]) + 1) % 12] + counterpoint[-2][-1]
print("Counterpoint: ", counterpoint, " Score: ", score)

track = 0
channel = 0
time = 0
duration = 2
tempo = 120
volume = 100

MyMIDI = MIDIFile(1)
MyMIDI.addTempo(track, time, tempo)

for i, pitch in enumerate(cantus.cantus):
    MyMIDI.addNote(track, channel, ai.getDegree(pitch[:-1], int(pitch[-1])), time + 2 * i, duration, volume)

for i, pitch in enumerate(counterpoint):
    MyMIDI.addNote(track, channel, ai.getDegree(pitch[:-1], int(pitch[-1])), time + 2 * i, duration, volume)

with open("Counterpoint-" + cantus.author + "-Species" + cantus.species + "-" + cantus.tonic + cantus.mode +
          ("-BassClef" if bass else "-TrebleClef") + ".mid", "wb") as output_file:
    MyMIDI.writeFile(output_file)
