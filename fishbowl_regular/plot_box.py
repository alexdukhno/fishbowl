import io
import matplotlib.pyplot as plt
import pygame as pg
class PlotBox:
    def __init__(self, surface, pos, update_every_n_gfx_ticks, fig_renderer):
        self.surface = surface
        self.pos = pos
        self.fig_renderer = fig_renderer
        self.update_every_n_gfx_ticks = update_every_n_gfx_ticks
        self.gfx_ticks_elapsed = -1 # always render first time
        self.last_sprite_surface = None

    def render(self, *args, **kwargs):        
        self.gfx_ticks_elapsed += 1
        if (self.gfx_ticks_elapsed >= self.update_every_n_gfx_ticks) or (self.gfx_ticks_elapsed <= 0):
            self.gfx_ticks_elapsed = 0
            
            sprite = io.BytesIO()
            fig = self.fig_renderer(*args,**kwargs)
            fig.savefig(sprite, format='png')
            plt.close(fig)
            sprite.seek(0)            
            plotsurface = pg.image.load(sprite).convert()   
            self.last_sprite_surface = plotsurface
        else: 
            plotsurface = self.last_sprite_surface

        if plotsurface is not None:
            self.surface.blit(plotsurface,self.pos)        
