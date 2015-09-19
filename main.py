#!/usr/bin/env python3

from collections import defaultdict

import speech_recognition as sr
import pygame

width, height = 600, 300
HOVER_THRESHOLD = 100

# set up the keys array
KEYS = {}
for i, letter in enumerate("qwertyuiop"): KEYS[letter] = pygame.Rect(50 * i + 10, 10, 50, 50)
for i, letter in enumerate("asdfghjkl"): KEYS[letter] = pygame.Rect(50 * i + 30, 60, 50, 50)
for i, letter in enumerate("zxcvbnm"): KEYS[letter] = pygame.Rect(50 * i + 50, 110, 50, 50)

# wip: each letter should have an associated weight to it that tells us how likely it is that the user meant to actually type that letter
# wip: need a key model that takes into account the path of the swipe, like corners or loops

# load dictionary
DICTIONARY = defaultdict(list)
with open("wordlist.txt", "rb") as f:
    for line in f:
        word = line.decode("utf-8", errors="replace").rstrip("\r\n")
        no_dup_word = "".join(letter for i, letter in enumerate(word) if i == 0 or word[i - 1] != letter)
        DICTIONARY[no_dup_word].append(word)

print(DICTIONARY["test"])
def callback(recognizer, audio):
    try:
        spoken_result = recognizer.recognize_google(audio, show_all=True)
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        pass
    possibilities = [entry["transcript"] for entry in spoken_result["alternative"]]
    for transcript in possibilities

r = sr.Recognizer()
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
current_sentence = []
def process_swipe(swipe):
    # `word` is a string of characters with no runs - each character is different from the one before it
    word = "".join(swipe)
    result = set()
    for word_variation in word_removals(word):
        if word_variation == "test": print("aaaa")
        if word_variation in DICTIONARY:
            current_result.extend(DICTIONARY[word_variation])

screen = pygame.display.set_mode((width, height))
pygame.font.init()
font = pygame.font.SysFont("monospace", 18)
def draw_keyboard(pressed_keys):
    for key, rectangle in KEYS.items():
        if key in pressed_keys:
            screen.fill((255, 255, 255), rectangle)
            label = font.render(key, 1, (0, 0, 0))
        else:
            pygame.draw.rect(screen, (255, 255, 255), rectangle, 1)
            label = font.render(key, 1, (255, 255, 255))
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
    pygame.display.flip()

pygame.quit()
