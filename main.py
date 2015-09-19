#!/usr/bin/env python3

import pygame

width, height = 800, 600
KEYS = {}
for i, letter in enumerate("qwertyuiop"): KEYS[letter] = pygame.Rect(50 * i + 10, 10, 50, 50)
for i, letter in enumerate("asdfghjkl"): KEYS[letter] = pygame.Rect(50 * i + 30, 60, 50, 50)
for i, letter in enumerate("zxcvbnm"): KEYS[letter] = pygame.Rect(50 * i + 50, 110, 50, 50)

#wip: represent the streak as a sequence of lists of pairs containing letters and the distances from the center of their rectangle

current_streak = []

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
    if event.type == pygame.QUIT:
        break

    screen.fill((0, 0, 0))

    button1, _, _ = pygame.mouse.get_pressed()
    if button1:
        pos = pygame.mouse.get_pos()
        current_pressed = set()
        for key, rectangle in KEYS.items():
            if rectangle.collidepoint(pos):
                current_streak.append(key)
                current_pressed = {key}


        draw_keyboard(current_pressed)
    else:
        current_streak.clear()

        draw_keyboard(set())
    pygame.display.flip()

pygame.quit()