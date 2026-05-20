import random
import math
from config import *
from entities import Zombie, ItemDrop


class World:
    def __init__(self, load=False):
        self.tiles = [[T_GRASS for _ in range(MAP_W)] for _ in range(MAP_H)]
        self.visible = [[False for _ in range(MAP_W)] for _ in range(MAP_H)]
        self.explored = [[False for _ in range(MAP_W)] for _ in range(MAP_H)]
        self.zombies = []
        self.items = []
        self.time = 0.0
        self.spawn_timer = 0
        self.game_day = 1
        self._last_vpos = (-1, -1)
        if not load:
            self.generate()

    def generate(self):
        for y in range(MAP_H):
            for x in range(MAP_W):
                self.tiles[y][x] = T_GRASS

        for y in range(MAP_H):
            for x in range(MAP_W):
                if y % BLOCK in (0, 1) or x % BLOCK in (0, 1):
                    self.tiles[y][x] = T_ROAD

        for by in range(BLOCK, MAP_H, BLOCK):
            for bx in range(BLOCK, MAP_W, BLOCK):
                if bx + BLOCK >= MAP_W or by + BLOCK >= MAP_H:
                    continue
                r = random.random()
                if r < 0.55:
                    self._make_building(bx + 1, by + 1, BLOCK - 2, BLOCK - 2)
                elif r < 0.70:
                    self._make_park(bx + 1, by + 1, BLOCK - 2, BLOCK - 2)

        for y in range(MAP_H):
            row = self.tiles[y]
            for x in range(MAP_W):
                if row[x] == T_GRASS and random.random() < 0.03:
                    row[x] = T_TREE

        self._place_start_items()

    def _make_building(self, sx, sy, w, h):
        if w < 4 or h < 4:
            return
        for y in range(sy, sy + h):
            for x in range(sx, sx + w):
                if y >= MAP_H or x >= MAP_W:
                    continue
                if y in (sy, sy + h - 1) or x in (sx, sx + w - 1):
                    self.tiles[y][x] = T_WALL
                else:
                    self.tiles[y][x] = T_FLOOR

        dx, dy = sx + w // 2, sy + h - 1
        if dy < MAP_H and dx < MAP_W:
            self.tiles[dy][dx] = T_DOOR

        if w >= 6 and h >= 6:
            for ry in range(sy + 2, sy + h - 2):
                for rx in range(sx + 2, sx + w - 2):
                    if random.random() < 0.12:
                        self.tiles[ry][rx] = T_GRASS

        for ry in range(sy + 1, sy + h - 1):
            for rx in range(sx + 1, sx + w - 1):
                r2 = random.random()
                if r2 < 0.08:
                    self.items.append(ItemDrop(rx, ry, random.choice(["food", "water", "cloth", "wood", "metal", "alcohol"])))
                elif r2 < 0.11:
                    self.items.append(ItemDrop(rx, ry, random.choice(["bat", "medkit", "ammo", "book"])))

    def _make_park(self, sx, sy, w, h):
        for y in range(sy, sy + h):
            row = self.tiles[y]
            for x in range(sx, sx + w):
                if y < MAP_H and x < MAP_W:
                    row[x] = T_TREE if random.random() < 0.15 else T_GRASS

    def _place_start_items(self):
        cx, cy = MAP_W // 2, MAP_H // 2
        for iid, qty in (("food", 3), ("water", 3), ("cloth", 2), ("wood", 2)):
            self.items.append(ItemDrop(cx + random.uniform(-2, 2), cy + random.uniform(-2, 2), iid, qty))

    def is_walkable(self, x, y):
        return 0 <= x < MAP_W and 0 <= y < MAP_H and self.tiles[y][x] not in (T_WALL, T_TREE)

    def get_tile(self, x, y):
        if 0 <= x < MAP_W and 0 <= y < MAP_H:
            return self.tiles[y][x]
        return T_WALL

    def update_player_visibility(self, px, py, radius=6):
        r2 = radius * radius
        for y in range(MAP_H):
            vy = (y - py) ** 2
            row_v = self.visible[y]
            row_e = self.explored[y]
            for x in range(MAP_W):
                v = vy + (x - px) ** 2 < r2
                row_v[x] = v
                if v:
                    row_e[x] = True

    def update(self, player, dt):
        self.time += dt / 60.0
        if self.time >= CYCLE_LENGTH:
            self.time -= CYCLE_LENGTH
            self.game_day += 1
            player.days_survived = self.game_day

        vx, vy = int(player.x), int(player.y)
        if (vx, vy) != self._last_vpos:
            self.update_player_visibility(vx, vy)
            self._last_vpos = (vx, vy)

        night = self.is_night()
        base = 150 if night else 360
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            day_scale = min(self.game_day, 30)
            self.spawn_timer = max(30, base - day_scale * 8)
            max_zombies = 15 + day_scale * 4
            if len(self.zombies) < max_zombies:
                self._spawn_zombie(player)

        zs = self.zombies
        for i in range(len(zs) - 1, -1, -1):
            z = zs[i]
            z.update(player, self, dt)
            if z.hp <= 0:
                self._on_zombie_kill(z, player)
                del zs[i]

        for item in self.items:
            item.update()

    def _spawn_zombie(self, player):
        a = random.uniform(0, math.pi * 2)
        dist = random.uniform(ZOMBIE_SPAWN_MIN, ZOMBIE_SPAWN_MAX)
        sx = max(1, min(MAP_W - 2, player.x + math.cos(a) * dist))
        sy = max(1, min(MAP_H - 2, player.y + math.sin(a) * dist))
        if not self.is_walkable(int(sx), int(sy)):
            return
        r = random.random()
        if r < 0.55:
            zt = "common"
        elif r < 0.80:
            zt = "runner"
        elif r < 0.93:
            zt = "executive"
        else:
            zt = "tank"
        self.zombies.append(Zombie(sx, sy, zt))

    def _on_zombie_kill(self, z, player):
        player.kills += 1
        loot = ["cloth", "cloth", "wood", "food", "food", "alcohol", "ammo"]
        if random.random() < 0.50:
            self.items.append(ItemDrop(z.x, z.y, random.choice(loot)))
        if random.random() < 0.15:
            self.items.append(ItemDrop(z.x, z.y, random.choice(["ammo", "medkit", "alcohol", "food"])))
        if z.ztype == "tank" and random.random() < 0.40:
            self.items.append(ItemDrop(z.x, z.y, random.choice(["metal", "bat", "ammo"])))
        if random.random() < 0.35:
            aid = random.choice(list(ARMOR_TYPES.keys()))
            self.items.append(ItemDrop(z.x, z.y, aid))
        if z.ztype == "tank" and random.random() < 0.45:
            aid = random.choice(list(ARMOR_TYPES.keys()))
            self.items.append(ItemDrop(z.x, z.y, aid))
        if z.ztype == "executive" and random.random() < 0.25:
            aid = random.choice(list(ARMOR_TYPES.keys()))
            self.items.append(ItemDrop(z.x, z.y, aid))

    def is_night(self):
        return self.time > DAY_LENGTH

    def night_factor(self):
        if self.time < DAY_LENGTH:
            return 0.0
        return min(1.0, (self.time - DAY_LENGTH) / NIGHT_LENGTH)

    def get_spawn_point(self):
        for _ in range(50):
            x = random.randint(2, MAP_W - 3)
            y = random.randint(2, MAP_H - 3)
            if self.is_walkable(x, y):
                return x, y
        return MAP_W // 2, MAP_H // 2
