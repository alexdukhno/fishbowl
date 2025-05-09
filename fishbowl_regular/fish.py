import io
import matplotlib.pyplot as plt
import pygame as pg
import numpy as np

class Fish:
    def __init__(self,
            arena=None,
            pos=None, angle=None, vel=None,
            size_coeff=None, species=None,
            gfx_pos=None,gfx_fish_sprite=None,gfx_surface=None
    ):
        self.pos = pos
        self.angle = angle
        self.vel = vel
        self.size_coeff = size_coeff
        self.species = species
        self.arena = arena
        self.gfx_pos = gfx_pos
        self.gfx_fish_sprite = gfx_fish_sprite
        self.gfx_surface = gfx_surface


    def update_direction(self,addangle=None):
        if addangle is not None:
            # self.angle += self.angle*0.03*(np.random.random()-0.5) 
            self.angle += addangle
            if self.angle < -np.pi: self.angle = 2*np.pi + self.angle
            if self.angle > np.pi: self.angle = self.angle - 2*np.pi 


    def update_velocity(self, addvel=None, minvel=None, maxvel=None):
        if addvel is not None:
            #self.vel = np.clip(self.vel + maxvel*0.05*(np.random.random()-0.5), minvel, maxvel)
            self.vel = np.clip(self.vel + addvel, minvel, maxvel)


    def tick(self):
        newpos = [
            self.pos[0] + np.cos(self.angle) * self.vel ,
            self.pos[1] - np.sin(self.angle) * self.vel
        ]
        if newpos[0] > self.arena.dimensions[0]: newpos[0] = newpos[0] - self.arena.dimensions[0]
        if newpos[0] < 0: newpos[0] = self.arena.dimensions[0] - newpos[0]
        if newpos[1] > self.arena.dimensions[1]: newpos[1] = newpos[1] - self.arena.dimensions[1]
        if newpos[1] < 0: newpos[1] = self.arena.dimensions[1] - newpos[1]
        self.pos = newpos


    def render(self):
        render_sprite = pg.transform.smoothscale_by(self.gfx_fish_sprite, self.size_coeff)
        render_sprite = pg.transform.rotate(render_sprite, self.angle * (360/2/np.pi))
        
        self.gfx_pos = (
            self.pos[0]/self.arena.dimensions[0]*self.gfx_surface.width, 
            self.pos[1]/self.arena.dimensions[1]*self.gfx_surface.height
        )
        render_pos = (
            self.gfx_pos[0] - render_sprite.width/2,
            self.gfx_pos[1] - render_sprite.height/2
        )
        
        if self.gfx_surface is not None and self.gfx_fish_sprite is not None:
            self.gfx_surface.blit(render_sprite,render_pos)