#!/usr/bin/env python3

from collections import defaultdict
import math

import speech_recognition as sr
import pygame

width, height = 600, 400
HOVER_THRESHOLD = 100

# set up the keys array
KEYS = {}
for i, letter in enumerate("qwertyuiop"): KEYS[letter] = pygame.Rect(50 * i + 10, 10, 50, 50)
for i, letter in enumerate("asdfghjkl"): KEYS[letter] = pygame.Rect(50 * i + 30, 60, 50, 50)
for i, letter in enumerate("zxcvbnm"): KEYS[letter] = pygame.Rect(50 * i + 50, 110, 50, 50)

# wip: each letter should have an associated weight to it that tells us how likely it is that the user meant to actually type that letter
# wip: need a key model that takes into account the path of the swipe, like corners or loops
# good for demo: polo, ward, red, loom, kite, two, fear, how, the, test

CURRENT_CHOICES = {}
CURRENT_DISPLAYED = ""

# load dictionary
DICTIONARY = defaultdict(list)
with open("wordlist.txt", "rb") as f: # ordered by frequency of use in English
    for i, line in enumerate(f):
        word = line.decode("utf-8", errors="replace").rstrip("\r\n").lower()
        no_dup_word = "".join(letter for j, letter in enumerate(word) if j == 0 or word[j - 1] != letter)
        DICTIONARY[no_dup_word].append((word, i))

def callback(recognizer, audio):
    global CURRENT_DISPLAYED
    try:
        spoken_result = recognizer.recognize_google(audio, show_all=True)
        if spoken_result == []: raise sr.UnknownValueError()
    except sr.UnknownValueError:
        return
    except sr.RequestError:
        return
    possibilities = {entry["transcript"].lower(): i for i, entry in enumerate(spoken_result["alternative"])}
    combined_possibilities = {}
    for possibility, rank in possibilities.items():
        if possibility not in CURRENT_CHOICES: continue
        combined_possibilities[possibility] = rank + 0.1 * math.log(CURRENT_CHOICES[possibility] + 1)
    print(combined_possibilities, possibilities)
    if not combined_possibilities: return # no candidates
    best_candidate = max(combined_possibilities.keys(), key=len) # longest result
    CURRENT_DISPLAYED = " ".join(CURRENT_DISPLAYED.split()[:-1] + [best_candidate])

r = sr.Recognizer()
r.dynamic_energy_threshold = False
r.energy_threshold = 900
m = sr.Microphone()
with m as source: r.adjust_for_ambient_noise(source) # we only need to calibrate once, before we start listening
stop_listening = r.listen_in_background(m, callback)

def n_removals(word, k):
    if k == 0:
        yield word
        return
    if word == "": return
    yield from n_removals(word[1:], k - 1)
    for sequence in n_removals(word[1:], k): yield word[0] + sequence

def word_removals(word, depth = 0):
    """Return all the possible variations of `word` with each letter successively removed, from longest to shortest"""
    if word == "": return
    for i in range(len(word)): yield from n_removals(word, i)

current_swipe = []
def process_swipe(swipe):
    global CURRENT_DISPLAYED

    # `word` is a string of characters with no runs - each character is different from the one before it
    word = "".join(swipe)
    CURRENT_CHOICES.clear()
    for word_variation in word_removals(word):
        if word_variation in DICTIONARY:
            for real_word, rank in DICTIONARY[word_variation]:
                CURRENT_CHOICES[real_word] = rank
    best_candidate = max(CURRENT_CHOICES.items(), key=lambda x: len(x[0]) - 0.1 * math.log(x[1] + 1))[0] # arbitrary ranking function that seems to work well
    CURRENT_DISPLAYED = " ".join(CURRENT_DISPLAYED.split() + [best_candidate])

screen = pygame.display.set_mode((width, height))
pygame.font.init()
keyboard_font = pygame.font.SysFont("monospace", 18)
display_font = pygame.font.SysFont("monospace", 20)
def draw_keyboard(pressed_keys):
    for key, rectangle in KEYS.items():
        if key in pressed_keys:
            screen.fill((255, 255, 255), rectangle)
            label = keyboard_font.render(key, 1, (0, 0, 0))
        else:
            pygame.draw.rect(screen, (255, 255, 255), rectangle, 1)
            label = keyboard_font.render(key, 1, (255, 255, 255))
        screen.blit(label, (rectangle.left + 10, rectangle.top + 10))
while True:
    event = pygame.event.poll()
    if event.type == pygame.QUIT: break

    screen.fill((0, 0, 0))

    button1, _, _ = pygame.mouse.get_pressed()
    if button1:
        pos = pygame.mouse.get_pos()
        current_pressed = set()
        for key, rectangle in KEYS.items():
            if rectangle.collidepoint(pos):
                distance_from_key_center = ((rectangle.centerx - pos[0]) ** 2 + (rectangle.centery - pos[1]) ** 2) ** 0.5

                if not current_swipe or current_swipe[-1] != key:
                    current_swipe.append(key)
                current_pressed = {key}
                break

        draw_keyboard(current_pressed)
    else:
        if current_swipe: process_swipe(current_swipe)
        current_swipe.clear()

        draw_keyboard(set())

    display = display_font.render(CURRENT_DISPLAYED, 1, (255, 255, 255))
    screen.blit(display, (10, 200))

    pygame.display.flip()

pygame.quit()
