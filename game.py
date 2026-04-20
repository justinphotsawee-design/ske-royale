import pygame
import math
import random
import csv
import os
from constants import *
from entities import Tower, Character, Card, ManaManager, Projectile, SpellEffect
import sounds


class Stage:
    """Represents the game board and wave logic.
    Attributes: GridSections (9 map sections), ActiveEntities, WaveNumber.
    Role: handle coordinate positioning, spawn infinite enemy waves,
          and trigger the end-screen summary."""

    def __init__(self, player_deck):
        # ── Grid ────────────────────────────────────────────────────────────
        self.grid_sections = []
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = GRID_LEFT + col * GRID_SEC_W
                y = GRID_TOP + row * GRID_SEC_H
                self.grid_sections.append(pygame.Rect(x, y, GRID_SEC_W, GRID_SEC_H))

        # ── Tower ───────────────────────────────────────────────────────────
        self.tower = Tower()

        # ── Active Entities ─────────────────────────────────────────────────
        self.player_characters: list[Character] = []
        self.enemy_characters: list[Character] = []
        self.projectiles: list[Projectile] = []
        self.effects: list[SpellEffect] = []

        # ── Mana ────────────────────────────────────────────────────────────
        self.mana = ManaManager()

        # ── Wave logic ──────────────────────────────────────────────────────
        self.wave_number = 0
        self.wave_timer = 3.0   # first wave after 3 seconds

        # ── Card hand ───────────────────────────────────────────────────────
        self.deck_cards = [Card(name) for name in player_deck]
        random.shuffle(self.deck_cards)
        self.hand = self.deck_cards[:4]
        self.queue = self.deck_cards[4:]
        self.selected_card_index = None

        # ── Game state ──────────────────────────────────────────────────────
        self.game_over = False
        self.elapsed_time = 0.0

        # ── Stats tracking ──────────────────────────────────────────────────
        self.total_damage_dealt = 0
        self.total_cards_played = 0
        self.total_mana_used = 0.0
        self.stats_log = []

        # ── Fonts ───────────────────────────────────────────────────────────
        self.font = pygame.font.SysFont("arial", 18, bold=True)
        self.font_sm = pygame.font.SysFont("arial", 14)
        self.font_lg = pygame.font.SysFont("arial", 28, bold=True)
        self.font_xl = pygame.font.SysFont("arial", 40, bold=True)

    # ════════════════════════════════════════════════════════════════════════
    #  Public interface
    # ════════════════════════════════════════════════════════════════════════
    def handle_event(self, event):
        if self.game_over:
            return "done" if event.type == pygame.MOUSEBUTTONDOWN else None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Card selection
            for i in range(4):
                rx = CARD_START_X + i * (CARD_W + CARD_GAP)
                ry = CARD_Y
                if rx <= mx <= rx + CARD_W and ry <= my <= ry + CARD_H:
                    self.selected_card_index = (
                        None if self.selected_card_index == i else i)
                    return None

            # Deploy in grid or spell anywhere on arena
            if self.selected_card_index is not None:
                card = self.hand[self.selected_card_index]
                grid_idx = self._get_grid_section(mx, my)
                if grid_idx is not None:
                    self._try_deploy(mx, my, grid_idx)
                elif card.is_spell and ARENA_TOP <= my <= ARENA_BOTTOM:
                    self._try_deploy(mx, my, -1)
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.selected_card_index = None
        return None

    def update(self, dt):
        if self.game_over:
            return

        self.elapsed_time += dt
        prev_tower_hp = self.tower.health

        # ── Mana ────────────────────────────────────────────────────────────
        self.mana.update(dt)

        # ── Waves ───────────────────────────────────────────────────────────
        self.wave_timer -= dt
        if self.wave_timer <= 0:
            self._spawn_wave()

        # ── Tower attacks ───────────────────────────────────────────────────
        proj = self.tower.update(dt, self.enemy_characters)
        if proj:
            self.projectiles.append(proj)

        # ── Player characters ───────────────────────────────────────────────
        for char in self.player_characters:
            projs, spawns = char.update(dt, self.enemy_characters)
            if projs:
                sounds.play_attack(char.name)
                for p in projs:
                    self.total_damage_dealt += p.damage
            self.projectiles.extend(projs)
            for s in spawns:
                self._spawn_helper(s)

        # ── Enemy characters ────────────────────────────────────────────────
        for char in self.enemy_characters:
            projs, spawns = char.update(dt, self.player_characters, self.tower)
            if projs:
                sounds.play_attack(char.name)
            self.projectiles.extend(projs)
            for s in spawns:
                self._spawn_helper(s)

        # ── Projectiles ────────────────────────────────────────────────────
        all_player = self.player_characters + [self.tower]
        for p in self.projectiles:
            if p.team == "player":
                p.update(dt, self.enemy_characters)
            else:
                p.update(dt, all_player)

        # ── Effects ─────────────────────────────────────────────────────────
        for e in self.effects:
            e.update(dt)

        # ── Cleanup dead ────────────────────────────────────────────────────
        self.player_characters = [c for c in self.player_characters if c.alive]
        self.enemy_characters = [c for c in self.enemy_characters if c.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.effects = [e for e in self.effects if e.alive]

        # ── Log tower damage ────────────────────────────────────────────────
        dmg_taken = prev_tower_hp - self.tower.health
        if dmg_taken > 0:
            self.stats_log.append({
                "time": round(self.elapsed_time, 2),
                "event": "tower_damage",
                "card_name": "",
                "mana_cost": 0,
                "attack_type": "",
                "grid_section": -1,
                "damage": dmg_taken,
            })

        # ── Check tower death ───────────────────────────────────────────────
        if not self.tower.alive:
            self.game_over = True
            self._save_stats()
            sounds.stop_music()
            sounds.play("lose")

    def draw(self, surface):
        surface.fill(BLACK)
        self._draw_arena(surface)
        self._draw_grid_overlay(surface)
        self.tower.draw(surface)
        for c in self.player_characters + self.enemy_characters:
            c.draw(surface)
        for p in self.projectiles:
            p.draw(surface)
        for e in self.effects:
            e.draw(surface)
        self._draw_ui(surface)
        self._draw_hud(surface)
        if self.game_over:
            self._draw_game_over(surface)

    # ════════════════════════════════════════════════════════════════════════
    #  Deployment
    # ════════════════════════════════════════════════════════════════════════
    def _get_grid_section(self, mx, my):
        for i, rect in enumerate(self.grid_sections):
            if rect.collidepoint(mx, my):
                return i
        return None

    def _try_deploy(self, mx, my, grid_idx):
        idx = self.selected_card_index
        if idx is None or idx >= len(self.hand):
            return
        card = self.hand[idx]
        if not card.can_play(self.mana):
            return

        if card.is_spell:
            deploy_x = max(20, min(mx, WIDTH - 20))
            deploy_y = max(ARENA_TOP + 20, min(my, ARENA_BOTTOM - 20))
            self.mana.spend(card.cost)
            self._apply_spell(card, deploy_x, deploy_y)
        else:
            deploy_x = max(GRID_LEFT, min(mx, GRID_RIGHT))
            deploy_y = max(GRID_TOP, min(my, GRID_BOTTOM))
            characters = card.play(self.mana, deploy_x, deploy_y, "player")
            self.player_characters.extend(characters)

        # Stats log
        self.total_cards_played += 1
        self.total_mana_used += card.cost
        self.stats_log.append({
            "time": round(self.elapsed_time, 2),
            "event": "card_played",
            "card_name": card.name,
            "mana_cost": card.cost,
            "attack_type": card.card_data.get("attack_type", "melee"),
            "grid_section": grid_idx if grid_idx is not None and grid_idx >= 0 else -1,
            "damage": 0,
        })

        # Cycle hand
        self.hand[idx] = self.queue.pop(0)
        self.queue.append(card)
        self.selected_card_index = None

    def _apply_spell(self, card, x, y):
        if card.name == "Fireball":
            for e in self.enemy_characters:
                if not e.alive:
                    continue
                if math.hypot(e.x - x, e.y - y) <= card.card_data["splash_radius"]:
                    e.take_damage(card.card_data["damage"])
                    self.total_damage_dealt += card.card_data["damage"]
            self.effects.append(
                SpellEffect(x, y, card.card_data["splash_radius"], (255, 140, 30)))
            sounds.play("fireball")

        elif card.name == "Goblin Barrel":
            goblin_data = SPAWNED_TROOPS["Goblins"]
            for i in range(3):
                angle = (2 * math.pi / 3) * i
                gx = x + math.cos(angle) * 18
                gy = y + math.sin(angle) * 18
                self.player_characters.append(
                    Character(gx, gy, "Goblins", goblin_data, "player"))
            self.effects.append(SpellEffect(x, y, 30, (60, 200, 60)))
            sounds.play("fireball")

    def _spawn_helper(self, spawn_dict):
        data = SPAWNED_TROOPS.get(spawn_dict["name"])
        if data is None:
            return
        c = Character(spawn_dict["x"], spawn_dict["y"],
                      spawn_dict["name"], data, spawn_dict["team"])
        if spawn_dict["team"] == "player":
            self.player_characters.append(c)
        else:
            self.enemy_characters.append(c)

    # ════════════════════════════════════════════════════════════════════════
    #  Wave system
    # ════════════════════════════════════════════════════════════════════════
    def _spawn_wave(self):
        self.wave_number += 1
        self.wave_timer = max(WAVE_INTERVAL - self.wave_number * 0.3, 5.0)

        num_enemies = WAVE_BASE_ENEMIES + (self.wave_number - 1) * WAVE_ENEMY_INCREMENT
        hp_mult = WAVE_HP_SCALE ** (self.wave_number - 1)
        dmg_mult = WAVE_DMG_SCALE ** (self.wave_number - 1)

        pool = []
        for name, weight in WAVE_ENEMY_POOL:
            pool.extend([name] * weight)

        for _ in range(num_enemies):
            name = random.choice(pool)
            card_data = dict(CARDS[name])
            card_data["hp"] = int(card_data["hp"] * hp_mult)
            card_data["damage"] = int(card_data["damage"] * dmg_mult)
            card_data["count"] = 1  # single character per slot
            x = random.randint(GRID_LEFT + 20, GRID_RIGHT - 20)
            y = random.randint(ENEMY_SPAWN_TOP, ENEMY_SPAWN_BOTTOM)
            self.enemy_characters.append(
                Character(x, y, name, card_data, "enemy"))

    # ════════════════════════════════════════════════════════════════════════
    #  CSV stats
    # ════════════════════════════════════════════════════════════════════════
    def _save_stats(self):
        self.stats_log.append({
            "time": round(self.elapsed_time, 2),
            "event": "game_over",
            "card_name": "",
            "mana_cost": 0,
            "attack_type": "",
            "grid_section": -1,
            "damage": self.wave_number,
        })

        filepath = os.path.join(os.path.dirname(__file__), "game_stats.csv")
        fieldnames = ["time", "event", "card_name", "mana_cost",
                      "attack_type", "grid_section", "damage"]
        file_exists = os.path.exists(filepath) and os.path.getsize(filepath) > 0
        with open(filepath, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for row in self.stats_log:
                writer.writerow(row)

    # ════════════════════════════════════════════════════════════════════════
    #  Drawing helpers
    # ════════════════════════════════════════════════════════════════════════
    def _draw_arena(self, surface):
        pygame.draw.rect(surface, ARENA_GREEN,
                         (0, ARENA_TOP, WIDTH, ARENA_HEIGHT))
        for row in range(ARENA_HEIGHT // TILE):
            for col in range(WIDTH // TILE):
                if (row + col) % 2 == 0:
                    pygame.draw.rect(surface, ARENA_GREEN2,
                                     (col * TILE, ARENA_TOP + row * TILE,
                                      TILE, TILE))
        # Top / bottom boundaries
        pygame.draw.line(surface, DARK_GRAY,
                         (0, ARENA_TOP), (WIDTH, ARENA_TOP), 2)
        pygame.draw.line(surface, DARK_GRAY,
                         (0, ARENA_BOTTOM), (WIDTH, ARENA_BOTTOM), 2)

    def _draw_grid_overlay(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i, rect in enumerate(self.grid_sections):
            pygame.draw.rect(overlay, (255, 255, 255, 10), rect)
            pygame.draw.rect(overlay, (255, 255, 255, 25), rect, 1)
        if not hasattr(self, "_grid_font"):
            self._grid_font = pygame.font.SysFont("arial", 11)
        for i, rect in enumerate(self.grid_sections):
            lbl = self._grid_font.render(str(i + 1), True, (255, 255, 255, 40))
            overlay.blit(lbl, (rect.x + 4, rect.y + 2))
        surface.blit(overlay, (0, 0))

    def _draw_hud(self, surface):
        pygame.draw.rect(surface, (30, 30, 50), (0, 0, WIDTH, ARENA_TOP))

        wave_txt = self.font_lg.render(f"Wave {self.wave_number}", True, WHITE)
        surface.blit(wave_txt,
                     (WIDTH // 2 - wave_txt.get_width() // 2, 5))

        mins = int(self.elapsed_time) // 60
        secs = int(self.elapsed_time) % 60
        time_txt = self.font_sm.render(f"{mins}:{secs:02d}", True, GRAY)
        surface.blit(time_txt,
                     (WIDTH // 2 - time_txt.get_width() // 2, 33))

        hp_txt = self.font.render(
            f"\u2665 {self.tower.health}/{self.tower.max_health}", True, LIGHT_BLUE)
        surface.blit(hp_txt, (20, 14))

        enemy_txt = self.font_sm.render(
            f"Enemies: {len(self.enemy_characters)}", True, LIGHT_RED)
        surface.blit(enemy_txt, (WIDTH - enemy_txt.get_width() - 20, 18))

    def _draw_ui(self, surface):
        pygame.draw.rect(surface, (30, 25, 45), (0, UI_TOP, WIDTH, UI_HEIGHT))

        # Mana bar
        pygame.draw.rect(surface, MANA_BG,
                         (MANA_BAR_X, MANA_BAR_Y, MANA_BAR_W, MANA_BAR_H),
                         border_radius=4)
        fill_w = int(MANA_BAR_W * self.mana.current_mana / self.mana.max_mana)
        pygame.draw.rect(surface, MANA_PURPLE,
                         (MANA_BAR_X, MANA_BAR_Y, fill_w, MANA_BAR_H),
                         border_radius=4)
        mtxt = self.font.render(f"{int(self.mana.current_mana)}", True, WHITE)
        surface.blit(mtxt,
                     (MANA_BAR_X + MANA_BAR_W // 2 - mtxt.get_width() // 2,
                      MANA_BAR_Y + 1))
        regen_txt = self.font_sm.render(
            f"{self.mana.regen_rate:.1f} mana/s", True, LIGHT_GRAY)
        surface.blit(regen_txt,
                     (MANA_BAR_X + MANA_BAR_W - regen_txt.get_width(),
                      MANA_BAR_Y - regen_txt.get_height() - 2))

        # Cards
        for i in range(4):
            if i >= len(self.hand):
                break
            card = self.hand[i]
            rx = CARD_START_X + i * (CARD_W + CARD_GAP)
            ry = CARD_Y
            selected = i == self.selected_card_index
            affordable = card.can_play(self.mana)
            self._draw_card(surface, card, rx, ry, selected, affordable)

        # Next card preview
        if self.queue:
            nc = self.queue[0]
            ntxt = self.font_sm.render(
                f"Next: {nc.name} ({nc.cost})", True, GRAY)
            surface.blit(ntxt, (CARD_START_X, CARD_Y + CARD_H + 4))

    def _draw_card(self, surface, card, x, y, selected, affordable):
        data = card.card_data
        bg = CARD_BG if not selected else (80, 70, 40)
        border = (CARD_SELECTED if selected
                  else (CARD_BORDER if affordable else DARK_GRAY))
        pygame.draw.rect(surface, bg,
                         (x, y, CARD_W, CARD_H), border_radius=6)
        pygame.draw.rect(surface, border,
                         (x, y, CARD_W, CARD_H), 2, border_radius=6)

        if not affordable and not selected:
            dim = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 100))
            surface.blit(dim, (x, y))

        cx = x + CARD_W // 2
        cy = y + 50
        s = data["size"] + 4
        c = data["colour"]
        if data["shape"] == "square":
            pygame.draw.rect(surface, c, (cx - s, cy - s, s * 2, s * 2))
        elif data["shape"] == "circle":
            pygame.draw.circle(surface, c, (cx, cy), s)
        elif data["shape"] == "triangle":
            pygame.draw.polygon(surface, c,
                                [(cx, cy - s), (cx - s, cy + s), (cx + s, cy + s)])
        elif data["shape"] == "diamond":
            pygame.draw.polygon(surface, c,
                                [(cx, cy - s), (cx + s, cy),
                                 (cx, cy + s), (cx - s, cy)])

        # Mana cost bubble
        pygame.draw.circle(surface, MANA_PURPLE, (x + 14, y + 14), 12)
        ct = self.font_sm.render(str(card.cost), True, WHITE)
        surface.blit(ct, (x + 14 - ct.get_width() // 2,
                          y + 14 - ct.get_height() // 2))

        # Name
        ntxt = self.font_sm.render(card.name, True, WHITE)
        surface.blit(ntxt, (x + CARD_W // 2 - ntxt.get_width() // 2,
                            y + CARD_H - 28))

    def _draw_game_over(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        txt = self.font_xl.render("GAME OVER", True, RED)
        surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2,
                           HEIGHT // 2 - 130))

        # ── End-screen summary ──────────────────────────────────────────────
        lines = [
            (f"Survived to Wave {self.wave_number}", YELLOW, self.font_lg),
            (f"Time: {int(self.elapsed_time // 60)}:"
             f"{int(self.elapsed_time) % 60:02d}", WHITE, self.font),
            (f"Total damage dealt: {self.total_damage_dealt}", WHITE, self.font),
            (f"Cards played: {self.total_cards_played}", WHITE, self.font),
            (f"Mana consumed: {int(self.total_mana_used)}", WHITE, self.font),
        ]
        y_cur = HEIGHT // 2 - 70
        for text, colour, font in lines:
            t = font.render(text, True, colour)
            surface.blit(t, (WIDTH // 2 - t.get_width() // 2, y_cur))
            y_cur += t.get_height() + 8

        hint = self.font.render("Click to return", True, GRAY)
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, y_cur + 20))
