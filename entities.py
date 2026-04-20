import pygame
import math
import random
from constants import *


# ────────────────────────────────────────────────────────────────────────────
# Tower
# ────────────────────────────────────────────────────────────────────────────
class Tower:
    """Represents the player's defensive structure.
    Attributes: Health, TowerImage (drawn as shape).
    Role: primary health pool – when Health reaches zero the run ends."""

    def __init__(self):
        self.x, self.y = TOWER_POS
        self.health = TOWER_STATS["hp"]
        self.max_health = TOWER_STATS["hp"]
        self.damage = TOWER_STATS["damage"]
        self.hit_speed = TOWER_STATS["hit_speed"]
        self.range = TOWER_STATS["range"]
        self.size = TOWER_SIZE
        self.attack_timer = 0.0
        self.alive = True
        self.target = None

    # ── Behaviour ───────────────────────────────────────────────────────────
    def take_damage(self, dmg):
        if not self.alive:
            return
        self.health -= dmg
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def _find_target(self, enemies):
        best = None
        best_dist = float("inf")
        for e in enemies:
            if not e.alive:
                continue
            d = math.hypot(e.x - self.x, e.y - self.y)
            if d < self.range and d < best_dist:
                best_dist = d
                best = e
        return best

    def update(self, dt, enemies):
        if not self.alive:
            return None
        self.target = self._find_target(enemies)
        if self.target is None:
            return None
        self.attack_timer -= dt
        if self.attack_timer <= 0:
            self.attack_timer = self.hit_speed
            return Projectile(self.x, self.y, self.target, self.damage, "player")
        return None

    # ── Drawing ─────────────────────────────────────────────────────────────
    def draw(self, surface):
        if not self.alive:
            rect = pygame.Rect(self.x - self.size // 2,
                               self.y - self.size // 2,
                               self.size, self.size)
            pygame.draw.rect(surface, DARK_GRAY, rect)
            pygame.draw.line(surface, GRAY, rect.topleft, rect.bottomright, 2)
            pygame.draw.line(surface, GRAY, rect.topright, rect.bottomleft, 2)
            return

        half = self.size // 2
        rect = pygame.Rect(self.x - half, self.y - half, self.size, self.size)
        pygame.draw.rect(surface, BLUE, rect)
        pygame.draw.rect(surface, LIGHT_BLUE, rect, 3)

        # Crown icon
        pts = [(self.x - 8, self.y - 5),
               (self.x, self.y - 16),
               (self.x + 8, self.y - 5)]
        pygame.draw.polygon(surface, YELLOW, pts)

        # HP bar
        bar_w = self.size
        bar_h = 5
        bx = self.x - half
        by = self.y - half - 8
        ratio = max(self.health / self.max_health, 0)
        pygame.draw.rect(surface, DARK_GRAY, (bx, by, bar_w, bar_h))
        pygame.draw.rect(surface, GREEN if ratio > 0.3 else RED,
                         (bx, by, int(bar_w * ratio), bar_h))


# ────────────────────────────────────────────────────────────────────────────
# Character
# ────────────────────────────────────────────────────────────────────────────
class Character:
    """Represents units on the board.
    Attributes: Name, Health, Speed, AttackType (melee/range/summon), Damage.
    Role: move along the stage and fight enemies."""

    def __init__(self, x, y, name, card_data, team):
        self.x = float(x)
        self.y = float(y)
        self.name = name
        self.team = team

        self.max_health = card_data["hp"]
        self.health = self.max_health
        self.speed = card_data["speed"]
        self.attack_type = card_data["attack_type"]   # melee or range or summonnnn
        self.damage = card_data["damage"]
        self.hit_speed = card_data["hit_speed"]
        self.attack_range = card_data["range"]
        self.splash_radius = card_data.get("splash_radius", 0)
        self.is_flying = card_data.get("is_flying", False)

        self.shape = card_data["shape"]
        self.base_colour = card_data["colour"]
        self.size = card_data["size"]

        self.alive = True
        self.attack_timer = 0.0
        self.target = None

        # Prince charge mechanic
        self.can_charge = "charge_speed" in card_data
        self.charge_speed = card_data.get("charge_speed", self.speed)
        self.charge_damage_mult = card_data.get("charge_damage_mult", 1.0)
        self.has_charged = False
        self.charging = False
        self.charge_dist_traveled = 0.0
        self.charge_threshold = 120

        # Summon mechanic (Witch)
        self.spawns = card_data.get("spawns", None)
        self.spawn_interval = card_data.get("spawn_interval", 0)
        self.spawn_count = card_data.get("spawn_count", 0)
        self.spawn_timer = self.spawn_interval

    @property
    def colour(self):
        r, g, b = self.base_colour
        if self.team == "enemy":
            return (min(r + 60, 255), max(g - 40, 0), max(b - 40, 0))
        return self.base_colour

    # ── Behaviour ───────────────────────────────────────────────────────────
    def take_damage(self, dmg):
        if not self.alive:
            return
        self.health -= dmg
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def find_target(self, enemy_characters, tower=None):
        best = None
        best_dist = float("inf")
        for e in enemy_characters:
            if not e.alive:
                continue
            d = math.hypot(e.x - self.x, e.y - self.y)
            if d < best_dist:
                best_dist = d
                best = e
        if tower and tower.alive:
            d = math.hypot(tower.x - self.x, tower.y - self.y)
            if d < best_dist:
                best_dist = d
                best = tower
        return best

    def _move_toward(self, tx, ty, dt):
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist < 1:
            return
        cur_speed = self.speed
        if self.can_charge and not self.has_charged:
            self.charge_dist_traveled += cur_speed * dt
            if self.charge_dist_traveled > self.charge_threshold:
                self.charging = True
                cur_speed = self.charge_speed
        nx = dx / dist * cur_speed * dt
        ny = dy / dist * cur_speed * dt
        if abs(nx) > abs(dx):
            nx = dx
        if abs(ny) > abs(dy):
            ny = dy
        self.x += nx
        self.y += ny

    def update(self, dt, enemy_characters, tower=None):
        """Returns (list[Projectile], list[spawn_dict])."""
        projectiles = []
        spawns = []
        if not self.alive:
            return projectiles, spawns

        self.target = self.find_target(enemy_characters, tower)
        if self.target is None:
            return projectiles, spawns

        dist = math.hypot(self.target.x - self.x, self.target.y - self.y)

        if dist <= self.attack_range:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attack_timer = self.hit_speed
                dmg = self.damage
                if self.can_charge and self.charging and not self.has_charged:
                    dmg = int(dmg * self.charge_damage_mult)
                    self.has_charged = True
                    self.charging = False
                projectiles.append(
                    Projectile(self.x, self.y, self.target, dmg, self.team,
                               splash=self.splash_radius))
        else:
            self._move_toward(self.target.x, self.target.y, dt)

        # Summon spawning (e.g. Witch)
        if self.spawns and self.alive:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.spawn_timer = self.spawn_interval
                for i in range(self.spawn_count):
                    angle = (2 * math.pi / self.spawn_count) * i
                    sx = self.x + math.cos(angle) * 20
                    sy = self.y + math.sin(angle) * 20
                    spawns.append({"name": self.spawns, "x": sx, "y": sy,
                                   "team": self.team})

        return projectiles, spawns

    # ── Drawing ─────────────────────────────────────────────────────────────
    def draw(self, surface):
        if not self.alive:
            return
        c = self.colour
        s = self.size
        ix, iy = int(self.x), int(self.y)

        if self.shape == "square":
            pygame.draw.rect(surface, c, (ix - s, iy - s, s * 2, s * 2))
            pygame.draw.rect(surface, BLACK, (ix - s, iy - s, s * 2, s * 2), 1)
        elif self.shape == "circle":
            pygame.draw.circle(surface, c, (ix, iy), s)
            pygame.draw.circle(surface, BLACK, (ix, iy), s, 1)
            if self.is_flying:
                pygame.draw.line(surface, WHITE,
                                 (ix - s - 4, iy - 3), (ix - s + 2, iy - 8), 2)
                pygame.draw.line(surface, WHITE,
                                 (ix + s + 4, iy - 3), (ix + s - 2, iy - 8), 2)
        elif self.shape == "triangle":
            pts = [(ix, iy - s), (ix - s, iy + s), (ix + s, iy + s)]
            pygame.draw.polygon(surface, c, pts)
            pygame.draw.polygon(surface, BLACK, pts, 1)
        elif self.shape == "diamond":
            pts = [(ix, iy - s), (ix + s, iy), (ix, iy + s), (ix - s, iy)]
            pygame.draw.polygon(surface, c, pts)
            pygame.draw.polygon(surface, BLACK, pts, 1)

        # Charge indicator
        if self.can_charge and self.charging:
            pygame.draw.circle(surface, YELLOW, (ix, iy - s - 6), 4)

        # HP bar (only if damaged)
        if self.health < self.max_health:
            bar_w = s * 2
            bar_h = 3
            bx = ix - s
            by = iy - s - 6
            ratio = max(self.health / self.max_health, 0)
            pygame.draw.rect(surface, DARK_GRAY, (bx, by, bar_w, bar_h))
            pygame.draw.rect(surface, GREEN if ratio > 0.3 else RED,
                             (bx, by, int(bar_w * ratio), bar_h))

        # Name label
        if not hasattr(Character, "_label_font"):
            Character._label_font = pygame.font.SysFont("arial", 11, bold=True)
        name_colour = LIGHT_BLUE if self.team == "player" else LIGHT_RED
        label = Character._label_font.render(self.name, True, name_colour)
        surface.blit(label, (ix - label.get_width() // 2, iy + s + 2))


# ────────────────────────────────────────────────────────────────────────────
# Card
# ────────────────────────────────────────────────────────────────────────────
class Card:
    """Represents playable deck items.
    Attributes: Name, CardImage (shape/colour), Cost, CharactersToBeSummoned.
    Role: deduct mana and spawn the corresponding Character(s)."""

    def __init__(self, name):
        data = CARDS[name]
        self.name = name
        self.cost = data["cost"]
        self.is_spell = data["is_spell"]
        self.characters_to_be_summoned = data["count"]
        self.card_data = data

    def can_play(self, mana_manager):
        return mana_manager.can_afford(self.cost)

    def play(self, mana_manager, x, y, team):
        """Deduct mana and return a list of Characters to place on the Stage."""
        if not mana_manager.can_afford(self.cost):
            return []
        mana_manager.spend(self.cost)

        if self.is_spell:
            return []   # spells handled separately by Stage

        characters = []
        count = self.characters_to_be_summoned
        for i in range(count):
            angle = (2 * math.pi / max(count, 1)) * i
            spread = min(10 + count * 3, 60) * (count > 1)
            sx = x + math.cos(angle) * spread + random.uniform(-8, 8)
            sy = y + math.sin(angle) * spread + random.uniform(-8, 8)
            sx = max(10, min(sx, WIDTH - 10))
            characters.append(Character(sx, sy, self.name, self.card_data, team))
        return characters


# ────────────────────────────────────────────────────────────────────────────
# ManaManager
# ────────────────────────────────────────────────────────────────────────────
class ManaManager:
    """Controls the player's economy.
    Attributes: CurrentMana, MaxMana, RegenRate.
    Role: regenerate mana over time and check if a Card can be afforded."""

    def __init__(self):
        self.current_mana = START_MANA
        self.max_mana = MAX_MANA
        self.regen_rate = MANA_REGEN_RATE

    def update(self, dt):
        self.regen_rate += 0.05 * dt
        self.current_mana = min(self.current_mana + self.regen_rate * dt,
                                self.max_mana)

    def can_afford(self, cost):
        return self.current_mana >= cost

    def spend(self, cost):
        self.current_mana -= cost


# ────────────────────────────────────────────────────────────────────────────
# Projectile  (helper – not a core proposal class)
# ────────────────────────────────────────────────────────────────────────────
class Projectile:
    SPEED = 400

    def __init__(self, x, y, target, damage, team, splash=0):
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.damage = damage
        self.team = team
        self.splash = splash
        self.alive = True
        self.radius = 4

    def update(self, dt, all_enemies):
        if not self.alive:
            return
        if not self.target.alive:
            self.alive = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist < 10:
            self._hit(all_enemies)
            return
        self.x += dx / dist * self.SPEED * dt
        self.y += dy / dist * self.SPEED * dt

    def _hit(self, all_enemies):
        self.alive = False
        if self.splash > 0:
            for e in all_enemies:
                if not e.alive:
                    continue
                if math.hypot(e.x - self.target.x,
                              e.y - self.target.y) <= self.splash:
                    e.take_damage(self.damage)
        else:
            self.target.take_damage(self.damage)

    def draw(self, surface):
        if not self.alive:
            return
        c = LIGHT_BLUE if self.team == "player" else LIGHT_RED
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)),
                           self.radius, 1)


# ────────────────────────────────────────────────────────────────────────────
# SpellEffect  (visual-only helper)
# ────────────────────────────────────────────────────────────────────────────
class SpellEffect:
    def __init__(self, x, y, radius, colour, duration=0.5):
        self.x = x
        self.y = y
        self.radius = radius
        self.colour = colour
        self.duration = duration
        self.timer = duration
        self.alive = True

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        alpha = max(self.timer / self.duration, 0)
        r = int(self.radius * (2 - alpha))
        c = tuple(min(int(v * alpha + 255 * (1 - alpha)), 255)
                  for v in self.colour)
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), r, 3)
