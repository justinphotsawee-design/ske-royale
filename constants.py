import pygame

# ── Window ──────────────────────────────────────────────────────────────────
WIDTH = 440
HEIGHT = 720
FPS = 60

# ── Colours ─────────────────────────────────────────────────────────────────
WHITE       = (255, 255, 255)
BLACK       = (0, 0, 0)
GRAY        = (180, 180, 180)
DARK_GRAY   = (100, 100, 100)
LIGHT_GRAY  = (220, 220, 220)

# Team colours
BLUE        = (70, 130, 230)
RED         = (220, 60, 60)
LIGHT_BLUE  = (140, 190, 255)
LIGHT_RED   = (255, 150, 150)

# UI colours
MANA_PURPLE    = (200, 60, 220)
MANA_BG        = (60, 20, 70)
GREEN          = (60, 200, 80)
DARK_GREEN     = (30, 120, 40)
YELLOW         = (240, 220, 60)
ORANGE         = (240, 160, 40)
BROWN          = (140, 100, 60)
DARK_BROWN     = (90, 60, 30)

# Arena colours
ARENA_GREEN    = (80, 160, 60)
ARENA_GREEN2   = (70, 145, 55)
PATH_GRAY      = (140, 140, 120)

# Card colours
CARD_BG        = (60, 50, 80)
CARD_BORDER    = (200, 180, 120)
CARD_SELECTED  = (255, 230, 100)

# ── Arena Layout (pixels) ──────────────────────────────────────────────────
TILE = 24
ARENA_TOP = 40
ARENA_BOTTOM = 590
ARENA_HEIGHT = ARENA_BOTTOM - ARENA_TOP   # 550 px

# ── Player Tower ───────────────────────────────────────────────────────────
TOWER_POS = (WIDTH // 2, 530)
TOWER_SIZE = 42
TOWER_STATS = {"hp": 5000, "damage": 80, "hit_speed": 1.0, "range": 144}

# ── 9-Grid Deployment Sections ─────────────────────────────────────────────
# Player deploys in a 3×3 grid on the lower part of the arena.
GRID_COLS = 3
GRID_ROWS = 3
GRID_LEFT = 24
GRID_RIGHT = WIDTH - 24
GRID_TOP = 300
GRID_BOTTOM = 500

GRID_SEC_W = (GRID_RIGHT - GRID_LEFT) // GRID_COLS   # ~132
GRID_SEC_H = (GRID_BOTTOM - GRID_TOP) // GRID_ROWS   # ~67

# ── Enemy spawn zone (top of arena) ───────────────────────────────────────
ENEMY_SPAWN_TOP = ARENA_TOP + 8
ENEMY_SPAWN_BOTTOM = ARENA_TOP + 80

# ── Mana ───────────────────────────────────────────────────────────────────
MAX_MANA = 10.0
START_MANA = 5.0
MANA_REGEN_RATE = 1.0 / 2.8    # mana per second

# ── UI Layout ──────────────────────────────────────────────────────────────
UI_TOP = ARENA_BOTTOM               # 590
UI_HEIGHT = HEIGHT - UI_TOP          # 130

MANA_BAR_Y = UI_TOP - 18
MANA_BAR_H = 18
MANA_BAR_X = 16
MANA_BAR_W = WIDTH - 32

CARD_W = 88
CARD_H = 112
CARD_Y = MANA_BAR_Y + MANA_BAR_H + 10
CARD_GAP = 8
CARD_START_X = (WIDTH - (4 * CARD_W + 3 * CARD_GAP)) // 2

# ── Speed constants (pixels per second) ────────────────────────────────────
SPEED_SLOW      = 30
SPEED_MEDIUM    = 60
SPEED_FAST      = 90
SPEED_VERY_FAST = 120

# ── Card Definitions ──────────────────────────────────────────────────────
# attack_type: "melee" | "range" | "summon"
# is_spell: True for instant-effect spells (no Character spawned)
# shape: "square", "circle", "triangle", "diamond"

CARDS = {
    "Knight": {
        "cost": 3, "hp": 670, "damage": 79, "hit_speed": 1.1,
        "speed": SPEED_MEDIUM, "range": 18, "attack_type": "melee",
        "splash_radius": 0, "count": 1, "is_spell": False,
        "shape": "square", "colour": (100, 150, 255), "size": 14,
        "description": "Sturdy melee fighter",
    },
    "Archers": {
        "cost": 3, "hp": 125, "damage": 50, "hit_speed": 1.2,
        "speed": SPEED_MEDIUM, "range": 150, "attack_type": "range",
        "splash_radius": 0, "count": 2, "is_spell": False,
        "shape": "triangle", "colour": (180, 100, 200), "size": 12,
        "description": "Pair of ranged attackers",
    },
    "Giant": {
        "cost": 5, "hp": 2000, "damage": 120, "hit_speed": 1.5,
        "speed": SPEED_SLOW, "range": 18, "attack_type": "melee",
        "splash_radius": 0, "count": 1, "is_spell": False,
        "shape": "circle", "colour": (180, 140, 80), "size": 20,
        "description": "Tanky melee fighter",
    },
    "Musketeer": {
        "cost": 4, "hp": 340, "damage": 100, "hit_speed": 1.1,
        "speed": SPEED_MEDIUM, "range": 180, "attack_type": "range",
        "splash_radius": 0, "count": 1, "is_spell": False,
        "shape": "triangle", "colour": (220, 180, 220), "size": 13,
        "description": "High-damage ranged shooter",
    },
    "Fireball": {
        "cost": 4, "hp": 0, "damage": 325, "hit_speed": 0,
        "speed": 0, "range": 0, "attack_type": "melee",
        "splash_radius": 60, "count": 0, "is_spell": True,
        "shape": "circle", "colour": (255, 140, 30), "size": 10,
        "description": "Area damage spell",
    },
    "Mini PEKKA": {
        "cost": 4, "hp": 600, "damage": 325, "hit_speed": 1.8,
        "speed": SPEED_FAST, "range": 18, "attack_type": "melee",
        "splash_radius": 0, "count": 1, "is_spell": False,
        "shape": "diamond", "colour": (60, 80, 180), "size": 14,
        "description": "High-damage melee glass cannon",
    },
    "Valkyrie": {
        "cost": 4, "hp": 880, "damage": 120, "hit_speed": 1.5,
        "speed": SPEED_MEDIUM, "range": 18, "attack_type": "melee",
        "splash_radius": 30, "count": 1, "is_spell": False,
        "shape": "circle", "colour": (240, 140, 50), "size": 15,
        "description": "Melee splash fighter",
    },
    "Hog Rider": {
        "cost": 4, "hp": 800, "damage": 150, "hit_speed": 1.5,
        "speed": SPEED_VERY_FAST, "range": 18, "attack_type": "melee",
        "splash_radius": 0, "count": 1, "is_spell": False,
        "shape": "diamond", "colour": (240, 200, 60), "size": 15,
        "description": "Fast melee charger",
    },
    "Witch": {
        "cost": 5, "hp": 440, "damage": 69, "hit_speed": 0.7,
        "speed": SPEED_MEDIUM, "range": 150, "attack_type": "summon",
        "splash_radius": 0, "count": 1, "is_spell": False,
        "shape": "circle", "colour": (160, 60, 200), "size": 14,
        "description": "Spawns skeletons, ranged",
        "spawns": "Skeletons",
        "spawn_interval": 7.0,
        "spawn_count": 3,
    },
    "Baby Dragon": {
        "cost": 4, "hp": 800, "damage": 100, "hit_speed": 1.8,
        "speed": SPEED_FAST, "range": 105, "attack_type": "range",
        "splash_radius": 25, "count": 1, "is_spell": False, "is_flying": True,
        "shape": "circle", "colour": (80, 200, 80), "size": 16,
        "description": "Flying splash damage",
    },
    "Prince": {
        "cost": 5, "hp": 1000, "damage": 245, "hit_speed": 1.4,
        "speed": SPEED_MEDIUM, "range": 18, "attack_type": "melee",
        "splash_radius": 0, "count": 1, "is_spell": False,
        "shape": "diamond", "colour": (100, 80, 200), "size": 16,
        "description": "Charges for double first hit",
        "charge_speed": SPEED_VERY_FAST,
        "charge_damage_mult": 2.0,
    },
    "Skeleton Army": {
        "cost": 3, "hp": 32, "damage": 32, "hit_speed": 1.0,
        "speed": SPEED_FAST, "range": 18, "attack_type": "melee",
        "splash_radius": 0, "count": 15, "is_spell": False,
        "shape": "square", "colour": (230, 230, 230), "size": 8,
        "description": "Swarm of fragile skeletons",
    },
    "Bomber": {
        "cost": 3, "hp": 200, "damage": 128, "hit_speed": 1.9,
        "speed": SPEED_MEDIUM, "range": 135, "attack_type": "range",
        "splash_radius": 30, "count": 1, "is_spell": False,
        "shape": "triangle", "colour": (255, 100, 50), "size": 12,
        "description": "Ranged splash attacker",
    },
    "Goblin Barrel": {
        "cost": 3, "hp": 0, "damage": 0, "hit_speed": 0,
        "speed": 0, "range": 0, "attack_type": "melee",
        "splash_radius": 0, "count": 0, "is_spell": True,
        "shape": "circle", "colour": (60, 200, 60), "size": 10,
        "description": "Throws goblins anywhere",
        "spawns_on_land": "Goblins",
        "spawn_land_count": 3,
    },
}

# Helper troop data (spawned by Witch / Goblin Barrel – not in deck)
SPAWNED_TROOPS = {
    "Skeletons": {
        "hp": 32, "damage": 32, "hit_speed": 1.0,
        "speed": SPEED_FAST, "range": 18, "attack_type": "melee",
        "splash_radius": 0,
        "shape": "square", "colour": (230, 230, 230), "size": 7,
    },
    "Goblins": {
        "hp": 80, "damage": 50, "hit_speed": 1.1,
        "speed": SPEED_VERY_FAST, "range": 18, "attack_type": "melee",
        "splash_radius": 0,
        "shape": "triangle", "colour": (80, 220, 80), "size": 9,
    },
}

ALL_CARD_NAMES = list(CARDS.keys())

DEFAULT_DECK = [
    "Knight", "Archers", "Giant", "Musketeer",
    "Fireball", "Mini PEKKA", "Valkyrie", "Hog Rider",
]

# ── Wave configuration ─────────────────────────────────────────────────────
WAVE_INTERVAL = 12.0              # seconds between waves
WAVE_BASE_ENEMIES = 3             # enemies in wave 1
WAVE_ENEMY_INCREMENT = 1          # extra enemies per wave
WAVE_HP_SCALE = 1.08              # HP multiplier per wave
WAVE_DMG_SCALE = 1.05             # damage multiplier per wave

# Enemy types for waves (name, spawn-weight)
WAVE_ENEMY_POOL = [
    ("Knight", 3),
    ("Archers", 2),
    ("Musketeer", 1),
    ("Mini PEKKA", 1),
    ("Bomber", 1),
    ("Valkyrie", 1),
]
