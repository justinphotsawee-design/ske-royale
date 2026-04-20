import pygame
import math
from constants import *


class Tower:
    def __init__(self, x, y, kind, team):
        """kind: 'king' or 'princess'   team: 'player' or 'enemy'"""
        self.x = x
        self.y = y
        self.kind = kind
        self.team = team
        stats = KING_TOWER_STATS if kind == "king" else PRINCESS_TOWER_STATS
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.damage = stats["damage"]
        self.hit_speed = stats["hit_speed"]
        self.range = stats["range"]
        self.size = KING_SIZE if kind == "king" else PRINCESS_SIZE
        self.attack_timer = 0.0
        self.alive = True
        self.activated = kind != "king"  # princess towers always active; king starts inactive
        self.target = None

    def activate(self):
        self.activated = True

    def take_damage(self, dmg):
        if not self.alive:
            return
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def _find_target(self, enemies):
        if not self.activated or not self.alive:
            return None
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

    def update(self, dt, enemy_troops):
        if not self.alive or not self.activated:
            return None  # returns projectile or None
        self.target = self._find_target(enemy_troops)
        if self.target is None:
            return None
        self.attack_timer -= dt
        if self.attack_timer <= 0:
            self.attack_timer = self.hit_speed
            return Projectile(self.x, self.y, self.target, self.damage, self.team)
        return None

    def draw(self, surface):
        if not self.alive:
            # draw rubble
            colour = (100, 100, 100)
            rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
            pygame.draw.rect(surface, colour, rect)
            pygame.draw.line(surface, DARK_GRAY, rect.topleft, rect.bottomright, 2)
            pygame.draw.line(surface, DARK_GRAY, rect.topright, rect.bottomleft, 2)
            return
        base = BLUE if self.team == "player" else RED
        lighter = LIGHT_BLUE if self.team == "player" else LIGHT_RED
        half = self.size // 2
        rect = pygame.Rect(self.x - half, self.y - half, self.size, self.size)
        pygame.draw.rect(surface, base, rect)
        pygame.draw.rect(surface, lighter, rect, 3)
        if self.kind == "king":
            # crown icon (small triangle on top)
            pts = [(self.x - 8, self.y - 5), (self.x, self.y - 16), (self.x + 8, self.y - 5)]
            pygame.draw.polygon(surface, YELLOW, pts)
        # HP bar
        bar_w = self.size
        bar_h = 5
        bx = self.x - half
        by = self.y - half - 8
        ratio = max(self.hp / self.max_hp, 0)
        pygame.draw.rect(surface, DARK_GRAY, (bx, by, bar_w, bar_h))
        pygame.draw.rect(surface, GREEN if ratio > 0.3 else RED, (bx, by, int(bar_w * ratio), bar_h))


class Troop:
    def __init__(self, x, y, card_name, card_data, team):
        self.x = float(x)
        self.y = float(y)
        self.card_name = card_name
        self.team = team
        self.max_hp = card_data["hp"]
        self.hp = self.max_hp
        self.damage = card_data["damage"]
        self.hit_speed = card_data["hit_speed"]
        self.speed = card_data["speed"]
        self.range = card_data["range"]
        self.target_type = card_data["target_type"]
        self.splash_radius = card_data.get("splash_radius", 0)
        self.is_flying = card_data.get("is_flying", False)
        self.shape = card_data["shape"]
        self.base_colour = card_data["colour"]
        self.size = card_data["size"]
        self.alive = True
        self.attack_timer = 0.0
        self.target = None

        # Prince charge
        self.can_charge = "charge_speed" in card_data
        self.charge_speed = card_data.get("charge_speed", self.speed)
        self.charge_damage_mult = card_data.get("charge_damage_mult", 1.0)
        self.has_charged = False  # first hit flag
        self.charging = False
        self.charge_dist_traveled = 0.0
        self.charge_threshold = 120  # px before full charge

        # Witch spawning
        self.spawns = card_data.get("spawns", None)
        self.spawn_interval = card_data.get("spawn_interval", 0)
        self.spawn_count = card_data.get("spawn_count", 0)
        self.spawn_timer = self.spawn_interval  # spawn after first interval

    @property
    def colour(self):
        """Tint colour based on team."""
        r, g, b = self.base_colour
        if self.team == "enemy":
            return (min(r + 60, 255), max(g - 40, 0), max(b - 40, 0))
        return self.base_colour

    def take_damage(self, dmg):
        if not self.alive:
            return
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def dist_to(self, other):
        return math.hypot(other.x - self.x, other.y - self.y)

    def find_target(self, enemy_troops, enemy_towers):
        best = None
        best_dist = float("inf")
        if self.target_type == "buildings":
            # only target towers
            for t in enemy_towers:
                if not t.alive:
                    continue
                d = math.hypot(t.x - self.x, t.y - self.y)
                if d < best_dist:
                    best_dist = d
                    best = t
        else:
            # target nearest enemy troop or tower
            for e in enemy_troops:
                if not e.alive:
                    continue
                d = math.hypot(e.x - self.x, e.y - self.y)
                if d < best_dist:
                    best_dist = d
                    best = e
            for t in enemy_towers:
                if not t.alive:
                    continue
                d = math.hypot(t.x - self.x, t.y - self.y)
                if d < best_dist:
                    best_dist = d
                    best = t
        return best

    def _needs_bridge(self, target):
        """Check if we need to cross the river to reach target."""
        if self.is_flying:
            return False
        my_side_top = self.y < RIVER_Y
        target_side_top = target.y < RIVER_Y + RIVER_H
        if my_side_top and not target_side_top:
            return True
        my_side_bot = self.y > RIVER_Y + RIVER_H
        target_side_bot = target.y > RIVER_Y
        if my_side_bot and not target_side_bot:
            return True
        return False

    def _nearest_bridge(self):
        dl = abs(self.x - (LEFT_BRIDGE_X + BRIDGE_W / 2))
        dr = abs(self.x - (RIGHT_BRIDGE_X + BRIDGE_W / 2))
        if dl < dr:
            return LEFT_BRIDGE_X + BRIDGE_W / 2, RIVER_Y + RIVER_H / 2
        return RIGHT_BRIDGE_X + BRIDGE_W / 2, RIVER_Y + RIVER_H / 2

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

    def update(self, dt, enemy_troops, enemy_towers):
        """Returns list of (Projectile | None) and list of spawned troop dicts."""
        projectiles = []
        spawns = []
        if not self.alive:
            return projectiles, spawns

        self.target = self.find_target(enemy_troops, enemy_towers)
        if self.target is None:
            return projectiles, spawns

        dist_to_target = math.hypot(self.target.x - self.x, self.target.y - self.y)

        if dist_to_target <= self.range:
            # In attack range – attack
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attack_timer = self.hit_speed
                dmg = self.damage
                if self.can_charge and self.charging and not self.has_charged:
                    dmg = int(dmg * self.charge_damage_mult)
                    self.has_charged = True
                    self.charging = False
                projectiles.append(Projectile(self.x, self.y, self.target, dmg, self.team,
                                              splash=self.splash_radius))
        else:
            # Move toward target, considering bridge crossing
            if self._needs_bridge(self.target):
                bx, by = self._nearest_bridge()
                if abs(self.y - by) > 10:
                    self._move_toward(bx, by, dt)
                else:
                    self._move_toward(self.target.x, self.target.y, dt)
            else:
                self._move_toward(self.target.x, self.target.y, dt)

        # Witch spawning
        if self.spawns and self.alive:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.spawn_timer = self.spawn_interval
                for i in range(self.spawn_count):
                    angle = (2 * math.pi / self.spawn_count) * i
                    sx = self.x + math.cos(angle) * 20
                    sy = self.y + math.sin(angle) * 20
                    spawns.append({"name": self.spawns, "x": sx, "y": sy, "team": self.team})

        return projectiles, spawns

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
                # small wing lines
                pygame.draw.line(surface, WHITE, (ix - s - 4, iy - 3), (ix - s + 2, iy - 8), 2)
                pygame.draw.line(surface, WHITE, (ix + s + 4, iy - 3), (ix + s - 2, iy - 8), 2)
        elif self.shape == "triangle":
            pts = [(ix, iy - s), (ix - s, iy + s), (ix + s, iy + s)]
            pygame.draw.polygon(surface, c, pts)
            pygame.draw.polygon(surface, BLACK, pts, 1)
        elif self.shape == "diamond":
            pts = [(ix, iy - s), (ix + s, iy), (ix, iy + s), (ix - s, iy)]
            pygame.draw.polygon(surface, c, pts)
            pygame.draw.polygon(surface, BLACK, pts, 1)

        # Charge indicator for prince
        if self.can_charge and self.charging:
            pygame.draw.circle(surface, YELLOW, (ix, iy - s - 6), 4)

        # HP bar (only if damaged)
        if self.hp < self.max_hp:
            bar_w = s * 2
            bar_h = 3
            bx = ix - s
            by = iy - s - 6
            ratio = max(self.hp / self.max_hp, 0)
            pygame.draw.rect(surface, DARK_GRAY, (bx, by, bar_w, bar_h))
            pygame.draw.rect(surface, GREEN if ratio > 0.3 else RED, (bx, by, int(bar_w * ratio), bar_h))

        # Name label
        if not hasattr(Troop, "_label_font"):
            Troop._label_font = pygame.font.SysFont("arial", 11, bold=True)
        name_colour = LIGHT_BLUE if self.team == "player" else LIGHT_RED
        label = Troop._label_font.render(self.card_name, True, name_colour)
        surface.blit(label, (ix - label.get_width() // 2, iy + s + 2))


class Projectile:
    SPEED = 400  # pixels per second

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
                if math.hypot(e.x - self.target.x, e.y - self.target.y) <= self.splash:
                    e.take_damage(self.damage)
                    if hasattr(e, "kind") and e.kind == "king":
                        e.activate()
        else:
            self.target.take_damage(self.damage)
            if hasattr(self.target, "kind") and self.target.kind == "king":
                self.target.activate()

    def draw(self, surface):
        if not self.alive:
            return
        c = LIGHT_BLUE if self.team == "player" else LIGHT_RED
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 1)


class SpellEffect:
    """Visual-only effect for spell impacts (fireball explosion, etc.)."""
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
        c = tuple(min(int(v * alpha + 255 * (1 - alpha)), 255) for v in self.colour)
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), r, 3)
