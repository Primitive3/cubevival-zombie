import pygame
import math
import random
import struct

pygame.mixer.init(frequency=22050, size=-16, channels=4)

def _make_sound(freq, duration, volume=0.3, wave="sine", decay=True):
    sr = 22050
    n = int(sr * duration)
    data = []
    for i in range(n):
        t = i / sr
        env = 1.0 - i / n if decay else 1.0
        if wave == "sine":
            v = math.sin(2 * math.pi * freq * t)
        elif wave == "square":
            v = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
        elif wave == "noise":
            v = random.uniform(-1, 1)
        elif wave == "saw":
            v = 2.0 * (freq * t - math.floor(freq * t + 0.5))
        else:
            v = 0
        data.append(max(-32768, min(32767, int(volume * 32767 * v * env))))
    buf = struct.pack(f"<{n}h", *data)
    return pygame.mixer.Sound(buffer=buf)

_cache = {}
_PARAMS = {
    "zombie_moan":   (70,   1.5,  0.12, "saw",   True),
    "footstep":      (40,   0.08, 0.18, "square", False),
    "attack_swing":  (200,  0.15, 0.22, "noise",  True),
    "player_hurt":   (150,  0.3,  0.28, "saw",   True),
    "heal":          (400,  0.4,  0.18, "sine",   True),
    "pickup":        (600,  0.15, 0.15, "sine",   False),
    "flashlight":    (1000, 0.05, 0.18, "square", False),
    "cricket":       (3000, 0.1,  0.08, "sine",   False),
}

def play(name):
    if name not in _cache:
        p = _PARAMS[name]
        _cache[name] = _make_sound(*p)
    _cache[name].play()
