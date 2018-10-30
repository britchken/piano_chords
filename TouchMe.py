#!/usr/bin/env python
import sys
import os
import pygame
import pygame.midi
import colorsys
import random
import math
import threading

from pygame.locals import *

class chord:
    def __init__(self, n, k):
        self.name = n
        self.keys = k

# display a list of MIDI devices connected to the computer
def print_device_info():
    for i in range( pygame.midi.get_count() ):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r
        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"
        print ("%2i: interface: %s, name: %s, opened: %s %s" %
               (i, interf, name, opened, in_out))
pygame.init()
pygame.fastevent.init()
event_get = pygame.fastevent.get
event_post = pygame.fastevent.post
pygame.midi.init()

myimage = pygame.image.load("keys.png")
imagerect = myimage.get_rect()
print ("Available MIDI devices:")
print_device_info();

# Change this to override use of default input device
device_id = 1
if device_id is None:
    input_id = pygame.midi.get_default_input_id()
else:
    input_id = device_id
print ("Using input_id: %s" % input_id)
i = pygame.midi.Input( input_id )
print ("Logging started:")

#Animation
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (15,40)
windowSurface = pygame.display.set_mode((1200, 874), 0, 32)
pygame.display.set_caption('Piano chords!')
BLACK = (30, 30, 30)
windowSurface.fill(BLACK)
pygame.display.update()

pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 80)
smallfont = pygame.font.SysFont('Comic Sans MS', 60)
#      C    C#   D   D#    E    F   F#   G     G#   A    A#   B
xx = [26,   55,  103, 144, 190, 237, 270, 316, 351, 392, 435, 476]
yy = [380, 250, 380, 250, 380, 380, 250, 380, 250, 380, 250, 380]

targ = []

def useDice(transpose, chance_type_seven, chance_mod_five, chance_ninths):
    words = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    five = 7
    flat_five = 6
    nine = 2
    flat_nine = 1
    sharp_five = 8
    seventh =     [0, 4, 10]
    min_seventh = [0, 3, 10]
    maj_seventh = [0, 4, 11]
    name = words[transpose]
    if chance_type_seven < 0.33:
        newTarget = seventh
        name = name + "7"
    elif chance_type_seven < 0.66:
        newTarget = min_seventh
        name = name + "min7"
    else:
        newTarget = maj_seventh
        name = name + "maj7"
    if chance_mod_five < 0.1:
        newTarget.append(sharp_five)
        name = name + "#5"
    elif chance_mod_five < 0.2:
        newTarget.append(flat_five)
        name = name + "b5"
    else:
        newTarget.append(five)
    if chance_ninths < 0.1:
        newTarget.append(nine)
        name = name.replace("7", "9")
    newTarget = [(x + transpose)% 12 for x in newTarget]
    return [name, newTarget]

def getTarget():
    global targ
    chance_two_five_one = random.random()
    transpose = random.randint(0,11)

    if (chance_two_five_one < 0.35):
        # 2-5-1 progression
        transpose_two = transpose + 2
        transpose_fiv = transpose + 7
        three_chords = []
        inputs = [
        [(transpose+2)%12, 0.5, random.random(), random.random()],
        [(transpose+7)%12, 0.2, random.random(), random.random()],
        [transpose,        0.9, 1,               1              ]
        ]
        for i in range(3):
            [name, keys] = useDice(*inputs[i])
            c_new = chord(name, keys)
            targ.append(c_new)
    else:
        # Total random chord
        chance_type_seven = random.random()
        chance_mod_five = random.random()
        chance_ninths = random.random()
        [name, keys] = useDice(transpose, chance_type_seven, chance_mod_five, chance_ninths)
        c_new = chord(name, keys)
        targ.append(c_new)

def drawDots(c):
    for i in c:
        a = i%12
        [x, y] = [xx[a], yy[a]]
        pygame.draw.circle(windowSurface, 0xed5500, [x,      y], 20)
        pygame.draw.circle(windowSurface, 0xed5500, [x+503,  y], 20)
        pygame.draw.circle(windowSurface, 0xed5500, [x+996,  y], 20)
    pygame.display.flip()

def drawName(name, next):
    text = myfont.render(name, False, (0xed, 0x95, 0x64))
    smalltext = smallfont.render(next, False, (0xbd, 0x45, 0x30))
    pygame.draw.rect(windowSurface, BLACK, [200,560,800,200], 0)
    windowSurface.blit(text, (200, 560))
    windowSurface.blit(smalltext, (650, 570))

if __name__ == '__main__':
    global targ
    done = 0
    getTarget()
    getTarget()
    getTarget()
    print(targ)
    windowSurface.blit(myimage, imagerect)
    drawDots(targ[0].keys)
    drawName(targ[0].name, targ[1].name)
    while not done:
        events = event_get()
        for e in events:
            if e.type in [pygame.midi.MIDIIN]:
                if (e.data1 > 0 and e.data2 > 0 and e.status == 144):
                    key = e.data1 - 21
                    key = (key-3)%12
                    print("Key pressed: " + str(key))
                    if key in targ[0].keys:
                        targ[0].keys.remove(key)
                        print("Got it!, remaining keys: " + str(targ[0].keys))
                        if len(targ[0].keys) == 0:
                            #remove first element
                            targ.pop(0)
                            if len(targ) == 2:
                                getTarget()
                            drawName(targ[0].name, targ[1].name)
                        drawDots(targ[0].keys)
                        #redraw frame
                        windowSurface.blit(myimage, imagerect)


        # if there are new data from the MIDI controller
        if i.poll():
            midi_events = i.read(1024)
            midi_evs = pygame.midi.midis2events(midi_events, i.device_id)
            for m_e in midi_evs:
                event_post( m_e )
