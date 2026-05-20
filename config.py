import pygame

# Display
SCREEN_W = 960
SCREEN_H = 640
TILE = 32
FPS = 60

# Map
MAP_W = 90
MAP_H = 70
BLOCK = 10

# Player
PLAYER_SPEED = 0.2
PLAYER_HP = 100
PLAYER_HUNGER = 100
PLAYER_THIRST = 100
PLAYER_STAMINA = 100
MAX_STACK = 12
PICKUP_RANGE = 32
HUNGER_DRAIN = 0.000055
THIRST_DRAIN = 0.000067
STAMINA_DRAIN = 0.45
STAMINA_REGEN = 0.006
IFRAMES = 45
STARVATION_DMG = 0.0008
DEHYDRATION_DMG = 0.001

# Zombies
ZOMBIE_BASE_SPEED = 1.2
ZOMBIE_DETECT_RANGE = 220
ZOMBIE_ATTACK_RANGE = 0.5
ZOMBIE_ATTACK_COOLDOWN = 90
ZOMBIE_DAMAGE = 8
ZOMBIE_SPAWN_MIN = 20
ZOMBIE_SPAWN_MAX = 35

# Day/Night
DAY_LENGTH = 7200
NIGHT_LENGTH = 2400
CYCLE_LENGTH = DAY_LENGTH + NIGHT_LENGTH

# Tile types
T_GRASS = 0
T_ROAD = 1
T_WALL = 2
T_FLOOR = 3
T_DOOR = 4
T_TREE = 5
T_WATER = 6

TILE_COLORS = {
    T_GRASS: (60, 120, 50),
    T_ROAD: (80, 80, 80),
    T_WALL: (100, 80, 60),
    T_FLOOR: (180, 160, 130),
    T_DOOR: (160, 130, 80),
    T_TREE: (30, 80, 20),
    T_WATER: (40, 80, 140),
}

TILE_VARIATIONS = 8

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 40, 40)
GREEN = (40, 180, 40)
BLUE = (40, 100, 220)
YELLOW = (220, 200, 40)
ORANGE = (220, 140, 20)
PURPLE = (160, 40, 200)
GRAY = (120, 120, 120)
DARK = (20, 20, 30)
BROWN = (140, 100, 60)

# Item definitions
ITEMS = {
    "food":      {"name": "Lata de atún",      "color": (200, 150, 50),  "icon": "F", "heal": 8,  "hunger": 65, "thirst": 0},
    "water":     {"name": "Agua embotellada",  "color": (60, 140, 220),  "icon": "W", "heal": 0,  "hunger": 0,  "thirst": 70},
    "medkit":    {"name": "Botiquín",          "color": (200, 60, 60),   "icon": "+", "heal": 75, "hunger": 0,  "thirst": 0},
    "bandage":   {"name": "Venda",             "color": (220, 200, 180), "icon": "B", "heal": 40, "hunger": 0,  "thirst": 0},
    "bat":       {"name": "Bate de béisbol",   "color": (180, 140, 60),  "icon": "b", "dmg": 28},
    "pistol":    {"name": "Pistola 9mm",       "color": (100, 100, 100), "icon": "P", "dmg": 45},
    "ammo":      {"name": "Munición",          "color": (180, 180, 60),  "icon": "a", "qty": 10},
    "wood":      {"name": "Madera",            "color": (140, 100, 50),  "icon": "M"},
    "metal":     {"name": "Metal",             "color": (150, 150, 160), "icon": "m"},
    "cloth":     {"name": "Tela",              "color": (200, 180, 160), "icon": "T"},
    "alcohol":   {"name": "Alcohol",           "color": (200, 220, 240), "icon": "A"},
    "spear":     {"name": "Lanza improvisada", "color": (160, 120, 60),  "icon": "L", "dmg": 38},
    "molotov":   {"name": "Cóctel Molotov",    "color": (220, 100, 30),  "icon": "X", "dmg": 60},
    "book":      {"name": "Manual antiguo",    "color": (140, 80, 160),  "icon": "?"},
    "rama":      {"name": "Rama de árbol",     "color": (100, 70, 30),   "icon": "r", "dmg": 8},
    "linterna":  {"name": "Linterna",          "color": (220, 220, 100),"icon": "L"},
}

# Armor types (inventory items)
ARMOR_TYPES = {
    "hat_cloth":    {"name": "Gorra de tela",       "slot": "head", "defense": 2,  "color": (160, 140, 120)},
    "hat_leather":  {"name": "Gorra de cuero",      "slot": "head", "defense": 4,  "color": (120, 80, 40)},
    "hat_military": {"name": "Casco militar",       "slot": "head", "defense": 7,  "color": (70, 90, 60)},
    "vest_cloth":   {"name": "Chaleco de tela",     "slot": "body", "defense": 2,  "color": (140, 120, 100)},
    "vest_leather": {"name": "Chaqueta de cuero",   "slot": "body", "defense": 4,  "color": (80, 50, 30)},
    "vest_military":{"name": "Chaleco militar",     "slot": "body", "defense": 7,  "color": (60, 80, 50)},
    "pants_cloth":  {"name": "Pantalones de tela",   "slot": "legs", "defense": 2,  "color": (100, 100, 120)},
    "pants_leather":{"name": "Pantalones de cuero",  "slot": "legs", "defense": 4,  "color": (70, 50, 30)},
    "pants_military":{"name": "Pantalones militares","slot": "legs", "defense": 7,  "color": (60, 80, 50)},
}
ARMOR_SLOTS = ["head", "body", "legs"]
ARMOR_NAMES = {k: v["name"] for k, v in ARMOR_TYPES.items()}

# Add armor to ITEMS so they render in inventory
for aid, ainfo in ARMOR_TYPES.items():
    ITEMS[aid] = {"name": ainfo["name"], "color": ainfo["color"], "icon": "A"}

# Crafting recipes
RECIPES = {
    "bandage": {"mats": {"cloth": 2, "alcohol": 1}, "result": "bandage",  "qty": 2},
    "spear":   {"mats": {"wood": 2, "cloth": 1},     "result": "spear",   "qty": 1},
    "molotov": {"mats": {"alcohol": 2, "cloth": 2},  "result": "molotov", "qty": 1},
}

# Zombie types
ZOMBIE_TYPES = {
    "common":    {"hp": 35,  "speed": 0.03, "color": (130, 165, 100), "dmg": 4,  "label": "Zombie común"},
    "runner":    {"hp": 20,  "speed": 0.07, "color": (175, 200, 140), "dmg": 3,  "label": "Runner zombie"},
    "executive": {"hp": 50,  "speed": 0.02, "color": (145, 155, 175), "dmg": 5,  "label": "Ejecutivo zombie"},
    "tank":      {"hp": 90,  "speed": 0.01, "color": (95, 115, 72),   "dmg": 8,  "label": "Zombie tanque"},
}

pygame.font.init()
FONT_SM = pygame.font.Font(None, 16)
FONT_MD = pygame.font.Font(None, 22)
FONT_LG = pygame.font.Font(None, 28)
FONT_TITLE = pygame.font.Font(None, 40)
