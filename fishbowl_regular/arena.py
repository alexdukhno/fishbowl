import io
import matplotlib.pyplot as plt
import pygame as pg
class Arena:
    def __init__(self,dimensions=None,gfx_arena_surface_dims=None,gfx_arena_surface_location=None,render_surface=None,bgd_sprite=None):
        self.dimensions = dimensions
        self.gfx_arena_surface_dims = gfx_arena_surface_dims
        self.gfx_arena_surface_location = gfx_arena_surface_location
        self.gfx_surface = pg.Surface(gfx_arena_surface_dims)
        self.render_surface = render_surface
        if bgd_sprite is not None:
            self.bgd_sprite = pg.transform.scale(bgd_sprite,(self.gfx_surface.width,self.gfx_surface.height))
        else:
            self.bgd_sprite = None
        self.gfx_clear()        

    def gfx_clear(self):
        if self.bgd_sprite is None:
            self.gfx_surface.fill((20, 20, 20))
        else:
            self.gfx_surface.blit(self.bgd_sprite,(0,0))

    def render(self):                
        self.render_surface.blit(self.gfx_surface,self.gfx_arena_surface_location)