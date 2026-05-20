import pygame
from config import *


def draw_bar(surf, x, y, w, h, val, max_val, fg, bg, label=""):
    pygame.draw.rect(surf, bg, (x, y, w, h))
    if max_val > 0:
        fw = int((val / max_val) * w)
        pygame.draw.rect(surf, fg, (x, y, fw, h))
    pygame.draw.rect(surf, WHITE, (x, y, w, h), 1)
    if label:
        t = FONT_SM.render(label, True, WHITE)
        surf.blit(t, (x + 4, y + 2))


class HUD:
    def __init__(self):
        self.show_inventory = False
        self.show_crafting = False
        self.messages = []
        self._mm_cache = None
        self._mm_dirty = True
        self._last_explored_count = 0
        self._ctrl_labels = None
        self._panel_bg = None

    def add_message(self, text):
        self.messages.append(text)
        if len(self.messages) > 5:
            self.messages.pop(0)

    def toggle_inventory(self):
        self.show_inventory = not self.show_inventory
        self.show_crafting = False

    def toggle_crafting(self):
        self.show_crafting = not self.show_crafting
        self.show_inventory = False

    def render(self, surf, player, world):
        self._draw_stats(surf, player, world)
        self._draw_minimap(surf, player, world)
        if self.show_inventory:
            self._draw_inventory(surf, player)
        elif self.show_crafting:
            self._draw_crafting(surf, player)
        self._draw_messages(surf)
        self._draw_controls(surf)

    def _draw_stats(self, surf, player, world):
        y = 8
        bars = [
            (player.hp, player.max_hp, RED, (60, 20, 20)),
            (player.hunger, 100, ORANGE, (50, 30, 10)),
            (player.thirst, 100, BLUE, (10, 20, 60)),
            (player.stamina, 100, GREEN, (10, 40, 10)),
        ]
        labels = [f"HP {int(player.hp)}", f"Hambre {int(player.hunger)}",
                  f"Sed {int(player.thirst)}", f"Stamina {int(player.stamina)}"]
        for (val, mx, fg, bg), lbl in zip(bars, labels):
            w = int((val / mx) * 160) if mx > 0 else 0
            pygame.draw.rect(surf, bg, (10, y, 160, 16))
            if w:
                pygame.draw.rect(surf, fg, (10, y, w, 16))
            pygame.draw.rect(surf, WHITE, (10, y, 160, 16), 1)
            t = FONT_SM.render(lbl, True, WHITE)
            surf.blit(t, (14, y + 2))
            y += 22

        t = FONT_MD.render(f"Dia {world.game_day} | Kills: {player.kills}", True, WHITE)
        surf.blit(t, (10, y))
        wep_name = {"rama": "Rama", "fists": "Puños", "bat": "Bate", "spear": "Lanza", "pistol": "Pistola"}
        wep = f"Arma: {wep_name.get(player.weapon, player.weapon.upper())}"
        if player.weapon == "pistol":
            wep += f" [{player.ammo} bal]"
        t2 = FONT_SM.render(wep, True, YELLOW)
        surf.blit(t2, (10, y + 22))
        y += 44

        defense = player.get_defense()
        armor_texts = []
        for slot in ("head", "body", "legs"):
            aid = player.armor[slot]
            if aid and aid in ARMOR_TYPES:
                ainfo = ARMOR_TYPES[aid]
                armor_texts.append(f"{ainfo['name']} ({ainfo['defense']})")
            else:
                armor_texts.append(f"-")
        def_text = f"Armadura: {defense} DEF"
        surf.blit(FONT_SM.render(def_text, True, (180, 180, 200)), (10, y))
        y += 14
        slot_labels = ["Casco", " torso", "Piernas"]
        for sl, at in zip(slot_labels, armor_texts):
            surf.blit(FONT_SM.render(f" {sl}: {at}", True, (150, 150, 170)), (10, y))
            y += 12

        if hasattr(player, 'flashlight_on'):
            fl_text = "Linterna: ON" if player.flashlight_on else "Linterna: OFF"
            fl_color = YELLOW if player.flashlight_on else GRAY
            surf.blit(FONT_SM.render(fl_text, True, fl_color), (10, y))

    def _draw_minimap(self, surf, player, world):
        mm_size = 90
        mm_x = RENDER_W - mm_size - 8
        mm_y = 8
        scale = mm_size / max(MAP_W, MAP_H)

        explored_count = sum(sum(row) for row in world.explored)
        if explored_count != self._last_explored_count:
            self._mm_dirty = True
            self._last_explored_count = explored_count

        if self._mm_dirty or self._mm_cache is None:
            self._mm_cache = pygame.Surface((mm_size, mm_size), pygame.SRCALPHA)
            self._mm_cache.fill((0, 0, 0, 160))
            px_data = self._mm_cache
            half_w = MAP_W / 2
            half_h = MAP_H / 2
            for y in range(MAP_H):
                row_e = world.explored[y]
                row_t = world.tiles[y]
                py = int((y - half_h) * scale + mm_size / 2)
                if not (0 <= py < mm_size):
                    continue
                for x in range(MAP_W):
                    if not row_e[x]:
                        continue
                    px = int((x - half_w) * scale + mm_size / 2)
                    if 0 <= px < mm_size:
                        c = TILE_COLORS.get(row_t[x], (0, 0, 0))
                        if not world.visible[y][x]:
                            c = tuple(v // 3 for v in c)
                        px_data.set_at((px, py), c)
            self._mm_dirty = False

        surf.blit(self._mm_cache, (mm_x, mm_y))
        cx = int((player.x - MAP_W / 2) * scale + mm_size / 2)
        cy = int((player.y - MAP_H / 2) * scale + mm_size / 2)
        pygame.draw.circle(surf, BLUE, (mm_x + cx, mm_y + cy), 3)
        for z in world.zombies:
            zx = int((z.x - MAP_W / 2) * scale + mm_size / 2)
            zy = int((z.y - MAP_H / 2) * scale + mm_size / 2)
            if 0 <= zx < mm_size and 0 <= zy < mm_size:
                surf.set_at((mm_x + zx, mm_y + zy), RED)
        t = FONT_SM.render("MAPA", True, WHITE)
        surf.blit(t, (mm_x + mm_size // 2 - t.get_width() // 2, mm_y + mm_size + 2))

    def _draw_inventory(self, surf, player):
        if self._panel_bg is None:
            ov = pygame.Surface((RENDER_W, RENDER_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 180))
            self._panel_bg = ov
        surf.blit(self._panel_bg, (0, 0))
        px, py, pw, ph = RENDER_W // 2 - 150, RENDER_H // 2 - 140, 300, 280
        pygame.draw.rect(surf, (30, 30, 40), (px, py, pw, ph))
        pygame.draw.rect(surf, WHITE, (px, py, pw, ph), 2)
        t = FONT_LG.render("INVENTARIO", True, WHITE)
        surf.blit(t, (px + pw // 2 - t.get_width() // 2, py + 10))

        items = list(player.inventory.items())
        yo = py + 50
        for i, (iid, qty) in enumerate(items):
            info = ITEMS.get(iid, {"name": iid, "color": GRAY})
            c = info["color"]
            pygame.draw.rect(surf, c, (px + 20, yo, 24, 24))
            pygame.draw.rect(surf, WHITE, (px + 20, yo, 24, 24), 1)
            label = f"{info['name']} x{qty}"
            if iid in ARMOR_TYPES:
                ainfo = ARMOR_TYPES[iid]
                label += f" [{ainfo['slot']} DEF:{ainfo['defense']}]"
            surf.blit(FONT_MD.render(label, True, WHITE), (px + 52, yo + 3))
            surf.blit(FONT_SM.render(f"[{i + 1}]", True, YELLOW), (px + pw - 50, yo + 3))
            yo += 32

        surf.blit(FONT_SM.render(f"Slots: {player.get_slot_count()}/{player.max_slots}", True, GRAY), (px + 20, py + ph - 30))
        surf.blit(FONT_SM.render(f"Presiona [1-{min(len(items),8)}] | I cerrar", True, YELLOW), (px + 20, py + ph - 50))

    def _draw_crafting(self, surf, player):
        if self._panel_bg is None:
            ov = pygame.Surface((RENDER_W, RENDER_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 180))
            self._panel_bg = ov
        surf.blit(self._panel_bg, (0, 0))
        px, py, pw, ph = RENDER_W // 2 - 150, RENDER_H // 2 - 140, 300, 280
        pygame.draw.rect(surf, (30, 30, 40), (px, py, pw, ph))
        pygame.draw.rect(surf, WHITE, (px, py, pw, ph), 2)
        t = FONT_LG.render("CRAFTING", True, WHITE)
        surf.blit(t, (px + pw // 2 - t.get_width() // 2, py + 10))

        yo = py + 50
        for idx, (rid, recipe) in enumerate(RECIPES.items()):
            ri = ITEMS.get(recipe["result"], {"name": recipe["result"]})
            can = all(player.inventory.get(m, 0) >= q for m, q in recipe["mats"].items())
            c = GREEN if can else GRAY
            surf.blit(FONT_MD.render(f"{ri['name']} x{recipe['qty']}", True, c), (px + 20, yo))
            surf.blit(FONT_SM.render("  ".join(f"{m}:{q}" for m, q in recipe["mats"].items()), True, (180, 180, 180)), (px + 220, yo + 2))
            if can:
                surf.blit(FONT_SM.render(f"[{idx + 1}]", True, YELLOW), (px + pw - 50, yo + 2))
            yo += 30
        surf.blit(FONT_SM.render(f"Presiona [1-{len(RECIPES)}] | C cerrar", True, YELLOW), (px + 20, py + ph - 30))

    def _draw_messages(self, surf):
        yo = RENDER_H - 60
        for msg in self.messages[-5:]:
            t = FONT_SM.render(msg, True, WHITE)
            surf.blit(t, (8, yo))
            yo += 14

    def _draw_controls(self, surf):
        if self._ctrl_labels is None:
            lines = [
                "WASD  Caminar",
                "SHIFT Correr",
                "SPACE Atacar",
                "R     Disparar/Molotov",
                "E     Recoger",
                "F     Linterna",
                "F5    Guardar",
                "F9    Cargar",
                "I     Inventario",
                "C     Crafting",
                "1-8   Usar/Equipar",
            ]
            self._ctrl_labels = [FONT_SM.render(l, True, (140, 140, 140)) for l in lines]
        yo = RENDER_H - 220
        for t in self._ctrl_labels:
            surf.blit(t, (RENDER_W - 160, yo))
            yo += 12
