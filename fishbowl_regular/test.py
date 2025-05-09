#!/usr/bin/env python
import os
import pygame as pg

import io
import matplotlib.pyplot as plt

import numpy as np

from fps_counter import FPSCounter

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)

pg.init()

RES = (1200, 1200)
FPS = 60
clock = pg.time.Clock()

screen = pg.display.set_mode(RES, pg.RESIZABLE)
pg.display._set_autoresize(False)

# MAIN LOOP

done = False

i = 0
j = 0
step = 15

font = pg.font.Font(None, 36)
fps_counter = FPSCounter(screen, font, clock, (0,255,0), (150, 10))

while not done:
    x = np.random.random(100)
    y = np.random.random(100)    
    figsize=(2,2)
    fig,ax = plt.subplots(figsize=figsize)
    ax.scatter(x,y)

    picture = io.BytesIO()
    fig.savefig(picture, format='png')
    plt.close(fig)
    picture.seek(0)
    plotsurface = pg.image.load(picture).convert()

    for event in pg.event.get():
        if event.type == pg.KEYDOWN and event.key == pg.K_q:
            done = True
        if event.type == pg.QUIT:
            done = True
        # if event.type==pg.WINDOWRESIZED:
        #    screen=pg.display.get_surface()
        if event.type == pg.VIDEORESIZE:
            screen = pg.display.get_surface()
    i += step
    i = i % screen.get_width()
    j += step / 2
    j = j % screen.get_height()

    screen.fill((255, 0, 255))
    # pg.draw.circle(screen, (0, 0, 0), (100, 100), 20)
    # pg.draw.circle(screen, (0, 0, 200), (0, 0), 10)
    # pg.draw.circle(screen, (200, 0, 0), (160, 120), 30)
    # pg.draw.line(screen, (250, 250, 0), (0, 120), (160, 0))
    pg.draw.circle(screen, (255, 255, 255), (i, j), 5)
    screen.blit(plotsurface,(0,0))
   
    fps_counter.render()
    fps_counter.update()

    pg.display.flip()
    clock.tick(FPS)
pg.quit()