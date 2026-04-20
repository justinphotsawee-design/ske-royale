import pygame
import math
import random
from constants import *
from entities import Tower, Troop, Projectile, SpellEffect
import sounds


class Battle:
    """Manages a single Clash-Royale-style battle."""

    def __init__(self, player_deck):
        # ── Towers ──────────────────────────────────────────────────────────
        self.player_towers = [
            Tower(*PLAYER_KING_POS, "king", "player"),
            Tower(*PLAYER_LEFT_PRINCESS, "princess", "player"),
            Tower(*PLAYER_RIGHT_PRINCESS, "princess", "player"),
        ]
        self.enemy_towers = [
            Tower(*ENEMY_KING_POS, "king", "enemy"),
            Tower(*ENEMY_LEFT_PRINCESS, "princess", "enemy"),
            Tower(*ENEMY_RIGHT_PRINCESS, "princess", "enemy"),
        ]

        # ── Troops & projectiles ────────────────────────────────────────────
        self.player_troops: list[Troop] = []
        self.enemy_troops: list[Troop] = []
        self.projectiles: list[Projectile] = []
        self.effects: list[SpellEffect] = []

        # ── Elixir ──────────────────────────────────────────────────────────
        self.player_elixir = START_ELIXIR
        self.enemy_elixir = START_ELIXIR

        # ── Timer ───────────────────────────────────────────────────────────
        self.time_left = BATTLE_DURATION
        self.overtime = False
        self.overtime_timer = 0.0
        self.game_over = False
        self.winner = None  # "player" | "enemy" | "draw"

        # ── Card hand (player) ──────────────────────────────────────────────
        self.player_deck = list(player_deck)
        random.shuffle(self.player_deck)
        self.player_hand = self.player_deck[:4]
        self.player_queue = self.player_deck[4:]
        self.selected_card_index = None  # index in hand (0-3)

        # ── AI ──────────────────────────────────────────────────────────────
        self.ai = AI()

        # ── Fonts ───────────────────────────────────────────────────────────
        self.font = pygame.font.SysFont("arial", 18, bold=True)
        self.font_sm = pygame.font.SysFont("arial", 14)
        self.font_lg = pygame.font.SysFont("arial", 28, bold=True)
        self.font_xl = pygame.font.SysFont("arial", 40, bold=True)

    # ── Public interface ────────────────────────────────────────────────────
    def handle_event(self, event):
        if self.game_over:
            return "done" if event.type == pygame.MOUSEBUTTONDOWN else None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Check card click
            for i in range(4):
                rx = CARD_START_X + i * (CARD_W + CARD_GAP)
                ry = CARD_Y
                if rx <= mx <= rx + CARD_W and ry <= my <= ry + CARD_H:
                    if self.selected_card_index == i:
                        self.selected_card_index = None  # deselect
                    else:
                        self.selected_card_index = i
                    return None

            # Check arena click (deploy)
            if self.selected_card_index is not None and ARENA_TOP <= my <= ARENA_BOTTOM:
                self._try_deploy_player(mx, my)
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.selected_card_index = None
        return None

    def update(self, dt):
        if self.game_over:
            return

        # ── Timer ───────────────────────────────────────────────────────────
        if not self.overtime:
            self.time_left -= dt
            if self.time_left <= 0:
                self.time_left = 0
                self._check_end_regulation()
        else:
            self.overtime_timer -= dt
            if self.overtime_timer <= 0:
                self.overtime_timer = 0
                self._decide_winner()

        is_double = (not self.overtime and self.time_left <= DOUBLE_ELIXIR_TIME) or self.overtime
        rate = ELIXIR_RATE_DOUBLE if is_double else ELIXIR_RATE

        # ── Elixir ──────────────────────────────────────────────────────────
        self.player_elixir = min(self.player_elixir + rate * dt, MAX_ELIXIR)
        self.enemy_elixir = min(self.enemy_elixir + rate * dt, MAX_ELIXIR)

        # ── AI ──────────────────────────────────────────────────────────────
        self.ai.update(dt, self)

        # ── Towers attack ───────────────────────────────────────────────────
        for t in self.player_towers:
            p = t.update(dt, self.enemy_troops)
            if p:
                self.projectiles.append(p)
        for t in self.enemy_towers:
            p = t.update(dt, self.player_troops)
            if p:
                self.projectiles.append(p)

        # ── Troops ──────────────────────────────────────────────────────────
        all_enemy_entities = self.enemy_troops + self.enemy_towers
        all_player_entities = self.player_troops + self.player_towers

        for troop in self.player_troops:
            projs, spawns = troop.update(dt, self.enemy_troops, self.enemy_towers)
            if projs:
                sounds.play_attack(troop.card_name)
            self.projectiles.extend(projs)
            for s in spawns:
                self._spawn_helper(s)

        for troop in self.enemy_troops:
            projs, spawns = troop.update(dt, self.player_troops, self.player_towers)
            if projs:
                sounds.play_attack(troop.card_name)
            self.projectiles.extend(projs)
            for s in spawns:
                self._spawn_helper(s)

        # ── Projectiles ────────────────────────────────────────────────────
        for p in self.projectiles:
            targets = all_enemy_entities if p.team == "player" else all_player_entities
            p.update(dt, targets)

        # ── Effects ────────────────────────────────────────────────────────
        for e in self.effects:
            e.update(dt)

        # ── Cleanup dead ───────────────────────────────────────────────────
        self.player_troops = [t for t in self.player_troops if t.alive]
        self.enemy_troops = [t for t in self.enemy_troops if t.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.effects = [e for e in self.effects if e.alive]

        # ── Check king tower destruction ───────────────────────────────────
        if not self.player_towers[0].alive:
            self.game_over = True
            self.winner = "enemy"
            sounds.stop_music()
            sounds.play("lose")
        elif not self.enemy_towers[0].alive:
            self.game_over = True
            self.winner = "player"
            sounds.stop_music()
            sounds.play("victory")

        # ── Activate king if princess destroyed ────────────────────────────
        for side_towers in (self.player_towers, self.enemy_towers):
            king = side_towers[0]
            if king.alive and not king.activated:
                if not side_towers[1].alive or not side_towers[2].alive:
                    king.activate()

    def draw(self, surface):
        surface.fill(BLACK)
        self._draw_arena(surface)
        self._draw_towers(surface)
        self._draw_troops(surface)
        self._draw_projectiles(surface)
        self._draw_effects(surface)
        self._draw_ui(surface)
        self._draw_hud(surface)
        if self.game_over:
            self._draw_game_over(surface)

    # ── Deploy logic ────────────────────────────────────────────────────────
    def _try_deploy_player(self, mx, my):
        idx = self.selected_card_index
        if idx is None or idx >= len(self.player_hand):
            return
        card_name = self.player_hand[idx]
        card = CARDS[card_name]
        cost = card["cost"]
        if self.player_elixir < cost:
            return
        # Clamp to player deploy zone
        deploy_y = max(PLAYER_DEPLOY_TOP, min(my, PLAYER_DEPLOY_BOTTOM))
        deploy_x = max(20, min(mx, WIDTH - 20))
        # For spells, allow placing anywhere on arena
        if card["is_spell"]:
            deploy_y = max(ARENA_TOP + 20, min(my, ARENA_BOTTOM - 20))

        self.player_elixir -= cost
        self._deploy_card(card_name, card, deploy_x, deploy_y, "player")
        # Cycle hand
        self.player_hand[idx] = self.player_queue.pop(0)
        self.player_queue.append(card_name)
        self.selected_card_index = None

    def _deploy_card(self, card_name, card, x, y, team):
        if card["is_spell"]:
            self._apply_spell(card_name, card, x, y, team)
        else:
            count = card["count"]
            for i in range(count):
                # Spread multiple units — larger spread for swarms
                angle = (2 * math.pi / max(count, 1)) * i
                spread = min(10 + count * 3, 60) * (count > 1)
                sx = x + math.cos(angle) * spread + random.uniform(-8, 8)
                sy = y + math.sin(angle) * spread + random.uniform(-8, 8)
                sx = max(10, min(sx, WIDTH - 10))
                troop = Troop(sx, sy, card_name, card, team)
                if team == "player":
                    self.player_troops.append(troop)
                else:
                    self.enemy_troops.append(troop)

    def _apply_spell(self, card_name, card, x, y, team):
        if card_name == "Fireball":
            # Area damage
            enemies = self.enemy_troops + self.enemy_towers if team == "player" \
                else self.player_troops + self.player_towers
            for e in enemies:
                if not e.alive:
                    continue
                if math.hypot(e.x - x, e.y - y) <= card["splash_radius"]:
                    e.take_damage(card["damage"])
                    if hasattr(e, "kind") and e.kind == "king":
                        e.activate()
            self.effects.append(SpellEffect(x, y, card["splash_radius"], (255, 140, 30)))
            sounds.play("fireball")

        elif card_name == "Goblin Barrel":
            # Spawn goblins at target
            goblin_data = SPAWNED_TROOPS["Goblins"]
            for i in range(3):
                angle = (2 * math.pi / 3) * i
                gx = x + math.cos(angle) * 18
                gy = y + math.sin(angle) * 18
                g = Troop(gx, gy, "Goblins", goblin_data, team)
                if team == "player":
                    self.player_troops.append(g)
                else:
                    self.enemy_troops.append(g)
            self.effects.append(SpellEffect(x, y, 30, (60, 200, 60)))
            sounds.play("fireball")

    def _spawn_helper(self, spawn_dict):
        data = SPAWNED_TROOPS.get(spawn_dict["name"])
        if data is None:
            return
        t = Troop(spawn_dict["x"], spawn_dict["y"], spawn_dict["name"], data, spawn_dict["team"])
        if spawn_dict["team"] == "player":
            self.player_troops.append(t)
        else:
            self.enemy_troops.append(t)

    # ── Win condition helpers ───────────────────────────────────────────────
    def _check_end_regulation(self):
        p_crowns = sum(1 for t in self.enemy_towers if not t.alive)
        e_crowns = sum(1 for t in self.player_towers if not t.alive)
        if p_crowns != e_crowns:
            self._decide_winner()
            self._play_end_sound()
        else:
            # Tied → overtime
            self.overtime = True
            self.overtime_timer = OVERTIME_DURATION
            self.time_left = OVERTIME_DURATION

    def _decide_winner(self):
        self.game_over = True
        p_crowns = sum(1 for t in self.enemy_towers if not t.alive)
        e_crowns = sum(1 for t in self.player_towers if not t.alive)
        if p_crowns > e_crowns:
            self.winner = "player"
        elif e_crowns > p_crowns:
            self.winner = "enemy"
        else:
            # Compare total tower HP
            p_hp = sum(t.hp for t in self.player_towers if t.alive)
            e_hp = sum(t.hp for t in self.enemy_towers if t.alive)
            if p_hp > e_hp:
                self.winner = "player"
            elif e_hp > p_hp:
                self.winner = "enemy"
            else:
                self.winner = "draw"
        self._play_end_sound()

    def _play_end_sound(self):
        sounds.stop_music()
        if self.winner == "player":
            sounds.play("victory")
        else:
            sounds.play("lose")

    # ── Drawing helpers ─────────────────────────────────────────────────────
    def _draw_arena(self, surface):
        # Green field
        pygame.draw.rect(surface, ARENA_GREEN,
                         (0, ARENA_TOP, WIDTH, ARENA_HEIGHT))
        # Checkerboard
        for row in range(ARENA_HEIGHT // TILE):
            for col in range(WIDTH // TILE):
                if (row + col) % 2 == 0:
                    pygame.draw.rect(surface, ARENA_GREEN2,
                                     (col * TILE, ARENA_TOP + row * TILE, TILE, TILE))

        # River
        pygame.draw.rect(surface, RIVER_BLUE, (0, RIVER_Y, WIDTH, RIVER_H))
        # River wave lines
        for i in range(0, WIDTH, 20):
            pygame.draw.arc(surface, (80, 170, 240),
                            (i, RIVER_Y + 5, 20, 20), 0, math.pi, 2)

        # Bridges
        for bx in (LEFT_BRIDGE_X, RIGHT_BRIDGE_X):
            pygame.draw.rect(surface, BRIDGE_BROWN,
                             (bx, RIVER_Y - 2, BRIDGE_W, RIVER_H + 4))
            pygame.draw.rect(surface, DARK_BROWN,
                             (bx, RIVER_Y - 2, BRIDGE_W, RIVER_H + 4), 2)
            # Planks
            for j in range(0, BRIDGE_W, 15):
                pygame.draw.line(surface, DARK_BROWN,
                                 (bx + j, RIVER_Y - 2), (bx + j, RIVER_Y + RIVER_H + 2), 1)

        # Side boundaries
        pygame.draw.line(surface, DARK_GRAY, (0, ARENA_TOP), (WIDTH, ARENA_TOP), 2)
        pygame.draw.line(surface, DARK_GRAY, (0, ARENA_BOTTOM), (WIDTH, ARENA_BOTTOM), 2)

    def _draw_towers(self, surface):
        for t in self.player_towers + self.enemy_towers:
            t.draw(surface)

    def _draw_troops(self, surface):
        for t in self.player_troops + self.enemy_troops:
            t.draw(surface)

    def _draw_projectiles(self, surface):
        for p in self.projectiles:
            p.draw(surface)

    def _draw_effects(self, surface):
        for e in self.effects:
            e.draw(surface)

    def _draw_hud(self, surface):
        # Top bar
        pygame.draw.rect(surface, (30, 30, 50), (0, 0, WIDTH, ARENA_TOP))
        # Timer
        minutes = int(self.time_left) // 60
        seconds = int(self.time_left) % 60
        timer_str = f"{minutes}:{seconds:02d}"
        txt = self.font_lg.render(timer_str, True, WHITE)
        surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 8))
        # Crowns
        p_crowns = sum(1 for t in self.enemy_towers if not t.alive)
        e_crowns = sum(1 for t in self.player_towers if not t.alive)
        crown_p = self.font.render(f"★ {p_crowns}", True, LIGHT_BLUE)
        crown_e = self.font.render(f"★ {e_crowns}", True, LIGHT_RED)
        surface.blit(crown_p, (20, 14))
        surface.blit(crown_e, (WIDTH - 60, 14))
        # Double elixir warning
        if not self.overtime and self.time_left <= DOUBLE_ELIXIR_TIME:
            de = self.font_sm.render("DOUBLE ELIXIR", True, ELIXIR_PURPLE)
            surface.blit(de, (WIDTH // 2 - de.get_width() // 2, 36))
        elif self.overtime:
            de = self.font_sm.render("OVERTIME!", True, YELLOW)
            surface.blit(de, (WIDTH // 2 - de.get_width() // 2, 36))

    def _draw_ui(self, surface):
        # Background
        pygame.draw.rect(surface, (30, 25, 45), (0, UI_TOP, WIDTH, UI_HEIGHT))

        # Elixir bar
        pygame.draw.rect(surface, ELIXIR_BG,
                         (ELIXIR_BAR_X, ELIXIR_BAR_Y, ELIXIR_BAR_W, ELIXIR_BAR_H), border_radius=4)
        fill_w = int(ELIXIR_BAR_W * self.player_elixir / MAX_ELIXIR)
        pygame.draw.rect(surface, ELIXIR_PURPLE,
                         (ELIXIR_BAR_X, ELIXIR_BAR_Y, fill_w, ELIXIR_BAR_H), border_radius=4)
        elixir_txt = self.font.render(f"{int(self.player_elixir)}", True, WHITE)
        surface.blit(elixir_txt,
                     (ELIXIR_BAR_X + ELIXIR_BAR_W // 2 - elixir_txt.get_width() // 2,
                      ELIXIR_BAR_Y + 1))

        # Cards
        for i in range(4):
            if i >= len(self.player_hand):
                break
            card_name = self.player_hand[i]
            card = CARDS[card_name]
            rx = CARD_START_X + i * (CARD_W + CARD_GAP)
            ry = CARD_Y
            selected = (i == self.selected_card_index)
            affordable = self.player_elixir >= card["cost"]
            self._draw_card(surface, card_name, card, rx, ry, selected, affordable)

        # Next card preview
        if self.player_queue:
            next_name = self.player_queue[0]
            nx_card = CARDS.get(next_name)
            if nx_card:
                ntxt = self.font_sm.render(f"Next: {next_name} ({nx_card['cost']})", True, GRAY)
                surface.blit(ntxt, (CARD_START_X, CARD_Y + CARD_H + 4))

    def _draw_card(self, surface, name, card, x, y, selected, affordable):
        # Card background
        bg = CARD_BG if not selected else (80, 70, 40)
        border = CARD_SELECTED if selected else (CARD_BORDER if affordable else DARK_GRAY)
        pygame.draw.rect(surface, bg, (x, y, CARD_W, CARD_H), border_radius=6)
        pygame.draw.rect(surface, border, (x, y, CARD_W, CARD_H), 2, border_radius=6)

        if not affordable and not selected:
            # Dim overlay
            dim = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 100))
            surface.blit(dim, (x, y))

        # Troop shape icon
        cx = x + CARD_W // 2
        cy = y + 50
        s = card["size"] + 4
        c = card["colour"]
        if card["shape"] == "square":
            pygame.draw.rect(surface, c, (cx - s, cy - s, s * 2, s * 2))
        elif card["shape"] == "circle":
            pygame.draw.circle(surface, c, (cx, cy), s)
        elif card["shape"] == "triangle":
            pygame.draw.polygon(surface, c, [(cx, cy - s), (cx - s, cy + s), (cx + s, cy + s)])
        elif card["shape"] == "diamond":
            pygame.draw.polygon(surface, c, [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)])

        # Elixir cost (top-left circle)
        pygame.draw.circle(surface, ELIXIR_PURPLE, (x + 14, y + 14), 12)
        cost_txt = self.font_sm.render(str(card["cost"]), True, WHITE)
        surface.blit(cost_txt, (x + 14 - cost_txt.get_width() // 2,
                                y + 14 - cost_txt.get_height() // 2))

        # Name
        ntxt = self.font_sm.render(name, True, WHITE)
        surface.blit(ntxt, (x + CARD_W // 2 - ntxt.get_width() // 2, y + CARD_H - 28))

    def _draw_game_over(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        if self.winner == "player":
            text = "VICTORY!"
            colour = YELLOW
        elif self.winner == "enemy":
            text = "DEFEAT"
            colour = RED
        else:
            text = "DRAW"
            colour = GRAY

        txt = self.font_xl.render(text, True, colour)
        surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 60))

        p_crowns = sum(1 for t in self.enemy_towers if not t.alive)
        e_crowns = sum(1 for t in self.player_towers if not t.alive)
        score = self.font_lg.render(f"{p_crowns} - {e_crowns}", True, WHITE)
        surface.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2))

        hint = self.font.render("Click to return", True, GRAY)
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 50))


class AI:
    """Simple enemy AI that plays cards on a timer."""

    def __init__(self):
        deck = list(DEFAULT_DECK)
        random.shuffle(deck)
        self.hand = deck[:4]
        self.queue = deck[4:]
        self.think_timer = random.uniform(2.0, 4.0)

    def update(self, dt, battle: Battle):
        self.think_timer -= dt
        if self.think_timer > 0:
            return
        self.think_timer = random.uniform(1.5, 4.0)

        # Pick affordable cards
        affordable = [(i, CARDS[name]) for i, name in enumerate(self.hand)
                      if CARDS[name]["cost"] <= battle.enemy_elixir]
        if not affordable:
            return

        # Play the most expensive affordable card (simple heuristic)
        affordable.sort(key=lambda x: x[1]["cost"], reverse=True)
        idx, card = affordable[0]
        card_name = self.hand[idx]

        battle.enemy_elixir -= card["cost"]

        # Decide placement
        x, y = self._choose_position(card, battle)
        battle._deploy_card(card_name, card, x, y, "enemy")

        # Cycle hand
        self.hand[idx] = self.queue.pop(0)
        self.queue.append(card_name)

    def _choose_position(self, card, battle):
        # Spells: target cluster of player troops near a princess tower
        if card["is_spell"]:
            if battle.player_troops:
                t = random.choice(battle.player_troops)
                return t.x, t.y
            # Aim at a player tower
            alive_towers = [t for t in battle.player_towers if t.alive]
            if alive_towers:
                t = random.choice(alive_towers)
                return t.x, t.y
            return WIDTH // 2, 600

        # Building targeters: deploy at bridge
        if card["target_type"] == "buildings":
            bx = random.choice([LEFT_BRIDGE_X + BRIDGE_W // 2,
                                RIGHT_BRIDGE_X + BRIDGE_W // 2])
            return bx, ENEMY_DEPLOY_BOTTOM - 20

        # Regular troops: deploy behind towers or at bridge
        if random.random() < 0.5:
            # Behind king tower (defensive/build push)
            return WIDTH // 2 + random.randint(-60, 60), ENEMY_DEPLOY_TOP + 30
        else:
            # At bridge (aggressive)
            bx = random.choice([LEFT_BRIDGE_X + BRIDGE_W // 2,
                                RIGHT_BRIDGE_X + BRIDGE_W // 2])
            return bx + random.randint(-20, 20), ENEMY_DEPLOY_BOTTOM - 30
