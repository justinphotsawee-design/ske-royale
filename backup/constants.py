import pygame

# ── Window ──────────────────────────────────────────────────────────────────
WIDTH = 540
HEIGHT = 960
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
ELIXIR_PURPLE  = (200, 60, 220)
ELIXIR_BG      = (60, 20, 70)
GREEN          = (60, 200, 80)
DARK_GREEN     = (30, 120, 40)
YELLOW         = (240, 220, 60)
ORANGE         = (240, 160, 40)
BROWN          = (140, 100, 60)
DARK_BROWN     = (90, 60, 30)

# Arena colours
ARENA_GREEN    = (80, 160, 60)
ARENA_GREEN2   = (70, 145, 55)
RIVER_BLUE     = (60, 140, 220)
BRIDGE_BROWN   = (160, 120, 70)
PATH_GRAY      = (140, 140, 120)

# Card colours (by elixir cost range)
CARD_BG        = (60, 50, 80)
CARD_BORDER    = (200, 180, 120)
CARD_SELECTED  = (255, 230, 100)

# ── Arena Layout (pixels) ──────────────────────────────────────────────────
TILE = 30                           # logical tile = 30 px  →  18 tiles across
ARENA_TOP = 50
ARENA_BOTTOM = 770
ARENA_HEIGHT = ARENA_BOTTOM - ARENA_TOP   # 720 px = 24 tiles
ARENA_MID_Y = ARENA_TOP + ARENA_HEIGHT // 2   # 410

RIVER_Y = ARENA_MID_Y - 15         # 395
RIVER_H = 30                       # river band 395-425

# Bridges
LEFT_BRIDGE_X  = 75
RIGHT_BRIDGE_X = 405
BRIDGE_W = 90
BRIDGE_H = RIVER_H

# ── Tower Positions (centre) ──────────────────────────────────────────────
KING_SIZE = 52
PRINCESS_SIZE = 40

PLAYER_KING_POS       = (WIDTH // 2, 720)
PLAYER_LEFT_PRINCESS  = (110, 620)
PLAYER_RIGHT_PRINCESS = (430, 620)

ENEMY_KING_POS        = (WIDTH // 2, 100)
ENEMY_LEFT_PRINCESS   = (110, 200)
ENEMY_RIGHT_PRINCESS  = (430, 200)

# Tower stats                       HP    DMG  HIT_SPD  RANGE(px)
KING_TOWER_STATS    = {"hp": 2400, "damage": 100, "hit_speed": 1.0, "range": 210}
PRINCESS_TOWER_STATS = {"hp": 1400, "damage":  55, "hit_speed": 0.8, "range": 225}

# ── Deployment zones ───────────────────────────────────────────────────────
PLAYER_DEPLOY_TOP    = RIVER_Y + RIVER_H   # 425
PLAYER_DEPLOY_BOTTOM = ARENA_BOTTOM - 30   # 740
ENEMY_DEPLOY_TOP     = ARENA_TOP + 30      # 80
ENEMY_DEPLOY_BOTTOM  = RIVER_Y             # 395

# ── Elixir ─────────────────────────────────────────────────────────────────
MAX_ELIXIR = 10.0
START_ELIXIR = 5.0
ELIXIR_RATE = 1.0 / 2.8            # elixir per second (normal)
ELIXIR_RATE_DOUBLE = 1.0 / 1.4     # elixir per second (double time)

# ── Battle timer ───────────────────────────────────────────────────────────
BATTLE_DURATION = 180               # 3 minutes
DOUBLE_ELIXIR_TIME = 60             # last 60 seconds = double elixir
OVERTIME_DURATION = 60              # 1 minute overtime if tied

# ── UI Layout ──────────────────────────────────────────────────────────────
UI_TOP = ARENA_BOTTOM               # 770
UI_HEIGHT = HEIGHT - UI_TOP          # 190

ELIXIR_BAR_Y = UI_TOP + 8
ELIXIR_BAR_H = 22
ELIXIR_BAR_X = 20
ELIXIR_BAR_W = WIDTH - 40

CARD_W = 110
CARD_H = 140
CARD_Y = ELIXIR_BAR_Y + ELIXIR_BAR_H + 12
CARD_GAP = 10
CARD_START_X = (WIDTH - (4 * CARD_W + 3 * CARD_GAP)) // 2   # centred

# ── Speed constants (pixels per second) ────────────────────────────────────
SPEED_SLOW      = 30
SPEED_MEDIUM    = 60
SPEED_FAST      = 90
SPEED_VERY_FAST = 120

# ── Card Definitions ──────────────────────────────────────────────────────
# shape: "square", "circle", "triangle", "diamond"
# target_type: "all" (nearest troop/tower) | "buildings" (towers only)
# is_spell: True for spells (no troop spawned; instant effect)
# is_flying: True = ignores river, can attack/be attacked by air-targeting only
# splash_radius: >0 means area damage around target
# count: how many units to spawn

CARDS = {
    "Knight": {
        "cost": 3, "hp": 670, "damage": 79, "hit_speed": 1.1,
        "speed": SPEED_MEDIUM, "range": 18, "target_type": "all",
        "splash_radius": 0, "count": 1, "is_spell": False, "is_flying": False,
        "shape": "square", "colour": (100, 150, 255), "size": 14,
        "description": "Sturdy melee fighter",
    },
    "Archers": {
        "cost": 3, "hp": 125, "damage": 50, "hit_speed": 1.2,
        "speed": SPEED_MEDIUM, "range": 150, "target_type": "all",
        "splash_radius": 0, "count": 2, "is_spell": False, "is_flying": False,
        "shape": "triangle", "colour": (180, 100, 200), "size": 12,
        "description": "Pair of ranged attackers",
    },
    "Giant": {
        "cost": 5, "hp": 2000, "damage": 120, "hit_speed": 1.5,
        "speed": SPEED_SLOW, "range": 18, "target_type": "buildings",
        "splash_radius": 0, "count": 1, "is_spell": False, "is_flying": False,
        "shape": "circle", "colour": (180, 140, 80), "size": 20,
        "description": "Tanky building targeter",
    },
    "Musketeer": {
        "cost": 4, "hp": 340, "damage": 100, "hit_speed": 1.1,
        "speed": SPEED_MEDIUM, "range": 180, "target_type": "all",
        "splash_radius": 0, "count": 1, "is_spell": False, "is_flying": False,
        "shape": "triangle", "colour": (220, 180, 220), "size": 13,
        "description": "High-damage ranged shooter",
    },
    "Fireball": {
        "cost": 4, "hp": 0, "damage": 325, "hit_speed": 0,
        "speed": 0, "range": 0, "target_type": "all",
        "splash_radius": 60, "count": 0, "is_spell": True, "is_flying": False,
        "shape": "circle", "colour": (255, 140, 30), "size": 10,
        "description": "Area damage spell",
    },
    "Mini PEKKA": {
        "cost": 4, "hp": 600, "damage": 325, "hit_speed": 1.8,
        "speed": SPEED_FAST, "range": 18, "target_type": "all",
        "splash_radius": 0, "count": 1, "is_spell": False, "is_flying": False,
        "shape": "diamond", "colour": (60, 80, 180), "size": 14,
        "description": "High-damage melee glass cannon",
    },
    "Valkyrie": {
        "cost": 4, "hp": 880, "damage": 120, "hit_speed": 1.5,
        "speed": SPEED_MEDIUM, "range": 18, "target_type": "all",
        "splash_radius": 30, "count": 1, "is_spell": False, "is_flying": False,
        "shape": "circle", "colour": (240, 140, 50), "size": 15,
        "description": "Melee splash fighter",
    },
    "Hog Rider": {
        "cost": 4, "hp": 800, "damage": 150, "hit_speed": 1.5,
        "speed": SPEED_VERY_FAST, "range": 18, "target_type": "buildings",
        "splash_radius": 0, "count": 1, "is_spell": False, "is_flying": False,
        "shape": "diamond", "colour": (240, 200, 60), "size": 15,
        "description": "Fast building targeter",
    },
    "Witch": {
        "cost": 5, "hp": 440, "damage": 69, "hit_speed": 0.7,
        "speed": SPEED_MEDIUM, "range": 150, "target_type": "all",
        "splash_radius": 0, "count": 1, "is_spell": False, "is_flying": False,
        "shape": "circle", "colour": (160, 60, 200), "size": 14,
        "description": "Spawns skeletons, ranged",
        "spawns": "Skeletons",
        "spawn_interval": 7.0,
        "spawn_count": 3,
    },
    "Baby Dragon": {
        "cost": 4, "hp": 800, "damage": 100, "hit_speed": 1.8,
        "speed": SPEED_FAST, "range": 105, "target_type": "all",
        "splash_radius": 25, "count": 1, "is_spell": False, "is_flying": True,
        "shape": "circle", "colour": (80, 200, 80), "size": 16,
        "description": "Flying splash damage",
    },
    "Prince": {
        "cost": 5, "hp": 1000, "damage": 245, "hit_speed": 1.4,
        "speed": SPEED_MEDIUM, "range": 18, "target_type": "all",
        "splash_radius": 0, "count": 1, "is_spell": False, "is_flying": False,
        "shape": "diamond", "colour": (100, 80, 200), "size": 16,
        "description": "Charges for double first hit",
        "charge_speed": SPEED_VERY_FAST,
        "charge_damage_mult": 2.0,
    },
    "Skeleton Army": {
        "cost": 3, "hp": 32, "damage": 32, "hit_speed": 1.0,
        "speed": SPEED_FAST, "range": 18, "target_type": "all",
        "splash_radius": 0, "count": 15, "is_spell": False, "is_flying": False,
        "shape": "square", "colour": (230, 230, 230), "size": 8,
        "description": "Swarm of fragile skeletons",
    },
    "Bomber": {
        "cost": 3, "hp": 200, "damage": 128, "hit_speed": 1.9,
        "speed": SPEED_MEDIUM, "range": 135, "target_type": "all",
        "splash_radius": 30, "count": 1, "is_spell": False, "is_flying": False,
        "shape": "triangle", "colour": (255, 100, 50), "size": 12,
        "description": "Ranged splash attacker",
    },
    "Goblin Barrel": {
        "cost": 3, "hp": 0, "damage": 0, "hit_speed": 0,
        "speed": 0, "range": 0, "target_type": "all",
        "splash_radius": 0, "count": 0, "is_spell": True, "is_flying": False,
        "shape": "circle", "colour": (60, 200, 60), "size": 10,
        "description": "Throws goblins anywhere",
        "spawns_on_land": "Goblins",
        "spawn_land_count": 3,
    },
}

# Hidden helper troop data (spawned by Witch / Goblin Barrel, not in deck)
SPAWNED_TROOPS = {
    "Skeletons": {
        "hp": 32, "damage": 32, "hit_speed": 1.0,
        "speed": SPEED_FAST, "range": 18, "target_type": "all",
        "splash_radius": 0, "is_flying": False,
        "shape": "square", "colour": (230, 230, 230), "size": 7,
    },
    "Goblins": {
        "hp": 80, "damage": 50, "hit_speed": 1.1,
        "speed": SPEED_VERY_FAST, "range": 18, "target_type": "all",
        "splash_radius": 0, "is_flying": False,
        "shape": "triangle", "colour": (80, 220, 80), "size": 9,
    },
}

ALL_CARD_NAMES = list(CARDS.keys())

DEFAULT_DECK = [
    "Knight", "Archers", "Giant", "Musketeer",
    "Fireball", "Mini PEKKA", "Valkyrie", "Hog Rider",
]
