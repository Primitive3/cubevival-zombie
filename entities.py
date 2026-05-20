import math
import random
from config import *
from sounds import play as play_sound

class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.hw = 0.35
        self.hh = 0.35
        self.hp = PLAYER_HP
        self.max_hp = PLAYER_HP
        self.hunger = PLAYER_HUNGER
        self.thirst = PLAYER_THIRST
        self.stamina = PLAYER_STAMINA
        self.inventory = {}
        self.max_slots = MAX_STACK
        self.weapon = "rama"
        self.ammo = 0
        self.attack_cooldown = 0
        self.kills = 0
        self.days_survived = 0
        self.iframes = 0
        self.hurt_flash = 0
        self.anim_state = "idle"
        self.anim_frame = 0
        self.anim_timer = 0
        self.attack_frames = 0
        self.heal_frames = 0
        self.armor = {"head": None, "body": None, "legs": None}
        self.flashlight_on = False

    def move(self, dx, dy, world, running=False):
        spd = PLAYER_SPEED
        moving = abs(dx) > 0 or abs(dy) > 0
        if moving:
            tile = world.get_tile(int(self.x + dx), int(self.y + dy))
            if tile == T_ROAD:
                spd *= 1.2
            if self.stamina <= 20:
                spd *= 0.7
            if running and self.stamina > 5:
                spd *= 1.8
                if self.stamina > 0:
                    self.stamina -= STAMINA_DRAIN * (abs(dx) + abs(dy)) * 1.2
            elif self.stamina > 0:
                self.stamina -= STAMINA_DRAIN * (abs(dx) + abs(dy)) * 0.5

            if self.attack_frames > 0:
                self.anim_state = "attack"
            elif self.heal_frames > 0:
                self.anim_state = "heal"
            elif running and self.stamina > 5:
                self.anim_state = "run"
            else:
                self.anim_state = "walk"
        else:
            if self.attack_frames > 0:
                self.anim_state = "attack"
            elif self.heal_frames > 0:
                self.anim_state = "heal"
            else:
                self.anim_state = "idle"

        nx = self.x + dx * spd
        ny = self.y + dy * spd

        if world.is_walkable(int(nx), int(self.y)):
            self.x = nx
        if world.is_walkable(int(self.x), int(ny)):
            self.y = ny
        if moving and self.anim_frame == 0 and self.anim_timer == 0:
            play_sound("footstep")

    def get_defense(self):
        total = 0
        for slot_id, item_id in self.armor.items():
            if item_id and item_id in ARMOR_TYPES:
                total += ARMOR_TYPES[item_id]["defense"]
        return total

    def take_damage(self, dmg):
        if self.iframes > 0:
            return False
        defense = self.get_defense()
        reduced = max(1, int(dmg - defense * 0.3))
        self.hp -= reduced
        self.iframes = IFRAMES
        self.hurt_flash = 8
        play_sound("player_hurt")
        return True

    def attack(self, zombies):
        if self.attack_cooldown > 0 or self.attack_frames > 0:
            return None
        self.attack_cooldown = 20
        self.attack_frames = 12
        self.anim_state = "attack"
        self.anim_frame = 0
        self.anim_timer = 0
        play_sound("attack_swing")
        dmg_map = {"fists": 5, "rama": 10, "bat": 25, "spear": 35, "pistol": 45}
        dmg = dmg_map.get(self.weapon, 8)
        noisy = self.weapon in ("bat", "pistol")
        hit = False
        reach = 1.5
        for z in zombies:
            dx = abs(self.x - z.x) - (self.hw + z.hw)
            dy = abs(self.y - z.y) - (self.hh + z.hh)
            d = math.hypot(max(0, dx), max(0, dy))
            if d < reach:
                z.hp -= dmg
                z.stun = 15
                z.hit_flash = 6
                hit = True
        return hit, noisy, dmg

    def shoot(self, zombies):
        if self.weapon != "pistol" or self.ammo <= 0 or self.attack_cooldown > 0:
            return None
        self.ammo -= 1
        self.attack_cooldown = 25
        closest = None
        min_d = 350
        for z in zombies:
            d = math.hypot(self.x - z.x, self.y - z.y)
            if d < min_d:
                min_d = d
                closest = z
        if closest:
            dmg = ITEMS.get("pistol", {}).get("dmg", 45)
            closest.hp -= dmg
            closest.stun = 25
            closest.hit_flash = 10
            return True, dmg, closest
        return True, 0, None

    def update(self, dt, moving=False):
        self.attack_cooldown = max(0, self.attack_cooldown - 1)
        self.iframes = max(0, self.iframes - 1)
        self.hurt_flash = max(0, self.hurt_flash - 1)

        self.hunger -= HUNGER_DRAIN * dt
        self.thirst -= THIRST_DRAIN * dt
        if self.hunger <= 0:
            self.hp -= STARVATION_DMG * dt
        if self.thirst <= 0:
            self.hp -= DEHYDRATION_DMG * dt

        if not moving and self.stamina < 100:
            self.stamina = min(100, self.stamina + STAMINA_REGEN * dt)
        self.hp = max(0, min(self.max_hp, self.hp))
        self.hunger = max(0, self.hunger)
        self.thirst = max(0, self.thirst)

        if self.attack_frames > 0:
            self.attack_frames -= 1
            self.anim_state = "attack"
            self.anim_timer += 1
            if self.anim_timer >= 5:
                self.anim_frame = 1 - self.anim_frame
                self.anim_timer = 0
        elif self.heal_frames > 0:
            self.heal_frames -= 1
            self.anim_state = "heal"
            self.anim_timer += 1
            if self.anim_timer >= 8:
                self.anim_frame = 1 - self.anim_frame
                self.anim_timer = 0
        elif moving:
            thr = 6 if self.anim_state == "run" else 12
            self.anim_timer += 1
            if self.anim_timer >= thr:
                self.anim_frame = 1 - self.anim_frame
                self.anim_timer = 0
        else:
            self.anim_state = "idle"
            self.anim_frame = 0
            self.anim_timer = 0

    def use_item(self, item_id):
        if item_id not in self.inventory or self.inventory[item_id] <= 0:
            return ("error", None)
        info = ITEMS.get(item_id)
        if not info:
            return ("error", None)

        if item_id == "food":
            self.hunger = min(100, self.hunger + info.get("hunger", 35))
            self.hp = min(self.max_hp, self.hp + info.get("heal", 0))
        elif item_id == "water":
            self.thirst = min(100, self.thirst + info.get("thirst", 40))
        elif item_id in ("medkit", "bandage"):
            self.hp = min(self.max_hp, self.hp + info.get("heal", 25))
        elif item_id in ("rama", "bat", "spear", "pistol"):
            self.weapon = item_id
        elif item_id == "ammo":
            self.ammo += info.get("qty", 10)
        elif item_id == "book":
            self.hp = min(self.max_hp, self.hp + 15)
        elif item_id == "linterna":
            self.flashlight_on = not self.flashlight_on
            return ("flashlight", item_id)
        elif item_id == "molotov":
            return ("throw", item_id)
        elif item_id in ARMOR_TYPES:
            slot = ARMOR_TYPES[item_id]["slot"]
            old = self.armor[slot]
            self.armor[slot] = item_id
            self.inventory[item_id] -= 1
            if self.inventory[item_id] <= 0:
                del self.inventory[item_id]
            if old:
                self.inventory[old] = self.inventory.get(old, 0) + 1
            return ("equip", item_id)
        else:
            return ("error", None)

        self.inventory[item_id] -= 1
        if self.inventory[item_id] <= 0:
            del self.inventory[item_id]
        return ("used", item_id)

    def get_slot_count(self):
        return sum(self.inventory.values())

    def can_pickup(self):
        return self.get_slot_count() < self.max_slots

    def pickup(self, item_id, qty=1):
        if not self.can_pickup():
            return False
        self.inventory[item_id] = self.inventory.get(item_id, 0) + qty
        return True


class Zombie:
    def __init__(self, x, y, ztype="common"):
        self.x = float(x)
        self.y = float(y)
        self.hw = 0.35
        self.hh = 0.35
        info = ZOMBIE_TYPES[ztype]
        self.ztype = ztype
        self.max_hp = info["hp"]
        self.hp = info["hp"]
        self.speed = info["speed"]
        self.color = info["color"]
        self.dmg = info["dmg"]
        self.label = info["label"]
        self.attack_cooldown = 0
        self.stun = 0
        self.hit_flash = 0
        self.roam_angle = random.uniform(0, math.pi * 2)
        self.roam_timer = 0
        self.anim_frame = 0
        self.anim_timer = 0

    def update(self, player, world, dt):
        self.attack_cooldown = max(0, self.attack_cooldown - 1)
        self.stun = max(0, self.stun - 1)
        self.hit_flash = max(0, self.hit_flash - 1)
        if self.stun > 0:
            return

        self.roam_timer -= 1
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        moving = False
        if dist < ZOMBIE_DETECT_RANGE:
            if dist > ZOMBIE_ATTACK_RANGE:
                move_x = (dx / dist) * self.speed
                move_y = (dy / dist) * self.speed
                nx = self.x + move_x
                ny = self.y + move_y
                if world.is_walkable(int(nx), int(self.y)):
                    self.x = nx
                    moving = True
                if world.is_walkable(int(self.x), int(ny)):
                    self.y = ny
                    moving = True
        else:
            if random.random() < 0.003:
                play_sound("zombie_moan")
            if self.roam_timer <= 0:
                self.roam_angle = random.uniform(0, math.pi * 2)
                self.roam_timer = random.randint(30, 120)
            move_x = math.cos(self.roam_angle) * self.speed * 0.3
            move_y = math.sin(self.roam_angle) * self.speed * 0.3
            if world.is_walkable(int(self.x + move_x), int(self.y)):
                self.x += move_x
                moving = True
            if world.is_walkable(int(self.x), int(self.y + move_y)):
                self.y += move_y
                moving = True

        if moving:
            self.anim_timer += 1
            if self.anim_timer >= 12:
                self.anim_frame = 1 - self.anim_frame
                self.anim_timer = 0
        else:
            self.anim_frame = 0
            self.anim_timer = 0

    def can_attack(self, player):
        if self.attack_cooldown > 0:
            return False
        dx = abs(self.x - player.x) - (self.hw + player.hw)
        dy = abs(self.y - player.y) - (self.hh + player.hh)
        if dx < 0 and dy < 0:
            return True
        return math.hypot(max(0, dx), max(0, dy)) < ZOMBIE_ATTACK_RANGE


class ItemDrop:
    def __init__(self, x, y, item_id, qty=1):
        self.x = float(x) + 0.5
        self.y = float(y) + 0.5
        self.item_id = item_id
        self.qty = qty
        self.bob = random.uniform(0, math.pi * 2)

    def update(self):
        self.bob += 0.05
