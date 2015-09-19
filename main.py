#!/usr/bin/env python3

import speech_recognition as sr

import pygame

width, height = 800, 600
HOVER_THRESHOLD = 100

# set up the keys array
KEYS = {}
for i, letter in enumerate("qwertyuiop"): KEYS[letter] = pygame.Rect(50 * i + 10, 10, 50, 50)
for i, letter in enumerate("asdfghjkl"): KEYS[letter] = pygame.Rect(50 * i + 30, 60, 50, 50)
for i, letter in enumerate("zxcvbnm"): KEYS[letter] = pygame.Rect(50 * i + 50, 110, 50, 50)

# wip: each letter should have an associated weight to it that tells us how likely it is that the user meant to actually type that letter
# wip: need a key model that takes into account the path of the swipe, like corners or loops

# load dictionary
DICTIONARY = set()
with open("wordlist.txt", "r") as f:
    for word in f: DICTIONARY.add(word)

def callback(recognizer, audio):
    try:
        print("Google Speech Recognition thinks you said " + recognizer.recognize_google(audio))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service")
r = sr.Recognizer()
m = sr.Microphone()
with m as source: r.adjust_for_ambient_noise(source) # we only need to calibrate once, before we start listening
stop_listening = r.listen_in_background(m, callback)

current_swipe = []
def process_swipe(swipe):
    print(swipe)

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
