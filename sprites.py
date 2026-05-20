import pygame

_cache = {}

def _draw_head(surf, skin, x, y, w, h):
    pygame.draw.rect(surf, skin, (x, y, w, h))

def _draw_eyes(surf, x, y):
    pygame.draw.rect(surf, (200, 40, 40), (x, y, 2, 2))
    pygame.draw.rect(surf, (200, 40, 40), (x + 4, y, 2, 2))

def _draw_mouth(surf, x, y, w):
    pygame.draw.rect(surf, (55, 28, 28), (x, y, w, 2))

def _make_zombie_frames(ztype):
    size = 28
    f0 = pygame.Surface((size, size), pygame.SRCALPHA)
    f1 = pygame.Surface((size, size), pygame.SRCALPHA)

    if ztype == "common":
        skin = (130, 165, 100)
        shirt = (105, 82, 58)
        pants = (55, 42, 28)
        for surf, leg_off in [(f0, 0), (f1, 1)]:
            _draw_head(surf, skin, 9, 1, 10, 8)
            _draw_eyes(surf, 11, 3)
            _draw_mouth(surf, 12, 7, 4)
            pygame.draw.rect(surf, shirt, (6, 8, 16, 9))
            pygame.draw.rect(surf, skin, (0, 9, 7, 4))
            pygame.draw.rect(surf, skin, (21, 9, 7, 4))
            pygame.draw.rect(surf, pants, (8 + leg_off, 17, 5, 8))
            pygame.draw.rect(surf, pants, (15 - leg_off, 17, 5, 8))
            pygame.draw.rect(surf, skin, (8, 16, 3, 3))
            pygame.draw.rect(surf, skin, (17, 16, 3, 3))

    elif ztype == "runner":
        skin = (175, 200, 140)
        shirt = (210, 185, 155)
        pants = (90, 90, 115)
        for surf, leg_off in [(f0, 0), (f1, 2)]:
            _draw_head(surf, skin, 10, 1, 8, 7)
            _draw_eyes(surf, 12, 3)
            pygame.draw.rect(surf, shirt, (8, 8, 12, 8))
            pygame.draw.rect(surf, skin, (2, 9, 6, 3))
            pygame.draw.rect(surf, skin, (20, 9, 6, 3))
            pygame.draw.rect(surf, pants, (9 + leg_off, 16, 4, 9))
            pygame.draw.rect(surf, pants, (16 - leg_off, 16, 4, 9))
            pygame.draw.rect(surf, skin, (8, 16, 2, 2))
            pygame.draw.rect(surf, skin, (18, 16, 2, 2))

    elif ztype == "executive":
        skin = (145, 155, 175)
        suit = (38, 38, 75)
        pants = (28, 28, 50)
        for surf, leg_off in [(f0, 0), (f1, 1)]:
            _draw_head(surf, skin, 9, 1, 10, 8)
            _draw_eyes(surf, 11, 3)
            _draw_mouth(surf, 12, 7, 4)
            pygame.draw.rect(surf, suit, (6, 8, 16, 9))
            pygame.draw.rect(surf, (200, 28, 28), (12, 10, 4, 5))
            pygame.draw.rect(surf, skin, (0, 9, 7, 4))
            pygame.draw.rect(surf, skin, (21, 9, 7, 4))
            pygame.draw.rect(surf, pants, (8 + leg_off, 17, 5, 8))
            pygame.draw.rect(surf, pants, (15 - leg_off, 17, 5, 8))
            pygame.draw.rect(surf, skin, (7, 16, 3, 3))
            pygame.draw.rect(surf, skin, (18, 16, 3, 3))

    elif ztype == "tank":
        skin = (95, 115, 72)
        cloth = (60, 48, 28)
        pants = (40, 32, 22)
        for surf, leg_off in [(f0, 0), (f1, 2)]:
            pygame.draw.rect(surf, skin, (7, 0, 14, 10))
            _draw_eyes(surf, 9, 3)
            _draw_mouth(surf, 10, 7, 6)
            pygame.draw.rect(surf, cloth, (4, 9, 20, 11))
            pygame.draw.rect(surf, skin, (0, 10, 6, 5))
            pygame.draw.rect(surf, skin, (22, 10, 6, 5))
            pygame.draw.rect(surf, pants, (8 + leg_off, 20, 5, 7))
            pygame.draw.rect(surf, pants, (15 - leg_off, 20, 5, 7))
            pygame.draw.rect(surf, skin, (7, 19, 3, 3))
            pygame.draw.rect(surf, skin, (18, 19, 3, 3))

    return f0, f1


def get_zombie_sprite(ztype, frame=0):
    key = (ztype, frame)
    if key not in _cache:
        f0, f1 = _make_zombie_frames(ztype)
        _cache[(ztype, 0)] = f0
        _cache[(ztype, 1)] = f1
    return _cache[key]


def _draw_weapon(surf, weapon, special):
    if weapon == "rama":
        if special == "attack":
            pygame.draw.line(surf, (100, 70, 30), (22, 6), (18, 0), 2)
        else:
            pygame.draw.line(surf, (100, 70, 30), (24, 12), (26, 4), 2)
    elif weapon == "bat":
        if special == "attack":
            pygame.draw.rect(surf, (160, 120, 60), (19, 0, 4, 12))
        else:
            pygame.draw.rect(surf, (160, 120, 60), (23, 5, 4, 12))
            pygame.draw.rect(surf, (180, 140, 70), (22, 14, 6, 4))
    elif weapon == "spear":
        if special == "attack":
            pygame.draw.line(surf, (140, 100, 50), (21, 0), (21, 14), 2)
            pygame.draw.rect(surf, (180, 160, 130), (20, 0, 2, 4))
        else:
            pygame.draw.line(surf, (140, 100, 50), (25, 0), (25, 16), 2)
            pygame.draw.rect(surf, (180, 160, 130), (24, 0, 2, 4))
    elif weapon == "pistol":
        if special == "attack":
            pygame.draw.rect(surf, (100, 100, 100), (20, 6, 8, 4))
            pygame.draw.rect(surf, (80, 80, 80), (24, 5, 3, 6))
        else:
            pygame.draw.rect(surf, (100, 100, 100), (22, 10, 6, 3))
            pygame.draw.rect(surf, (80, 80, 80), (26, 9, 3, 5))


def _draw_armor(surf, head, body, legs):
    if head:
        c = __import__('config', fromlist=['ARMOR_TYPES']).ARMOR_TYPES[head]["color"]
        pygame.draw.rect(surf, c, (8, 0, 12, 5))
        pygame.draw.rect(surf, tuple(min(255, v + 30) for v in c), (9, 1, 10, 3))
    if body:
        c = __import__('config', fromlist=['ARMOR_TYPES']).ARMOR_TYPES[body]["color"]
        pygame.draw.rect(surf, c, (7, 8, 14, 9))
        pygame.draw.rect(surf, tuple(min(255, v + 20) for v in c), (8, 9, 12, 7))


def _build_player_surf(leg_offset=0, special=None, weapon="fists", head_armor=None, body_armor=None, legs_armor=None):
    size = 28
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    skin = (210, 180, 150)
    hair = (60, 40, 20)
    shirt = (60, 100, 180)
    pants = (50, 60, 110)
    backpack = (40, 40, 50)
    shoes = (30, 30, 30)
    bandage_c = (220, 200, 180)

    # Hair & head
    _draw_armor(surf, head_armor, None, None)
    if not head_armor:
        pygame.draw.rect(surf, hair, (9, 0, 10, 4))
    _draw_head(surf, skin, 9, 3, 10, 6)
    pygame.draw.rect(surf, (200, 60, 60), (11, 4, 2, 2))
    pygame.draw.rect(surf, (60, 60, 60), (15, 4, 2, 2))
    pygame.draw.rect(surf, (160, 120, 90), (12, 7, 4, 2))
    _draw_armor(surf, None, body_armor, None)
    if not body_armor:
        pygame.draw.rect(surf, shirt, (7, 8, 14, 9))
    pygame.draw.rect(surf, backpack, (19, 8, 8, 11))

    # Arms with natural swing (no T-pose)
    lo = leg_offset if special not in ("attack", "heal") else 0
    if special == "attack":
        pygame.draw.rect(surf, skin, (0, 9, 7, 4))
        pygame.draw.rect(surf, skin, (21, 7, 7, 7))
        pygame.draw.rect(surf, shirt, (22, 9, 6, 4))
    elif special == "heal":
        pygame.draw.rect(surf, skin, (9, 10, 10, 4))
        pygame.draw.rect(surf, bandage_c, (11, 9, 6, 6))
        pygame.draw.rect(surf, skin, (0, 9, 7, 4))
        pygame.draw.rect(surf, skin, (21, 9, 7, 4))
    elif lo > 0:  # left leg forward → right arm forward
        pygame.draw.rect(surf, skin, (0, 10, 6, 4))
        pygame.draw.rect(surf, skin, (22, 9, 6, 4))
    elif lo < 0:  # right leg forward → left arm forward
        pygame.draw.rect(surf, skin, (0, 9, 6, 4))
        pygame.draw.rect(surf, skin, (20, 10, 6, 4))
    else:  # idle: arms relax slightly down
        pygame.draw.rect(surf, skin, (2, 10, 6, 4))
        pygame.draw.rect(surf, skin, (20, 10, 6, 4))

    # Legs
    pygame.draw.rect(surf, pants, (8 + lo, 17, 5, 7))
    pygame.draw.rect(surf, pants, (15 - lo, 17, 5, 7))
    pygame.draw.rect(surf, shoes, (8 + lo, 24, 5, 3))
    pygame.draw.rect(surf, shoes, (15 - lo, 24, 5, 3))

    _draw_weapon(surf, weapon, special)
    return surf


def _make_player_frames(weapon="fists", head_armor=None, body_armor=None, legs_armor=None):
    frames = {}
    frames[("idle", 0)] = _build_player_surf(0, weapon=weapon, head_armor=head_armor, body_armor=body_armor, legs_armor=legs_armor)
    for lo in (1, -1):
        frames[("walk", lo)] = _build_player_surf(lo, weapon=weapon, head_armor=head_armor, body_armor=body_armor, legs_armor=legs_armor)
        frames[("run", lo)] = _build_player_surf(lo, weapon=weapon, head_armor=head_armor, body_armor=body_armor, legs_armor=legs_armor)
    frames[("attack", 0)] = _build_player_surf(0, "attack", weapon=weapon, head_armor=head_armor, body_armor=body_armor, legs_armor=legs_armor)
    frames[("attack", 1)] = _build_player_surf(0, weapon=weapon, head_armor=head_armor, body_armor=body_armor, legs_armor=legs_armor)
    frames[("heal", 0)] = _build_player_surf(0, "heal", weapon=weapon, head_armor=head_armor, body_armor=body_armor, legs_armor=legs_armor)
    frames[("heal", 1)] = _build_player_surf(0, weapon=weapon, head_armor=head_armor, body_armor=body_armor, legs_armor=legs_armor)
    return frames


_player_frame_cache = {}

def get_player_sprite(state="idle", frame=0, weapon="fists", head_armor=None, body_armor=None, legs_armor=None):
    key = (weapon, head_armor, body_armor, legs_armor)
    if key not in _player_frame_cache:
        _player_frame_cache[key] = _make_player_frames(weapon, head_armor, body_armor, legs_armor)
    return _player_frame_cache[key].get((state, frame), _player_frame_cache[key][("idle", 0)])


_item_sprites = {}

def get_item_sprite(item_id):
    if item_id not in _item_sprites:
        sz = 14
        s = pygame.Surface((sz, sz), pygame.SRCALPHA)
        if item_id == "food":
            pygame.draw.rect(s, (200, 150, 50), (1, 2, 12, 10))
            pygame.draw.rect(s, (220, 180, 80), (3, 4, 8, 6))
            pygame.draw.rect(s, (180, 120, 30), (4, 1, 6, 3))
        elif item_id == "water":
            pygame.draw.rect(s, (60, 140, 220), (3, 1, 8, 12))
            pygame.draw.rect(s, (100, 180, 240), (4, 3, 6, 8))
            pygame.draw.rect(s, (40, 80, 160), (3, 12, 8, 2))
        elif item_id == "medkit":
            pygame.draw.rect(s, (200, 60, 60), (1, 1, 12, 12))
            pygame.draw.rect(s, (255, 255, 255), (5, 2, 4, 10))
            pygame.draw.rect(s, (255, 255, 255), (2, 5, 10, 4))
        elif item_id == "bandage":
            pygame.draw.rect(s, (220, 200, 180), (2, 3, 10, 8))
            pygame.draw.rect(s, (240, 220, 200), (4, 4, 6, 6))
            pygame.draw.line(s, (200, 180, 160), (3, 5), (11, 5), 1)
            pygame.draw.line(s, (200, 180, 160), (3, 7), (11, 7), 1)
            pygame.draw.line(s, (200, 180, 160), (3, 9), (11, 9), 1)
        elif item_id == "bat":
            pygame.draw.rect(s, (160, 120, 60), (6, 0, 3, 14))
            pygame.draw.rect(s, (180, 140, 70), (5, 10, 5, 4))
        elif item_id == "pistol":
            pygame.draw.rect(s, (100, 100, 100), (2, 4, 10, 5))
            pygame.draw.rect(s, (80, 80, 80), (7, 3, 4, 7))
            pygame.draw.rect(s, (60, 60, 60), (1, 5, 3, 3))
        elif item_id in ("cloth", "hat_cloth", "vest_cloth", "pants_cloth"):
            c = (200, 180, 160)
            pygame.draw.rect(s, c, (2, 2, 10, 10))
            pygame.draw.rect(s, tuple(v-20 for v in c), (4, 4, 6, 6))
        elif item_id in ("wood",):
            pygame.draw.rect(s, (140, 100, 50), (3, 1, 8, 12))
            pygame.draw.rect(s, (160, 120, 70), (5, 3, 4, 8))
        elif item_id == "metal":
            pygame.draw.rect(s, (150, 150, 160), (2, 2, 10, 10))
            pygame.draw.rect(s, (170, 170, 180), (4, 4, 6, 6))
            pygame.draw.rect(s, (130, 130, 140), (6, 1, 2, 12))
        elif item_id == "alcohol":
            pygame.draw.rect(s, (200, 220, 240), (3, 1, 8, 10))
            pygame.draw.rect(s, (180, 200, 220), (4, 2, 6, 8))
            pygame.draw.rect(s, (160, 180, 200), (5, 11, 4, 3))
        elif item_id == "rama":
            pygame.draw.line(s, (100, 70, 30), (7, 13), (2, 1), 3)
            pygame.draw.line(s, (80, 50, 20), (4, 4), (1, 2), 1)
            pygame.draw.line(s, (80, 50, 20), (6, 6), (8, 3), 1)
        elif item_id == "linterna":
            pygame.draw.rect(s, (180, 180, 120), (4, 2, 6, 10))
            pygame.draw.rect(s, (220, 220, 100), (5, 1, 4, 4))
            pygame.draw.rect(s, (200, 200, 80), (5, 9, 4, 4))
        elif item_id.startswith("hat_"):
            c = (120, 80, 40)
            pygame.draw.rect(s, c, (2, 4, 10, 6))
            pygame.draw.rect(s, tuple(v+30 for v in c), (3, 5, 8, 4))
            pygame.draw.rect(s, c, (4, 1, 6, 4))
        elif item_id.startswith("vest_"):
            c = (80, 50, 30)
            pygame.draw.rect(s, c, (1, 3, 12, 9))
            pygame.draw.rect(s, tuple(v+20 for v in c), (3, 4, 8, 7))
            pygame.draw.line(s, (60, 40, 20), (7, 4), (7, 11), 1)
        elif item_id.startswith("pants_"):
            c = (70, 50, 30)
            pygame.draw.rect(s, c, (2, 2, 10, 10))
            pygame.draw.rect(s, tuple(v+20 for v in c), (3, 3, 4, 8))
            pygame.draw.rect(s, tuple(v+20 for v in c), (7, 3, 4, 8))
        else:
            info = __import__('config', fromlist=['ITEMS']).ITEMS.get(item_id, {})
            c = info.get("color", (200, 200, 200))
            pygame.draw.rect(s, c, (1, 1, 12, 12))
            pygame.draw.rect(s, (255, 255, 255), (0, 0, 14, 14), 1)
        _item_sprites[item_id] = s
    return _item_sprites[item_id]
