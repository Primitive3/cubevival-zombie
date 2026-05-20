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
        grass_rects = [(6, 6, 4, 4), (18, 4, 3, 3), (4, 18, 5, 3), (22, 22, 4, 4)]
        pygame.draw.rect(s, (50, 105, 40), grass_rects[v4])
        if var < 8:
            for fx, fy in ((4, 12), (20, 6), (26, 22), (10, 26), (12, 4)):
                if var % 3 == fx % 3:
                    pygame.draw.circle(s, ((fx * 37 + fy * 13) % 60 + 180, (fx * 7 + fy * 17) % 40 + 140, (fx * 11 + fy * 5) % 30 + 30), (fx, fy), 1)
        else:
            for sx, sy in ((8, 22), (24, 10), (4, 18), (16, 6), (28, 16)):
                pygame.draw.rect(s, ((var * 20 + sx) % 40 + 80, (var * 15 + sy) % 40 + 70, (var * 10 + sx + sy) % 30 + 40), (sx, sy, 2, 2))
    elif tile == T_ROAD:
        v4 = var & 3
        if v4 == 0:
            for cx in (6, 16, 26):
                pygame.draw.rect(s, (90, 90, 90), (cx, 0, 2, TILE))
        elif v4 == 1:
            pygame.draw.rect(s, (100, 100, 80), (13, 15, 6, 2))
            for cx in (4, 24):
                pygame.draw.rect(s, (60, 60, 60), (cx, 8, 3, 3))
                pygame.draw.rect(s, (60, 60, 60), (cx, 20, 3, 3))
        elif v4 == 2:
            for cx in (2, 10, 18, 26):
                pygame.draw.line(s, (50, 50, 50), (cx, 0), (cx, TILE))
            for cy in (6, 12, 18, 24):
                pygame.draw.line(s, (70, 70, 70), (0, cy), (TILE, cy))
        else:
            pygame.draw.rect(s, (100, 60, 40), (8, 10, 16, 12))
            for dx, dy in ((4, 4), (20, 18), (6, 24), (24, 6)):
                pygame.draw.rect(s, (60, 50, 40), (dx, dy, 4, 2))
        if var >= 8:
            for sx, sy in ((2 + var % 4, (var * 3) % 28), (20 + var % 3, (var * 7) % 24)):
                pygame.draw.rect(s, (130, 40, 40), (sx, sy, 3, 2))
    elif tile == T_WALL:
        v4 = var & 3
        if v4 == 0:
            for ly in (7, 15, 23):
                pygame.draw.rect(s, (110, 90, 70), (0, ly, TILE, 2))
            pygame.draw.rect(s, (90, 70, 50), (15, 0, 2, TILE))
            if var >= 8:
                for wx in (2, 10, 20, 28):
                    pygame.draw.rect(s, (130, 110, 80), (wx, 12, 4, 2))
        elif v4 == 1:
            pygame.draw.rect(s, (130, 120, 110), (0, 0, TILE, TILE))
            pygame.draw.rect(s, (140, 130, 120), (0, 0, TILE, TILE), 1)
            for ly in (8, 16, 24):
                pygame.draw.line(s, (120, 110, 100), (0, ly), (TILE, ly))
            for lx in (8, 16, 24):
                pygame.draw.line(s, (120, 110, 100), (lx, 0), (lx, TILE))
        elif v4 == 2:
            for ly in (7, 15, 23):
                pygame.draw.rect(s, (110, 90, 70), (0, ly, TILE, 2))
            pygame.draw.rect(s, (90, 70, 50), (15, 0, 2, TILE))
            for wx in (4, 20):
                pygame.draw.rect(s, (80, 60, 40), (wx, 5, 6, 8))
        else:
            for ly in (7, 15, 23):
                pygame.draw.rect(s, (110, 90, 70), (0, ly, TILE, 2))
            pygame.draw.rect(s, (90, 70, 50), (15, 0, 2, TILE))
            pygame.draw.rect(s, (60, 40, 30), (8, 10, 16, 12))
        if var >= 8:
            gx = 4 + (var * 5) % 20
            gy = 2 + (var * 3) % 8
            for ly in range(gy, gy + 8, 3):
                for lx in range(gx, gx + 8, 4):
                    pygame.draw.rect(s, (180, 50, 50), (lx, ly, 2, 2))
    elif tile == T_FLOOR:
        v4 = var & 3
        if v4 == 0:
            pygame.draw.rect(s, (170, 150, 120), (4, 4, 3, 3))
            pygame.draw.rect(s, (190, 170, 140), (20, 18, 3, 3))
        elif v4 == 1:
            for ly in range(0, TILE, 8):
                for lx in range(0, TILE, 16):
                    c2 = (160, 140, 110) if (lx + ly) % 32 == 0 else (190, 170, 140)
                    pygame.draw.rect(s, c2, (lx, ly, 16, 8))
        elif v4 == 2:
            for ly in range(0, TILE, 6):
                pygame.draw.line(s, (160, 140, 110), (0, ly), (TILE, ly))
                pygame.draw.line(s, (200, 180, 150), (0, ly + 3), (TILE, ly + 3))
            pygame.draw.rect(s, (120, 80, 50), (2, 6, 28, 20))
            pygame.draw.rect(s, (140, 100, 70), (4, 8, 24, 16), 1)
        else:
            for r in range(4):
                rx = (r * 7 + var * 3) % 28
                ry = (r * 11 + var * 5) % 28
                pygame.draw.rect(s, ((var * 20 + r * 30) % 40 + 60, (var * 10 + r * 20) % 30 + 40, 30), (rx, ry, 4, 4))
        if var >= 8:
            for si in range(3):
                sx = (si * 13 + var * 7) % 28
                sy = (si * 17 + var * 11) % 24
                pygame.draw.rect(s, (80, 70, 60), (sx, sy, 4, 2))
    elif tile == T_DOOR:
        v4 = var & 3
        base = (160, 130, 80) if v4 == 0 else (120, 90, 60) if v4 == 1 else (140, 100, 70) if v4 == 2 else (100, 70, 50)
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
    elif tile == T_TREE:
        v4 = var & 3
        if v4 == 0:
            pygame.draw.circle(s, (20, 60, 20), (16, 16), 10)
            pygame.draw.rect(s, (80, 50, 30), (14, 20, 4, 8))
            pygame.draw.circle(s, (30, 80, 30), (11, 9), 5)
            pygame.draw.circle(s, (25, 70, 25), (22, 12), 4)
        elif v4 == 1:
            pygame.draw.polygon(s, (15, 55, 15), [(16, 2), (4, 20), (28, 20)])
            pygame.draw.polygon(s, (20, 65, 20), [(16, 6), (6, 22), (26, 22)])
            pygame.draw.rect(s, (80, 50, 30), (14, 20, 4, 8))
        elif v4 == 2:
            for bx, by in ((14, 4), (18, 6), (12, 10), (22, 14)):
                pygame.draw.line(s, (80, 50, 30), (16, 22), (bx, by), 2)
            for bx, by in ((10, 6), (20, 4), (8, 14), (24, 8)):
                if var < 8:
                    pygame.draw.line(s, (80, 60, 40), (bx, by), (bx, by + 4), 1)
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
        for wx, wy in ((6, 3), (18, 11), (10, 22), (24, 17)):
            pygame.draw.rect(s, (50 + v4 * 10, 90 - v4 * 15, 150 - v4 * 20), (wx, wy + (var & 1) * 2, 6, 3))
        if var & 4:
            for sx in range(0, TILE, 8):
                cl = (min(255, 60 + var * 5), max(0, 100 - var * 8), max(0, 160 - var * 10))
                pygame.draw.line(s, cl, (sx, var % 4 * 2), (sx + 4, var % 4 * 2 + 2), 1)
        if var >= 8:
            for ss in range(3):
                sx = (ss * 11 + var * 7) % 28
                sy = (ss * 13 + var * 3) % 24 + 2
                pygame.draw.rect(s, ((var * 30 + 100) % 100 + 80, (var * 20 + 80) % 80 + 100, 100), (sx, sy, 4, 2))
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
        _night_overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

    alpha = int(180 * factor)
    _night_overlay.fill((0, 0, 30, alpha))

    px, py = cam.world_to_screen(player.x, player.y)
    cx = int(px + TILE // 2)
    cy = int(py + TILE // 2)
    base_r = 280 if flashlight else 160
    r = int(base_r * (1 - factor * 0.2))

    key = (r, flashlight)
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

def main():
    world = World()
    spawn = world.get_spawn_point()
    player = Player(spawn[0], spawn[1])
    camera = Camera()
    hud = HUD()
    screen_flash = 0
    game_over = False
    paused = False
    cricket_timer = 0

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
            screen.fill(BLACK)
            for i, (t, c, y) in enumerate([
                (f"HAS MUERTO", RED, -60),
                (f"Sobreviviste {player.days_survived} días | Mataste {player.kills} zombies", WHITE, 0),
                ("Presiona R para reiniciar | ESC para salir", YELLOW, 40),
            ]):
                txt = FONT_TITLE.render(t, True, c) if i == 0 else FONT_MD.render(t, True, c)
                screen.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, SCREEN_H // 2 + y))
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

        screen.fill(DARK)
        vx, vy, vx2, vy2 = camera.get_visible_range()
        cam_ox = camera.x
        cam_oy = camera.y
        tile_cache = _tile_cache
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
                    screen.blit(_fog_tile_cache[key], (sx, sy))
                else:
                    screen.blit(get_tile(row_t[x], x, y), (sx, sy))

        for item in world.items:
            ix, iy = int(item.x), int(item.y)
            if 0 <= iy < MAP_H and 0 <= ix < MAP_W and world.visible[iy][ix]:
                sx, sy = camera.world_to_screen(item.x - 0.3, item.y - 0.3)
                sx, sy = int(sx), int(sy)
                bob = int(math.sin(item.bob) * 2)
                item_surf = get_item_sprite(item.item_id)
                screen.blit(item_surf, (sx, sy + bob))

        for z in world.zombies:
            if 0 <= int(z.y) < MAP_H and 0 <= int(z.x) < MAP_W and world.visible[int(z.y)][int(z.x)]:
                render_zombie(screen, z, camera)
                render_zombie_hp(screen, z, camera)

        px, py = camera.world_to_screen(player.x, player.y)
        px, py = int(px), int(py)
        sprite = get_player_sprite(player.anim_state, player.anim_frame, player.weapon, player.armor.get("head"), player.armor.get("body"), player.armor.get("legs"))
        if player.iframes > 0 and player.iframes % 4 < 2:
            sprite.set_alpha(160)
            screen.blit(sprite, (px, py))
            sprite.set_alpha(255)
        elif player.hurt_flash > 0:
            sprite.set_alpha(200)
            screen.blit(sprite, (px, py))
            sprite.set_alpha(255)
        else:
            screen.blit(sprite, (px, py))

        if (dx or dy) or player.anim_state == "attack":
            if dx or dy:
                cos_a, sin_a = dx, dy
                alen = 1.0
                norm = math.hypot(dx, dy)
                if norm > 0:
                    cos_a, sin_a = dx / norm, dy / norm
            else:
                cos_a, sin_a = 1.0, 0.0
            alen = 18 if player.anim_state == "attack" else 12
            cx, cy = px + 14, py + 14
            pygame.draw.line(screen, (150, 200, 255), (cx, cy), (cx + cos_a * alen, cy + sin_a * alen), 3)

        nf = world.night_factor()
        if nf > 0:
            c = (200, 100, 50) if nf < 0.5 else (100, 50, 150)
            tl = get_time_label("NOCHE" if nf > 0.5 else "ATARDECER", c)
        else:
            tl = get_time_label("DIA", (200, 200, 100))
        screen.blit(tl, (SCREEN_W // 2 - tl.get_width() // 2, 10))

        render_night_overlay(screen, player, camera, nf, player.flashlight_on)

        if screen_flash > 0:
            global _flash_surf
            if _flash_surf is None:
                _flash_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            _flash_surf.fill((255, 30, 30, 40 * screen_flash))
            screen.blit(_flash_surf, (0, 0))

        if paused:
            global _pause_overlay
            if _pause_overlay is None:
                _pause_overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                _pause_overlay.fill((0, 0, 0, 160))
            screen.blit(_pause_overlay, (0, 0))
            t = FONT_TITLE.render("PAUSA", True, WHITE)
            screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, SCREEN_H // 2 - 60))
            t2 = FONT_MD.render("ESC para reanudar", True, YELLOW)
            screen.blit(t2, (SCREEN_W // 2 - t2.get_width() // 2, SCREEN_H // 2))
            t3 = FONT_MD.render("Q para salir", True, RED)
            screen.blit(t3, (SCREEN_W // 2 - t3.get_width() // 2, SCREEN_H // 2 + 30))

            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                pygame.quit()
                sys.exit()

        hud.render(screen, player, world)
        pygame.display.flip()


if __name__ == "__main__":
    main()
