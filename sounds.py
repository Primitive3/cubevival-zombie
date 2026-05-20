import pygame
import math
import random
import struct

pygame.mixer.init(frequency=22050, size=-16, channels=8)

def _mix_waves(*components):
    sr = 22050
    max_n = max(n for _, n in components)
    data = []
    for i in range(max_n):
        t = i / sr
        v = 0.0
        for wave_func, n, vol in components:
            if i < n:
                v += wave_func(t) * vol
        data.append(max(-32768, min(32767, int(v * 32767))))
    buf = struct.pack(f"<{max_n}h", *data)
    return pygame.mixer.Sound(buffer=buf)

def _sine(freq, t):
    return math.sin(2 * math.pi * freq * t)

def _square(freq, t):
    return 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0

def _noise(t):
    return random.uniform(-1, 1)

def _saw(freq, t):
    return 2.0 * (freq * t - math.floor(freq * t + 0.5))

def _env_lin(duration, i, n):
    return 1.0 - i / n

def _env_slow(duration, i, n):
    t = i / n
    return 1.0 - t * t

_cache = {}

def _build(name):
    sr = 22050
    if name == "zombie_moan":
        n = int(sr * 1.5)
        data = []
        for i in range(n):
            t = i / sr
            env = _env_slow(1.5, i, n)
            v = _saw(70, t) * 0.08 + _sine(140, t) * 0.04 + _noise(t) * 0.02
            data.append(max(-32768, min(32767, int(v * env * 32767))))
        buf = struct.pack(f"<{n}h", *data)
        _cache[name] = pygame.mixer.Sound(buffer=buf)
    elif name == "footstep":
        n = int(sr * 0.06)
        data = []
        for i in range(n):
            t = i / sr
            v = _noise(t) * 0.15 + _square(40, t) * 0.08
            env = 1.0 - i / n
            data.append(max(-32768, min(32767, int(v * env * 32767))))
        buf = struct.pack(f"<{n}h", *data)
        _cache[name] = pygame.mixer.Sound(buffer=buf)
    elif name == "attack_swing":
        n = int(sr * 0.12)
        data = []
        for i in range(n):
            t = i / sr
            env = 1.0 - (i / n) ** 2
            v = _noise(t) * 0.15 + _saw(200, t) * 0.08
            data.append(max(-32768, min(32767, int(v * env * 32767))))
        buf = struct.pack(f"<{n}h", *data)
        _cache[name] = pygame.mixer.Sound(buffer=buf)
    elif name == "player_hurt":
        n = int(sr * 0.25)
        data = []
        for i in range(n):
            t = i / sr
            env = _env_slow(0.25, i, n)
            v = _saw(150, t) * 0.15 + _noise(t) * 0.1
            data.append(max(-32768, min(32767, int(v * env * 32767))))
        buf = struct.pack(f"<{n}h", *data)
        _cache[name] = pygame.mixer.Sound(buffer=buf)
    elif name == "heal":
        n = int(sr * 0.35)
        data = []
        for i in range(n):
            t = i / sr
            env = i / n
            f = 400 + 200 * (i / n)
            v = _sine(f, t) * 0.12 + _sine(f * 1.5, t) * 0.06
            data.append(max(-32768, min(32767, int(v * env * 32767))))
        buf = struct.pack(f"<{n}h", *data)
        _cache[name] = pygame.mixer.Sound(buffer=buf)
    elif name == "pickup":
        n = int(sr * 0.12)
        data = []
        for i in range(n):
            t = i / sr
            env = 1.0 - i / n
            f = 600 + 300 * (1.0 - i / n)
            v = _sine(f, t) * 0.12
            data.append(max(-32768, min(32767, int(v * env * 32767))))
        buf = struct.pack(f"<{n}h", *data)
        _cache[name] = pygame.mixer.Sound(buffer=buf)
    elif name == "flashlight":
        n = int(sr * 0.04)
        data = []
        for i in range(n):
            t = i / sr
            v = _square(1000, t) * 0.1
            data.append(max(-32768, min(32767, int(v * 32767))))
        buf = struct.pack(f"<{n}h", *data)
        _cache[name] = pygame.mixer.Sound(buffer=buf)
    elif name == "cricket":
        n = int(sr * 0.08)
        data = []
        for i in range(n):
            t = i / sr
            env = 1.0 - i / n
            v = _sine(3000 + random.randint(-100, 100), t) * 0.05
            data.append(max(-32768, min(32767, int(v * env * 32767))))
        buf = struct.pack(f"<{n}h", *data)
        _cache[name] = pygame.mixer.Sound(buffer=buf)
    elif name == "rain":
        n = int(sr * 0.5)
        data = []
        for i in range(n):
            v = _noise(0) * 0.06
            data.append(max(-32768, min(32767, int(v * 32767))))
        buf = struct.pack(f"<{n}h", *data)
        _cache[name] = pygame.mixer.Sound(buffer=buf)
    elif name == "wind":
        n = int(sr * 1.0)
        data = []
        for i in range(n):
            t = i / sr
            env = _env_slow(1.0, i, n)
            v = _noise(t) * 0.05 + _sine(60 + 40 * (i / n), t) * 0.04
            data.append(max(-32768, min(32767, int(v * env * 32767))))
        buf = struct.pack(f"<{n}h", *data)
        _cache[name] = pygame.mixer.Sound(buffer=buf)
    elif name == "thunder":
        n = int(sr * 0.8)
        data = []
        for i in range(n):
            t = i / sr
            env = math.exp(-i / (sr * 0.15)) * 0.7
            f = 50 + random.random() * 80
            v = _saw(f, t) * 0.15 + _noise(t) * 0.2
            data.append(max(-32768, min(32767, int(v * env * 32767))))
        buf = struct.pack(f"<{n}h", *data)
        _cache[name] = pygame.mixer.Sound(buffer=buf)

def play(name):
    if name not in _cache:
        _build(name)
    _cache[name].play()
