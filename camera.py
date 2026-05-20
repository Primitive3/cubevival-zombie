from config import *


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    def follow(self, target):
        self.x = target.x * TILE - SCREEN_W // 2
        self.y = target.y * TILE - SCREEN_H // 2

    def world_to_screen(self, wx, wy):
        return (wx * TILE - self.x, wy * TILE - self.y)

    def screen_to_world(self, sx, sy):
        return ((sx + self.x) / TILE, (sy + self.y) / TILE)

    def get_visible_range(self):
        return (
            max(0, int(self.x / TILE) - 1),
            max(0, int(self.y / TILE) - 1),
            min(MAP_W, int((self.x + SCREEN_W) / TILE) + 2),
            min(MAP_H, int((self.y + SCREEN_H) / TILE) + 2),
        )
