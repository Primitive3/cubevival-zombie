import pygame
import sys
import math
import random

from config import *
from entities import Player, ItemDrop
from world import World
from camera import Camera
from ui import HUD
from sprites import get_zombie_sprite, get_player_sprite, get_item_sprite
from sounds import play as play_sound
from saveload import save_game, load_game

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Sobreviviente Sin CV")
clock = pygame.time.Clock()

_night_overlay = None
_flash_surf = None
_light_cache = {}
_time_labels = {}
_pause_overlay = None

_tile_cache = {}
_fog_tile_cache = {}

def _make_tile_surface(tile, var):
    s = pygame.Surface((TILE, TILE))
    c = TILE_COLORS[tile]
    pygame.draw.rect(s, c, (0, 0, TILE, TILE))
    if tile == T_GRASS:
        v4 = var & 3
        grass_clumps = [(8, 8, 5, 4), (20, 5, 4, 4), (5, 20, 5, 4), (24, 22, 5, 4)]
        for dx, dy in ((3, 12), (14, 3), (25, 14), (9, 26), (18, 26)):
            pygame.draw.circle(s, ((var * 7 + dx * 3) % 30 + 45, (var * 11 + dy * 5) % 25 + 100, (var * 5 + dx * 7) % 15 + 35), (dx, dy), 1)
        pygame.draw.rect(s, (48, 108, 38), grass_clumps[v4])
        if var & 1:
            for fi in range(2):
                fx = (fi * 19 + var * 7) % 26 + 3
                fy = (fi * 23 + var * 13) % 26 + 3
                pygame.draw.circle(s, ((var * 30 + 220) % 50 + 200, (var * 20 + 170) % 60 + 90, (var * 10 + 200) % 50 + 50), (fx, fy), 1)
                pygame.draw.circle(s, ((var * 25 + 230) % 45 + 195, (var * 15 + 180) % 50 + 100, (var * 5 + 210) % 40 + 55), (fx + 1, fy + 1), 1)
    elif tile == T_ROAD:
        v4 = var & 3
        if v4 == 0:
            for cx in (8, 16, 24):
                pygame.draw.rect(s, (90, 90, 90), (cx, 0, 2, TILE))
        elif v4 == 1:
            pygame.draw.rect(s, (100, 100, 80), (13, 15, 6, 2))
            for cx in (6, 22):
                pygame.draw.rect(s, (60, 60, 60), (cx, 10, 3, 3))
                pygame.draw.rect(s, (60, 60, 60), (cx, 20, 3, 3))
        elif v4 == 2:
            for cx in (2, 10, 18, 26):
                pygame.draw.line(s, (50, 50, 50), (cx, 0), (cx, TILE))
        else:
            for cx in (4, 20):
                pygame.draw.rect(s, (85, 85, 85), (cx, 0, 2, TILE))
        if var >= 8 and var < 12:
            for si in range(2):
                sx = (si * 15 + var * 5) % 24 + 4
                sy = (si * 11 + var * 7) % 20 + 6
                pygame.draw.rect(s, (95, 95, 95), (sx, sy, 4, 2))
    elif tile == T_WALL:
        v4 = var & 3
        wall_base = (140, 90, 55)
        shadow = (90, 55, 30)
        roof = (100, 65, 40)
        pygame.draw.rect(s, wall_base, (0, 0, TILE, TILE))
        pygame.draw.rect(s, shadow, (0, 0, TILE, 3))
        pygame.draw.rect(s, shadow, (0, TILE - 2, TILE, 2))
        pygame.draw.rect(s, shadow, (0, 0, 2, TILE))
        if v4 == 0:
            for ly in (6, 14, 22):
                pygame.draw.line(s, roof, (0, ly), (TILE, ly), 2)
            pygame.draw.rect(s, roof, (12, 4, 8, 2))
        elif v4 == 1:
            pygame.draw.rect(s, (150, 110, 75), (2, 4, 4, 4))
            for ly in (8, 16, 24):
                pygame.draw.line(s, roof, (0, ly), (TILE, ly))
            for lx in (8, 16, 24):
                pygame.draw.line(s, roof, (lx, 0), (lx, TILE))
        elif v4 == 2:
            pygame.draw.rect(s, roof, (0, 6, TILE, 2))
            pygame.draw.rect(s, roof, (0, 14, TILE, 2))
            pygame.draw.rect(s, roof, (0, 22, TILE, 2))
            for wx in (3, 11, 19):
                pygame.draw.rect(s, (120, 75, 45), (wx, 8, 4, 5))
        else:
            pygame.draw.rect(s, roof, (0, 6, TILE, 2))
            pygame.draw.rect(s, roof, (0, 14, TILE, 2))
            pygame.draw.rect(s, (120, 75, 45), (6, 8, 5, 5))
            pygame.draw.rect(s, (120, 75, 45), (18, 8, 5, 5))
        if var >= 8:
            gx = 4 + (var * 5) % 16
            gy = 2 + (var * 3) % 8
            for ly in range(gy, gy + 6, 3):
                for lx in range(gx, gx + 6, 4):
                    pygame.draw.rect(s, (50, 40, 30), (lx, ly, 3, 2))
    elif tile == T_FLOOR:
        v4 = var & 3
        floor_base = (195, 170, 135)
        pygame.draw.rect(s, floor_base, (0, 0, TILE, TILE))
        if v4 == 0:
            for ly in range(0, TILE, 8):
                for lx in range(0, TILE, 16):
                    c2 = (170, 145, 110) if (lx + ly) % 32 == 0 else (205, 180, 145)
                    pygame.draw.rect(s, c2, (lx, ly, 16, 8))
        elif v4 == 1:
            for ly in (6, 14, 22):
                pygame.draw.line(s, (170, 145, 110), (0, ly), (TILE, ly), 2)
            pygame.draw.rect(s, (160, 120, 80), (4, 4, 3, 3))
            pygame.draw.rect(s, (180, 140, 100), (20, 18, 3, 3))
        elif v4 == 2:
            for r in range(5):
                rx = (r * 6 + var * 3) % 24 + 4
                ry = (r * 8 + var * 5) % 24 + 4
                pygame.draw.rect(s, ((var * 20 + r * 30) % 30 + 160, (var * 10 + r * 20) % 25 + 140, (var * 5 + r * 15) % 20 + 115), (rx, ry, 5, 5))
        else:
            for ly in range(0, TILE, 8):
                for lx in range(0, TILE, 8):
                    c2 = (175, 150, 115) if (lx // 8 + ly // 8) % 2 == 0 else (210, 185, 150)
                    pygame.draw.rect(s, c2, (lx, ly, 8, 8))
        if var >= 8:
            for si in range(2):
                sx = (si * 15 + var * 7) % 24 + 4
                sy = (si * 19 + var * 11) % 24 + 4
                pygame.draw.rect(s, (140, 110, 80), (sx, sy, 5, 3))
    elif tile == T_DOOR:
        v4 = var & 3
        base = (170, 130, 70) if v4 == 0 else (130, 90, 50) if v4 == 1 else (150, 100, 60) if v4 == 2 else (100, 70, 50)
        pygame.draw.rect(s, (100, 70, 40), (2, 2, TILE - 4, TILE - 4))
        pygame.draw.rect(s, base, (4, 4, TILE - 8, TILE - 8))
        pygame.draw.rect(s, tuple(max(0, v - 30) for v in base), (14, 8, 4, 16))
        pygame.draw.circle(s, tuple(min(255, v + 30) for v in base), (22, 16), 2)
        if var >= 4 and var < 12:
            for ly in (8, 14, 20):
                pygame.draw.line(s, tuple(max(0, v - 20) for v in base), (8, ly), (12, ly))
        if var >= 12:
            pygame.draw.rect(s, (50, 40, 30), (4, 4, TILE - 8, TILE - 8))
            for dx, dy in ((0, 0), (4, 4), (8, 8), (12, 12), (16, 16)):
                pygame.draw.rect(s, (80, 60, 40), (4 + dx, 4 + dy, 4, 4))
        for di in range(2):
            dx = (di * 9 + var * 3) % 24 + 4
            dy = (di * 7 + var * 5) % 24 + 4
            pygame.draw.rect(s, tuple(min(255, v + 15) for v in base), (dx, dy, 2, 2))
    elif tile == T_TREE:
        v4 = var & 3
        if v4 == 0:
            pygame.draw.circle(s, (20, 60, 20), (16, 16), 10)
            pygame.draw.rect(s, (80, 50, 30), (14, 20, 4, 8))
            pygame.draw.circle(s, (30, 80, 30), (11, 9), 5)
            pygame.draw.circle(s, (25, 70, 25), (22, 12), 4)
            if var >= 8:
                pygame.draw.circle(s, (18, 50, 18), (14, 6), 3)
        elif v4 == 1:
            pygame.draw.polygon(s, (15, 55, 15), [(16, 2), (4, 20), (28, 20)])
            pygame.draw.polygon(s, (20, 65, 20), [(16, 6), (6, 22), (26, 22)])
            pygame.draw.rect(s, (80, 50, 30), (14, 20, 4, 8))
            if var >= 8:
                pygame.draw.polygon(s, (10, 45, 10), [(16, 1), (2, 18), (30, 18)])
        elif v4 == 2:
            for bx, by in ((14, 4), (18, 6), (12, 10), (22, 14)):
                pygame.draw.line(s, (80, 50, 30), (16, 22), (bx, by), 2)
            for bx, by in ((10, 6), (20, 4), (8, 14), (24, 8)):
                if var < 8:
                    pygame.draw.line(s, (80, 60, 40), (bx, by), (bx, by + 4), 1)
                else:
                    pygame.draw.line(s, (60, 40, 20), (bx, by), (bx, by + 4), 1)
        else:
            pygame.draw.circle(s, (30, 90, 30), (16, 14), 8)
            pygame.draw.rect(s, (80, 50, 30), (14, 20, 4, 8))
            for fx, fy in ((10, 10), (20, 8), (14, 6), (22, 14)):
                pygame.draw.circle(s, (40, 100, 40), (fx, fy), 3)
        if var >= 8:
            pygame.draw.rect(s, (80, 50, 30), (14, 20, 4, 8))
            for bx, by in ((14, 4), (18, 6), (12, 10), (22, 14), (6, 12), (24, 18)):
                pygame.draw.line(s, (60, 40, 25), (16, 20), (bx, by), 1)
    elif tile == T_WATER:
        v4 = var & 3
        for wi in range(3):
            wx = (wi * 13 + var * 7) % 28
            wy = (wi * 17 + var * 11) % 24 + 4
            pygame.draw.rect(s, (45 + wi * 15 + var * 3, 80 + wi * 5 - var * 5, 140 + wi * 5 - var * 8), (wx, wy + (var & 1), 7, 2))
        for sx in range(2, TILE, 10):
            cl = (min(255, 55 + var * 8), max(0, 95 - var * 6), max(0, 155 - var * 8))
            pygame.draw.line(s, cl, (sx, 8 + var % 3), (sx + 6, 8 + var % 3 + 1), 1)
    elif tile == T_RUBBLE:
        c2 = TILE_COLORS[T_RUBBLE]
        pygame.draw.rect(s, tuple(max(0, v - 20) for v in c2), (0, 0, TILE, TILE))
        for i in range(6):
            rx = (i * 13 + var * 7) % (TILE - 6)
            ry = (i * 17 + var * 11) % (TILE - 6)
            rw = 4 + (i * 3 + var) % 5
            rh = 3 + (i * 5 + var * 2) % 4
            rc = tuple(max(0, min(255, v + (i * 20 + var * 10) % 40 - 20)) for v in c2)
            pygame.draw.rect(s, rc, (rx, ry, rw, rh))
            pygame.draw.rect(s, tuple(max(0, v - 20) for v in rc), (rx, ry, rw, rh), 1)
        for ri in range(3):
            rx = (ri * 23 + var * 13) % 28
            ry = (ri * 29 + var * 17) % 28
            pygame.draw.rect(s, (60, 50, 35), (rx, ry, 3, 2))
    elif tile == T_DEBRIS:
        for i in range(5):
            dx = (i * 19 + var * 13) % (TILE - 4)
            dy = (i * 23 + var * 7) % (TILE - 4)
            ds = 2 + (i * var) % 3
            dc = ((var * 30 + i * 40) % 60 + 80, (var * 20 + i * 30) % 50 + 70, (var * 10 + i * 20) % 40 + 50)
            pygame.draw.rect(s, dc, (dx, dy, ds, ds))
        if var >= 8:
            for i in range(3):
                dx = (i * 11 + var * 5) % 26 + 2
                dy = (i * 7 + var * 3) % 26 + 2
                pygame.draw.circle(s, ((var * 50 + 100) % 100 + 80, 60, 60), (dx, dy), 1)
        for di in range(2):
            dx = (di * 17 + var * 11) % 28
            dy = (di * 13 + var * 5) % 28
            pygame.draw.rect(s, ((var * 40 + 70) % 60 + 70, (var * 30 + 60) % 50 + 60, (var * 20 + 50) % 40 + 45), (dx, dy, 2, 2))
    elif tile == T_CAR:
        c2 = TILE_COLORS[T_CAR]
        pygame.draw.rect(s, tuple(max(0, v - 30) for v in c2), (4, 8, TILE - 8, TILE - 12))
        pygame.draw.rect(s, (140, 80, 60), (6, 10, TILE - 12, TILE - 16))
        wx = 8 + (var * 3) % 8
        wy = 10 + (var * 5) % 4
        pygame.draw.rect(s, (180, 200, 220), (wx, wy, 4, 4))
        pygame.draw.rect(s, (180, 200, 220), (wx + 8, wy, 4, 4))
        pygame.draw.rect(s, (30, 30, 30), (wx + 4, wy + 4, 8, 4))
        pygame.draw.rect(s, (30, 30, 30), (10, TILE - 6, 5, 2))
        pygame.draw.rect(s, (30, 30, 30), (TILE - 15, TILE - 6, 5, 2))
        if var % 2 == 0:
            pygame.draw.rect(s, (40, 40, 40), (4, 13, TILE - 8, 3))
        if var >= 8:
            pygame.draw.rect(s, (200, 50, 50), (wx + 2, wy + 1, 2, 2))
            pygame.draw.rect(s, (200, 50, 50), (wx + 10, wy + 1, 2, 2))
    elif tile == T_BUSH:
        c2 = TILE_COLORS[T_BUSH]
        pygame.draw.rect(s, tuple(v - 10 for v in c2), (0, 0, TILE, TILE))
        cx, cy = 16, 18
        r = 8 + (var & 3)
        pygame.draw.circle(s, (40 + var * 3, 90 + var * 2, 30 + var * 2), (cx, cy), r)
        pygame.draw.circle(s, (50 + var * 4, 100 + var * 3, 35 + var * 2), (cx - 4, cy - 3), r - 2)
        pygame.draw.circle(s, (45 + var * 3, 95 + var * 2, 32 + var * 2), (cx + 5, cy - 2), r - 3)
        pygame.draw.circle(s, (35 + var * 2, 85 + var * 2, 28 + var * 2), (cx + 2, cy + 3), r - 3)
        if var >= 8:
            for bi in range(3):
                bx = (bi * 13 + var * 7) % (TILE - 4) + 2
                by = (bi * 11 + var * 5) % (TILE - 8) + 4
                pygame.draw.circle(s, ((var * 30 + bi * 40) % 40 + 30 + bi * 20, (var * 20 + bi * 30) % 30 + 80, (var * 10 + bi * 20) % 20 + 30), (bx, by), 3 + bi % 2)
        if var >= 4 and var < 12:
            for fi in range(2):
                fx = (fi * 17 + var * 11) % 26 + 3
                fy = (fi * 13 + var * 7) % 26 + 3
                if var % 2 == 0:
                    pygame.draw.circle(s, (220, 180, 60), (fx, fy), 1)
    return s

def get_tile(tile, x, y):
    key = (tile, (x * 13 + y * 37) & (TILE_VARIATIONS - 1))
    if key not in _tile_cache:
        _tile_cache[key] = _make_tile_surface(tile, key[1])
    return _tile_cache[key]

_zombie_label_cache = {}

def render_zombie(surf, z, cam):
    sx, sy = cam.world_to_screen(z.x, z.y)
    sx = int(sx)
    sy = int(sy)
    sprite = get_zombie_sprite(z.ztype, z.anim_frame)
    if z.hit_flash > 0 and z.hit_flash % 2 == 0:
        sprite.set_alpha(200)
        surf.blit(sprite, (sx, sy))
        sprite.set_alpha(255)
    else:
        surf.blit(sprite, (sx, sy))
    key = z.ztype
    if key not in _zombie_label_cache:
        _zombie_label_cache[key] = FONT_SM.render(z.label[:8], True, WHITE)
    t = _zombie_label_cache[key]
    surf.blit(t, (sx + 14 - t.get_width() // 2, sy - 8))

def render_night_overlay(surf, player, cam, factor, flashlight=False):
    global _night_overlay
    if factor <= 0:
        return
    if _night_overlay is None:
        _night_overlay = pygame.Surface((RENDER_W, RENDER_H), pygame.SRCALPHA)

    alpha = int(180 * factor)
    _night_overlay.fill((0, 0, 30, alpha))

    px, py = cam.world_to_screen(player.x, player.y)
    cx = int(px + TILE // 2)
    cy = int(py + TILE // 2)
    base_r = 280 if flashlight else 160
    r = int(base_r * (1 - factor * 0.2))

    key = (r, flashlight, RENDER_W, RENDER_H)
    if key not in _light_cache:
        size = r * 2 + 8
        lt = pygame.Surface((size, size), pygame.SRCALPHA)
        inner_r = r if flashlight else r
        for i in range(inner_r, 0, -1):
            a = int(alpha * (1.0 - i / inner_r) * 0.9)
            pygame.draw.circle(lt, (0, 0, 30, a), (r + 4, r + 4), i)
        _light_cache[key] = lt

    _night_overlay.blit(_light_cache[key], (cx - r - 4, cy - r - 4), special_flags=pygame.BLEND_RGBA_SUB)
    surf.blit(_night_overlay, (0, 0))

def render_zombie_hp(surf, z, cam):
    sx, sy = cam.world_to_screen(z.x, z.y)
    sx = int(sx)
    sy = int(sy - 8)
    fw = int((z.hp / z.max_hp) * 28)
    pygame.draw.rect(surf, (40, 0, 0), (sx, sy, 28, 4))
    c = RED if fw > 14 else ORANGE
    pygame.draw.rect(surf, c, (sx, sy, fw, 4))

def throw_molotov(player, zombies, hud):
    for z in zombies:
        if math.hypot(player.x - z.x, player.y - z.y) < 60:
            z.hp -= 60
            z.hit_flash = 15
            z.stun = 30
    hud.add_message("Lanzaste un Molotov!")

def get_time_label(text, color):
    key = (text, color)
    if key not in _time_labels:
        _time_labels[key] = FONT_MD.render(text, True, color)
    return _time_labels[key]

_rain_particles = []
_wind_particles = []
_rain_ambient_channel = None
_wind_ambient_channel = None
_rain_sound = None
_wind_sound = None

def update_weather_particles(world):
    global _rain_particles, _wind_particles, _rain_ambient_channel, _wind_ambient_channel, _rain_sound, _wind_sound

    if world.weather in (WEATHER_RAIN, WEATHER_STORM):
        target = int(RAIN_DROPS * world.rain_intensity)
        while len(_rain_particles) < target:
            _rain_particles.append([random.uniform(0, RENDER_W), random.uniform(-20, RENDER_H), random.uniform(2, 4)])
        while len(_rain_particles) > target:
            _rain_particles.pop()
        if _rain_sound is None:
            import sounds as _snd_mod
            if "rain" not in _snd_mod._cache:
                _snd_mod._build("rain")
            _rain_sound = _snd_mod._cache["rain"]
        if _rain_ambient_channel is None or not _rain_ambient_channel.get_busy():
            _rain_ambient_channel = _rain_sound.play(-1)

        if world.weather == WEATHER_STORM and random.random() < 0.001:
            play_sound("thunder")
    else:
        _rain_particles.clear()
        if _rain_ambient_channel:
            _rain_ambient_channel.stop()
            _rain_ambient_channel = None

    if world.weather in (WEATHER_WIND, WEATHER_STORM):
        target = int(WIND_PARTICLES * world.wind_strength)
        while len(_wind_particles) < target:
            _wind_particles.append([random.uniform(-20, RENDER_W), random.uniform(0, RENDER_H), random.uniform(0.5, 2.0), random.uniform(0.5, 1.5)])
        while len(_wind_particles) > target:
            _wind_particles.pop()
        if _wind_sound is None:
            import sounds as _snd_mod
            if "wind" not in _snd_mod._cache:
                _snd_mod._build("wind")
            _wind_sound = _snd_mod._cache["wind"]
        if _wind_ambient_channel is None or not _wind_ambient_channel.get_busy():
            _wind_ambient_channel = _wind_sound.play(-1)
    else:
        _wind_particles.clear()
        if _wind_ambient_channel:
            _wind_ambient_channel.stop()
            _wind_ambient_channel = None

def render_weather_particles(surf, world):
    if world.weather in (WEATHER_RAIN, WEATHER_STORM):
        for p in _rain_particles:
            p[0] += math.cos(world.wind_dir) * world.wind_strength * 1.5
            p[1] += p[2]
            px, py = int(p[0]), int(p[1])
            if px < 0: p[0] += RENDER_W
            if px >= RENDER_W: p[0] -= RENDER_W
            if py > RENDER_H:
                p[1] = -random.uniform(0, 10)
                p[0] = random.uniform(0, RENDER_W)
            else:
                alpha = 80 + int(80 * world.rain_intensity)
                pygame.draw.line(surf, (min(255, 160 + alpha // 2), min(255, 180 + alpha // 2), min(255, 220 + alpha // 3)), (px, py), (int(px - math.cos(world.wind_dir) * 3), int(py - 4)), 1)

    if world.weather in (WEATHER_WIND, WEATHER_STORM):
        for p in _wind_particles:
            p[0] += p[2] * 2
            p[1] += p[3] * 0.2
            px, py = int(p[0]), int(p[1])
            if px > RENDER_W + 20:
                p[0] = -random.uniform(0, 20)
                p[1] = random.uniform(0, RENDER_H)
            elif px < -20:
                p[0] = RENDER_W + random.uniform(0, 20)
                p[1] = random.uniform(0, RENDER_H)
            if 0 <= px < RENDER_W and 0 <= py < RENDER_H:
                alpha = 40 + int(40 * world.wind_strength)
                pygame.draw.line(surf, (min(255, 180 + alpha), min(255, 180 + alpha), min(255, 160 + alpha)), (px, py), (int(px - p[2] * 3), int(py - p[3])), 1)

def get_weather_text(weather):
    if weather == WEATHER_CLEAR:
        return "DESPEJADO", YELLOW
    elif weather == WEATHER_RAIN:
        return "LLUVIOSO", (150, 150, 200)
    elif weather == WEATHER_WIND:
        return "VENTOSO", (180, 180, 160)
    elif weather == WEATHER_STORM:
        return "TORMENTA", (200, 100, 100)
    return "", WHITE

def main():
    global _rain_ambient_channel, _wind_ambient_channel
    world = World()
    spawn = world.get_spawn_point()
    player = Player(spawn[0], spawn[1])
    camera = Camera()
    hud = HUD()
    screen_flash = 0
    game_over = False
    paused = False
    cricket_timer = 0

    game_surf = pygame.Surface((RENDER_W, RENDER_H))
    scale_x = SCREEN_W / RENDER_W
    scale_y = SCREEN_H / RENDER_H

    while True:
        dt = clock.tick(FPS)
        screen_flash = max(0, screen_flash - 1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if not game_over:
                    paused = not paused
                continue
            if paused:
                continue
            if event.type != pygame.KEYDOWN:
                continue
            if game_over:
                if event.key == pygame.K_r:
                    return main()
                continue

            if event.key == pygame.K_F5:
                if save_game(player, world):
                    hud.add_message("Partida guardada!")
                else:
                    hud.add_message("Error al guardar")
            elif event.key == pygame.K_F9:
                if load_game(player, world):
                    hud.add_message("Partida cargada!")
                else:
                    hud.add_message("No hay partida guardada")
            elif event.key == pygame.K_f:
                player.flashlight_on = not player.flashlight_on
                play_sound("flashlight")
                hud.add_message(f"Linterna {'ENCENDIDA' if player.flashlight_on else 'APAGADA'}")
            elif event.key == pygame.K_i:
                hud.toggle_inventory()
            elif event.key == pygame.K_c:
                hud.toggle_crafting()
            elif event.key == pygame.K_e:
                picked = False
                px, py = player.x, player.y
                for item in list(world.items):
                    if math.hypot(px - item.x, py - item.y) < PICKUP_RANGE / TILE:
                        if player.pickup(item.item_id, item.qty):
                            world.items.remove(item)
                            picked = True
                            hud.add_message(f"Recogiste: {ITEMS[item.item_id]['name']}")
                            play_sound("pickup")
                        else:
                            hud.add_message("Inventario lleno!")
                if not picked:
                    near = any(math.hypot(px - it.x, py - it.y) < PICKUP_RANGE / TILE for it in world.items)
                    if not near:
                        hud.add_message("No hay items cerca")
            elif event.key == pygame.K_r:
                if player.weapon == "pistol" and player.ammo > 0:
                    result = player.shoot(world.zombies)
                    if result:
                        _, dmg, z = result
                        hud.add_message(f"Disparaste! {dmg} dmg a {z.label}" if z else "Disparaste! Fallaste")
                elif "molotov" in player.inventory and player.inventory["molotov"] > 0:
                    player.inventory["molotov"] -= 1
                    if player.inventory["molotov"] <= 0:
                        del player.inventory["molotov"]
                    throw_molotov(player, world.zombies, hud)
            elif event.key == pygame.K_SPACE:
                result = player.attack(world.zombies)
                if result:
                    hit, _, dmg = result
                    if hit:
                        hud.add_message(f"Golpeaste! {dmg} dmg con {player.weapon}")
                    else:
                        hud.add_message(f"Atacaste con {player.weapon} (fallaste)")

            if hud.show_inventory:
                items = list(player.inventory.items())
                if pygame.K_1 <= event.key <= pygame.K_8:
                    idx = event.key - pygame.K_1
                    if idx < len(items):
                        item_id = items[idx][0]
                        res, _ = player.use_item(item_id)
                        if res == "used":
                            hud.add_message(f"Usaste: {ITEMS[item_id]['name']}")
                            play_sound("pickup")
                            if item_id in ("bandage", "medkit"):
                                player.heal_frames = 16
                                player.anim_state = "heal"
                                player.anim_frame = 0
                                player.anim_timer = 0
                                play_sound("heal")
                        elif res == "equip":
                            hud.add_message(f"Equipaste: {ITEMS[item_id]['name']}")
                            play_sound("pickup")
                        elif res == "flashlight":
                            hud.add_message(f"Linterna {'ENCENDIDA' if player.flashlight_on else 'APAGADA'}")
                        elif res == "throw":
                            hud.add_message("Selecciona Molotov, presiona R para lanzar")

            if hud.show_crafting:
                if pygame.K_1 <= event.key <= pygame.K_8:
                    idx = event.key - pygame.K_1
                    rkeys = list(RECIPES.keys())
                    if idx < len(rkeys):
                        rid = rkeys[idx]
                        recipe = RECIPES[rid]
                        can = all(player.inventory.get(m, 0) >= q for m, q in recipe["mats"].items())
                        if can:
                            for m, q in recipe["mats"].items():
                                player.inventory[m] -= q
                                if player.inventory[m] <= 0:
                                    del player.inventory[m]
                            player.inventory[recipe["result"]] = player.inventory.get(recipe["result"], 0) + recipe["qty"]
                            hud.add_message(f"Crafteaste: {ITEMS[recipe['result']]['name']} x{recipe['qty']}")
                        else:
                            hud.add_message("No tienes suficientes materiales")

        if game_over:
            game_surf.fill(BLACK)
            for i, (t, c, y) in enumerate([
                (f"HAS MUERTO", RED, -60),
                (f"Sobreviviste {player.days_survived} días | Mataste {player.kills} zombies", WHITE, 0),
                ("Presiona R para reiniciar | ESC para salir", YELLOW, 40),
            ]):
                txt = FONT_TITLE.render(t, True, c) if i == 0 else FONT_MD.render(t, True, c)
                game_surf.blit(txt, (RENDER_W // 2 - txt.get_width() // 2, RENDER_H // 2 + y))
            pygame.transform.smoothscale(game_surf, (SCREEN_W, SCREEN_H), screen)
            pygame.display.flip()
            continue

        dx, dy = 0, 0
        if not paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = 1
            if dx and dy:
                dx *= 0.7071
                dy *= 0.7071

            running = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and player.stamina > 5
            player.move(dx, dy, world, running)
            world.update(player, dt)
            player.update(dt, moving=(dx != 0 or dy != 0))

            cricket_timer -= 1
            if cricket_timer <= 0 and world.night_factor() > 0.3:
                play_sound("cricket")
                cricket_timer = random.randint(120, 300)

            for z in world.zombies:
                if z.can_attack(player) and player.take_damage(z.dmg):
                    z.attack_cooldown = ZOMBIE_ATTACK_COOLDOWN
                    screen_flash = 6
                    hud.add_message(f"Recibiste {z.dmg} de daño de {z.label}!")
                    if player.hp <= 0:
                        game_over = True
                        break

            if player.hp <= 0:
                game_over = True

            removed = []
            for item in world.items:
                d = math.hypot(player.x - item.x, player.y - item.y)
                if d < 0.5:
                    if player.can_pickup():
                        player.pickup(item.item_id, item.qty)
                        hud.add_message(f"Recogiste: {ITEMS[item.item_id]['name']}")
                        play_sound("pickup")
                        removed.append(item)
                    elif d < 0.3:
                        hud.add_message("Inventario lleno!")
            for item in removed:
                world.items.remove(item)

            camera.follow(player)

            update_weather_particles(world)

        game_surf.fill(DARK)
        vx, vy, vx2, vy2 = camera.get_visible_range()
        cam_ox = camera.x
        cam_oy = camera.y
        for y in range(vy, vy2):
            sy = int(y * TILE - cam_oy)
            row_t = world.tiles[y]
            row_v = world.visible[y]
            row_e = world.explored[y]
            for x in range(vx, vx2):
                if not row_e[x]:
                    continue
                sx = int(x * TILE - cam_ox)
                if not row_v[x]:
                    tid = row_t[x]
                    key = (tid, (x * 13 + y * 37) & (TILE_VARIATIONS - 1))
                    if key not in _fog_tile_cache:
                        bc = TILE_COLORS[tid]
                        fs = pygame.Surface((TILE, TILE))
                        fs.fill(tuple(v // 3 for v in bc))
                        _fog_tile_cache[key] = fs
                    game_surf.blit(_fog_tile_cache[key], (sx, sy))
                else:
                    game_surf.blit(get_tile(row_t[x], x, y), (sx, sy))

        render_weather_particles(game_surf, world)

        for item in world.items:
            ix, iy = int(item.x), int(item.y)
            if 0 <= iy < MAP_H and 0 <= ix < MAP_W and world.visible[iy][ix]:
                sx, sy = camera.world_to_screen(item.x - 0.3, item.y - 0.3)
                sx, sy = int(sx), int(sy)
                bob = int(math.sin(item.bob) * 2)
                item_surf = get_item_sprite(item.item_id)
                game_surf.blit(item_surf, (sx, sy + bob))

        for z in world.zombies:
            if 0 <= int(z.y) < MAP_H and 0 <= int(z.x) < MAP_W and world.visible[int(z.y)][int(z.x)]:
                render_zombie(game_surf, z, camera)
                render_zombie_hp(game_surf, z, camera)

        px, py = camera.world_to_screen(player.x, player.y)
        px, py = int(px), int(py)
        sprite = get_player_sprite(player.anim_state, player.anim_frame, player.weapon, player.armor.get("head"), player.armor.get("body"), player.armor.get("legs"))
        if player.iframes > 0 and player.iframes % 4 < 2:
            sprite.set_alpha(160)
            game_surf.blit(sprite, (px, py))
            sprite.set_alpha(255)
        elif player.hurt_flash > 0:
            sprite.set_alpha(200)
            game_surf.blit(sprite, (px, py))
            sprite.set_alpha(255)
        else:
            game_surf.blit(sprite, (px, py))

        if (dx or dy) or player.anim_state == "attack":
            if dx or dy:
                cos_a, sin_a = dx, dy
                norm = math.hypot(dx, dy)
                if norm > 0:
                    cos_a, sin_a = dx / norm, dy / norm
            else:
                cos_a, sin_a = 1.0, 0.0
            alen = 18 if player.anim_state == "attack" else 12
            cx, cy = px + 14, py + 14
            pygame.draw.line(game_surf, (150, 200, 255), (cx, cy), (cx + cos_a * alen, cy + sin_a * alen), 3)

        nf = world.night_factor()
        if nf > 0:
            c = (200, 100, 50) if nf < 0.5 else (100, 50, 150)
            tl = get_time_label("NOCHE" if nf > 0.5 else "ATARDECER", c)
        else:
            tl = get_time_label("DIA", (200, 200, 100))
        game_surf.blit(tl, (RENDER_W // 2 - tl.get_width() // 2, 10))

        wt, wc = get_weather_text(world.weather)
        wt_label = get_time_label(wt, wc)
        game_surf.blit(wt_label, (RENDER_W // 2 - wt_label.get_width() // 2, 24))

        render_night_overlay(game_surf, player, camera, nf, player.flashlight_on)

        if screen_flash > 0:
            global _flash_surf
            if _flash_surf is None or _flash_surf.get_size() != (RENDER_W, RENDER_H):
                _flash_surf = pygame.Surface((RENDER_W, RENDER_H), pygame.SRCALPHA)
            _flash_surf.fill((255, 30, 30, 40 * screen_flash))
            game_surf.blit(_flash_surf, (0, 0))

        if paused:
            global _pause_overlay
            if _pause_overlay is None or _pause_overlay.get_size() != (RENDER_W, RENDER_H):
                _pause_overlay = pygame.Surface((RENDER_W, RENDER_H), pygame.SRCALPHA)
                _pause_overlay.fill((0, 0, 0, 160))
            game_surf.blit(_pause_overlay, (0, 0))
            t = FONT_TITLE.render("PAUSA", True, WHITE)
            game_surf.blit(t, (RENDER_W // 2 - t.get_width() // 2, RENDER_H // 2 - 60))
            t2 = FONT_MD.render("ESC para reanudar", True, YELLOW)
            game_surf.blit(t2, (RENDER_W // 2 - t2.get_width() // 2, RENDER_H // 2))
            t3 = FONT_MD.render("Q para salir", True, RED)
            game_surf.blit(t3, (RENDER_W // 2 - t3.get_width() // 2, RENDER_H // 2 + 30))

            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                pygame.quit()
                sys.exit()

        hud.render(game_surf, player, world)
        pygame.transform.smoothscale(game_surf, (SCREEN_W, SCREEN_H), screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
