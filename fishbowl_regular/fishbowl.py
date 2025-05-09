#!/usr/bin/env python
import os
import time
import pygame as pg

import io
import matplotlib.pyplot as plt

import numpy as np
import scipy

from fps_counter import FPSCounter
from plot_box import PlotBox
from fish import Fish
from arena import Arena

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)

pg.init()

UPDATEGFX = pg.USEREVENT + 1

RES = (1000, 800)
calc_target_FPS = 300
visual_target_FPS = 60
sim_speed_mult = 1
clock = pg.time.Clock()

screen = pg.display.set_mode(RES, pg.RESIZABLE)
pg.display._set_autoresize(False)

fps_counter = FPSCounter(screen, pg.font.Font(None, 36), clock, (0,255,0), (0, 0))
fps_counter.pos = (screen.get_width() - 120, 20)


# =======================================================
# initialization for core logic

arena_dimensions = (100,100)
arena_surface_dims = (700,700)
arena_surface_location = (50,50)
arena = Arena(
    dimensions=arena_dimensions,    
    gfx_arena_surface_dims=arena_surface_dims,
    gfx_arena_surface_location=arena_surface_location,
    render_surface=screen,
    bgd_sprite=pg.image.load(os.path.join(str(os.getcwd()), 'assets', 'reef_650x650_darker.png')).convert_alpha(),
)

N_fishes = 100
N_species = 6
N_fish_sprites = 3
#species_colors = [np.random.random()*360 for s in range(N_species)]
species_colors = np.linspace(0,360,N_species+1)[:-1]
min_fish_vel, max_fish_vel = 8 / calc_target_FPS * sim_speed_mult, 10 / calc_target_FPS * sim_speed_mult # arena dim units per calc frame
min_fish_size_coeff, max_fish_size_coeff = 0.8 , 1.30
turn_speed = 3.14 / calc_target_FPS * sim_speed_mult # radian units per calc frame
repelling_distance = 1.5 # arena dim units
aligning_distance = 3.3 # arena dim units

fish_list = []
fish_sprites = [pg.image.load(os.path.join(str(os.getcwd()), 'assets', f'fish_sprite_{i % N_fish_sprites + 1}_30x30_red_fill.png')).convert_alpha() for i in range(N_species)]
species_sprite_list = [pg.transform.hsl(fish_sprites[i], species_colors[i % N_species], -0.3, -0.2) for i in range(N_species)]

for i in range(N_fishes):
    new_fish_species = i % N_species
    #new_fish_sprite = pg.transform.hsl(fish_sprite, species_colors[new_fish_species], 0.3, 0.2)
    new_fish_sprite = pg.transform.hsl(species_sprite_list[new_fish_species], (np.random.random()-0.5)*0.01, (np.random.random()-0.5)*0.1, (np.random.random()-0.5)*0.2)
    new_fish = Fish(
        arena=arena,
        pos=(np.random.random()*arena.dimensions[0], np.random.random()*arena.dimensions[1]),
        angle=(np.random.random()-0.5)*2*np.pi,
        vel=np.random.random()*max_fish_vel,
        species=new_fish_species,
        gfx_fish_sprite=new_fish_sprite, gfx_surface=arena.gfx_surface,
        size_coeff=min_fish_size_coeff + np.random.random()*(max_fish_size_coeff-min_fish_size_coeff),
    )
    fish_list.append(new_fish)

# =======================================================
# initialization for plots, UI etc.

def render_plot(x,y,c):
    figsize=(2,2)
    fig,ax = plt.subplots(figsize=figsize)
    ax.scatter(x,y,c=c,cmap='gist_rainbow')
    ax.set_xlim(0,arena.dimensions[0])
    ax.set_ylim(0,arena.dimensions[1])
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    return fig
plot_box = PlotBox(screen,(800,100),60,render_plot)

# =======================================================
# MAIN LOOP
curr_time = time.time()
last_gfx_update_time = curr_time
gfx_frame_delay_s = 1 / visual_target_FPS
gfx_update_times = np.array([curr_time] * 10)

calc_tick = 0
calc_tick_loopback = 3000
done = False

while not done:
    # ---------------------
    # main calculation tick
    # ---------------------
    calc_tick += 1
    if calc_tick>=calc_tick_loopback: calc_tick = 0

    if calc_tick % 1 == 0:

        fish_coords = np.array([[fish.pos[0] for fish in fish_list],[fish.pos[1] for fish in fish_list]]).T
        fish_lookup_tree = scipy.spatial.KDTree(fish_coords, leafsize=5)

        for fish in fish_list:
            nearest_fish_idx = fish_lookup_tree.query((fish.pos[0],fish.pos[1]),k=2)[1][1]
            nearest_fish_pos = fish_coords[nearest_fish_idx] # nearest fish is second in the list bc the first is the query fish itself
            nearest_fish_angle = fish_list[nearest_fish_idx].angle
            nearest_fish_species = fish_list[nearest_fish_idx].species
            desired_angle = np.atan2(
                [-nearest_fish_pos[1]+fish.pos[1]],
                [nearest_fish_pos[0]-fish.pos[0]]
            )[0]
            # fish_dir_v = np.array([np.cos(fish.angle),np.sin(fish.angle)])
            # fish_dir_v = fish_dir_v / np.linalg.norm(fish_dir_v)
            # dir_towards_nearest_fish_v = np.array([np.cos(desired_angle),np.sin(desired_angle)])
            # dir_towards_nearest_fish_v = dir_towards_nearest_fish_v / np.linalg.norm(dir_towards_nearest_fish_v)
            # angle_correction = np.arccos(np.dot(dir_towards_nearest_fish_v,fish_dir_v))
            # # desired_angle = np.atan2([nearest_fish_pos[1]],[nearest_fish_pos[0]]) - np.atan2([fish.pos[1]],[fish.pos[0]])
            # # angle_correction = desired_angle
            # print(f'fish pos {fish.pos}, nearest fish pos {nearest_fish_pos}, desired angle {desired_angle}, fish angle {fish.angle}, correction_angle {angle_correction}')
            dist_to_nearest_fish = np.sqrt((fish.pos[0]-nearest_fish_pos[0])**2 + (fish.pos[1]-nearest_fish_pos[1])**2)
            
            fish_dir_v = np.array([np.cos(fish.angle),np.sin(fish.angle)])
            fish_dir_v = fish_dir_v / np.linalg.norm(fish_dir_v)
            
            nearest_fish_dir_v = np.array([np.cos(nearest_fish_angle),np.sin(nearest_fish_angle)])
            nearest_fish_dir_v = nearest_fish_dir_v / np.linalg.norm(nearest_fish_dir_v)
            
            dir_towards_nearest_fish_v = np.array([np.cos(desired_angle),np.sin(desired_angle)])
            dir_towards_nearest_fish_v = dir_towards_nearest_fish_v / np.linalg.norm(dir_towards_nearest_fish_v)

            if dist_to_nearest_fish <= repelling_distance:
                # if too close, move away
                dot = fish_dir_v[0]*dir_towards_nearest_fish_v[0] + fish_dir_v[1]*dir_towards_nearest_fish_v[1]
                det = -fish_dir_v[0]*dir_towards_nearest_fish_v[1] + fish_dir_v[1]*dir_towards_nearest_fish_v[0]
                angle_correction = np.atan2(det, dot)
                angle_correction = -angle_correction
            elif (dist_to_nearest_fish <= aligning_distance) and (np.abs(fish.species-nearest_fish_species)<=1):
                # if kinda close, align
                dot = fish_dir_v[0]*nearest_fish_dir_v[0] + fish_dir_v[1]*nearest_fish_dir_v[1]
                det = -fish_dir_v[0]*nearest_fish_dir_v[1] + fish_dir_v[1]*nearest_fish_dir_v[0]
                angle_correction = np.atan2(det, dot)
            elif (dist_to_nearest_fish <= aligning_distance) and (np.abs(fish.species-nearest_fish_species)>1):
                # if diff species, move away instead of aligning
                dot = fish_dir_v[0]*dir_towards_nearest_fish_v[0] + fish_dir_v[1]*dir_towards_nearest_fish_v[1]
                det = -fish_dir_v[0]*dir_towards_nearest_fish_v[1] + fish_dir_v[1]*dir_towards_nearest_fish_v[0]
                angle_correction = np.atan2(det, dot)
                angle_correction = -angle_correction      
            elif fish.species==nearest_fish_species:
                # if same species afar, move closer
                dot = fish_dir_v[0]*dir_towards_nearest_fish_v[0] + fish_dir_v[1]*dir_towards_nearest_fish_v[1]
                det = -fish_dir_v[0]*dir_towards_nearest_fish_v[1] + fish_dir_v[1]*dir_towards_nearest_fish_v[0]
                angle_correction = np.atan2(det, dot)            
            else: 
                angle_correction=0

            #print(f'fish pos {fish.pos}, nearest fish pos {nearest_fish_pos}, desired angle {desired_angle}, fish angle {fish.angle}, correction_angle {angle_correction}')

            fish.update_direction(addangle=-np.sign(angle_correction)*turn_speed*(0.1+np.random.random()*0.9)*2)
            fish.update_velocity(addvel=(np.random.random()-0.5)*max_fish_vel*0.05, minvel=min_fish_vel, maxvel=max_fish_vel)        
        
    for fish in fish_list:
        fish.tick()

    #x = np.random.randint(0,800,20)
    #y = np.random.randint(0,800,20)
    x = np.array([fish.pos[0] for fish in fish_list])
    y = np.array([fish.pos[1] for fish in fish_list]) 
    c = np.array([fish.species for fish in fish_list])

    # ---------------------
    #     event handling    
    # ---------------------
    curr_time = time.time()
    if curr_time - last_gfx_update_time >= gfx_frame_delay_s: pg.event.post(pg.event.Event(UPDATEGFX))

    for event in pg.event.get():

        if event.type == pg.KEYDOWN and event.key == pg.K_q:
            done = True

        if event.type == pg.QUIT:
            done = True

        if event.type == pg.VIDEORESIZE:
            screen = pg.display.get_surface()
            fps_counter.pos = (screen.get_width() - 120, 20)

        # -----------------------------
        # Main graphics update tick
        # -----------------------------
        if event.type == UPDATEGFX: 
            screen.fill((50, 50, 50))

            plot_box.render(x,y,c)

            gfx_update_times = np.roll(gfx_update_times,-1)
            gfx_update_times[-1] = curr_time
            fps_counter.render()
            fps_counter.update(1 / np.mean(np.diff(gfx_update_times)))
            
            arena.gfx_clear()            
            for fish in fish_list:
                fish.render()
            arena.render()

            pg.display.flip()
            last_gfx_update_time = curr_time

    clock.tick(calc_target_FPS)
    #clock.tick_busy_loop(calc_target_FPS)


pg.quit()    