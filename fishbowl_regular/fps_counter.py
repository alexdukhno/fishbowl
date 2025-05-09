import pygame as pg
class FPSCounter:
    def __init__(self, surface, font, clock, color, pos):
        self.surface = surface
        self.font = font
        self.clock = clock
        self.pos = pos
        self.color = color

        self.fps_text = self.font.render(str(int(self.clock.get_fps())) + "FPS", False, self.color)
        self.fps_text_rect = self.fps_text.get_rect(center=(self.pos[0], self.pos[1]))

    def render(self):
        pg.draw.rect(self.surface,(50, 50, 50),pg.Rect(self.pos[0],self.pos[1], 100,30))
        self.surface.blit(self.fps_text, self.fps_text_rect)

    def update(self, viz_fps=0):
        text = f"{self.clock.get_fps():.0f} CFPS, {viz_fps:.0f} VFPS"
        self.fps_text = self.font.render(text, False, self.color)
        self.fps_text_rect = self.fps_text.get_rect(center=(self.pos[0], self.pos[1]))