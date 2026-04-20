import os
import pygame

_SOUND_DIR = os.path.join(os.path.dirname(__file__), "gamesoundyay")

# Lazy-loaded sound effects and music paths
_sounds: dict[str, pygame.mixer.Sound] = {}
_initialized = False


def _init():
    global _initialized
    if _initialized:
        return
    _initialized = True
    pygame.mixer.init()
    for name in ("sword", "bow", "punch", "fireball", "victory", "lose"):
        path = os.path.join(_SOUND_DIR, f"{name}.mp3")
        if os.path.exists(path):
            _sounds[name] = pygame.mixer.Sound(path)
            _sounds[name].set_volume(0.5)


def play(name: str):
    """Play a short sound effect by key."""
    _init()
    snd = _sounds.get(name)
    if snd:
        snd.play()


def play_music(track: str, loops=-1, volume=0.35):
    """Start background music. track: 'menu' or 'ingame'."""
    _init()
    filemap = {"menu": "menutheme.mp3", "ingame": "ingame.mp3"}
    filename = filemap.get(track)
    if not filename:
        return
    path = os.path.join(_SOUND_DIR, filename)
    if not os.path.exists(path):
        return
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loops)


def stop_music():
    _init()
    pygame.mixer.music.fadeout(500)


# ── Card → attack sound mapping ────────────────────────────────────────────
# swing  = melee weapon users
# bow    = ranged attackers
# punch  = unarmed / fist melee
# fireball = spells
CARD_ATTACK_SOUND: dict[str, str] = {
    "Knight":         "sword",
    "Mini PEKKA":     "sword",
    "Valkyrie":       "sword",
    "Prince":         "sword",
    "Archers":        "bow",
    "Musketeer":      "bow",
    "Bomber":         "bow",
    "Witch":          "bow",
    "Baby Dragon":    "bow",
    "Giant":          "punch",
    "Hog Rider":      "punch",
    "Skeleton Army":  "punch",
    "Skeletons":      "punch",
    "Goblins":        "punch",
    "Fireball":       "fireball",
    "Goblin Barrel":  "fireball",
}


def play_attack(card_name: str):
    """Play the appropriate attack sound for a card/troop."""
    key = CARD_ATTACK_SOUND.get(card_name)
    if key:
        play(key)
