import json
import os
import pygame
from config import *
from entities import Player, ItemDrop

SAVE_DIR = "saves"
SAVE_FILE = os.path.join(SAVE_DIR, "save.json")

def save_game(player, world):
    os.makedirs(SAVE_DIR, exist_ok=True)
    data = {
        "version": 1,
        "tiles": world.tiles,
        "explored": [[int(v) for v in row] for row in world.explored],
        "world": {
            "time": world.time,
            "game_day": world.game_day,
            "spawn_timer": world.spawn_timer,
        },
        "player": {
            "x": player.x,
            "y": player.y,
            "hp": player.hp,
            "max_hp": player.max_hp,
            "hunger": player.hunger,
            "thirst": player.thirst,
            "stamina": player.stamina,
            "inventory": dict(player.inventory),
            "weapon": player.weapon,
            "ammo": player.ammo,
            "attack_cooldown": player.attack_cooldown,
            "kills": player.kills,
            "days_survived": player.days_survived,
            "iframes": player.iframes,
            "armor": dict(player.armor),
            "flashlight_on": player.flashlight_on,
        },
        "zombies": [
            {
                "x": z.x, "y": z.y, "ztype": z.ztype,
                "hp": z.hp, "attack_cooldown": z.attack_cooldown,
                "stun": z.stun, "hit_flash": z.hit_flash,
                "roam_angle": z.roam_angle, "roam_timer": z.roam_timer,
                "anim_frame": z.anim_frame, "anim_timer": z.anim_timer,
            }
            for z in world.zombies
        ],
        "items": [
            {
                "x": it.x, "y": it.y, "item_id": it.item_id,
                "qty": it.qty, "bob": it.bob,
            }
            for it in world.items
        ],
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return True


def load_game(player, world):
    if not os.path.exists(SAVE_FILE):
        return False
    with open(SAVE_FILE) as f:
        data = json.load(f)
    if data.get("version") != 1:
        return False

    pd = data["player"]
    player.x = pd["x"]
    player.y = pd["y"]
    player.hp = pd["hp"]
    player.max_hp = pd.get("max_hp", PLAYER_HP)
    player.hunger = pd["hunger"]
    player.thirst = pd["thirst"]
    player.stamina = pd["stamina"]
    player.inventory = dict(pd["inventory"])
    player.weapon = pd["weapon"]
    player.ammo = pd["ammo"]
    player.attack_cooldown = pd["attack_cooldown"]
    player.kills = pd["kills"]
    player.days_survived = pd["days_survived"]
    player.iframes = pd.get("iframes", 0)
    player.armor = dict(pd.get("armor", {"head": None, "body": None, "legs": None}))
    player.flashlight_on = pd.get("flashlight_on", False)
    player.hurt_flash = 0
    player.anim_state = "idle"
    player.anim_frame = 0
    player.anim_timer = 0
    player.attack_frames = 0
    player.heal_frames = 0

    wd = data["world"]
    world.time = wd["time"]
    world.game_day = wd["game_day"]
    world.spawn_timer = wd.get("spawn_timer", 360)

    world.tiles = data["tiles"]
    for y in range(min(len(data["explored"]), MAP_H)):
        row = data["explored"][y]
        for x in range(min(len(row), MAP_W)):
            world.explored[y][x] = bool(row[x])

    world.zombies = []
    for zd in data["zombies"]:
        z = Zombie(0, 0, zd["ztype"])
        z.x = zd["x"]
        z.y = zd["y"]
        z.hp = zd["hp"]
        z.attack_cooldown = zd["attack_cooldown"]
        z.stun = zd["stun"]
        z.hit_flash = zd["hit_flash"]
        z.roam_angle = zd["roam_angle"]
        z.roam_timer = zd["roam_timer"]
        z.anim_frame = zd["anim_frame"]
        z.anim_timer = zd["anim_timer"]
        world.zombies.append(z)

    world.items = []
    for itd in data["items"]:
        it = ItemDrop(itd["x"], itd["y"], itd["item_id"], itd["qty"])
        it.bob = itd["bob"]
        world.items.append(it)

    world._last_vpos = (-1, -1)
    return True
