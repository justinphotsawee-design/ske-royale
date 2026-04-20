import pygame
import csv
import os

import tkinter as tk
from tkinter import ttk
import threading
from constants import *
# For embedding matplotlib charts in Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np


class TitleScreen:
    """Main menu with Play, Deck, Stats buttons."""

    def __init__(self):
        self.font_title = pygame.font.SysFont("arial", 52, bold=True)
        self.font_sub = pygame.font.SysFont("arial", 20)
        self.font_btn = pygame.font.SysFont("arial", 28, bold=True)
        self.logo = pygame.image.load("assets/logo.png")
        self.buttons = [
            {"label": "PLAY",  "action": "play",  "y": 315},
            {"label": "DECK",  "action": "deck",  "y": 383},
            {"label": "STATS", "action": "stats", "y": 450},
        ]
        self.btn_w = 240
        self.btn_h = 60
        self.hovered = None
        self.stats_window = None
        self.stats_thread = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self._hit(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            btn = self._hit(event.pos)
            if btn:
                if btn["action"] == "stats":
                    self._toggle_stats()
                    return None
                return btn["action"]
        return None

    def draw(self, surface):
        # Background gradient (approximated with horizontal rects)
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(20 + 30 * t)
            g = int(10 + 20 * t)
            b = int(50 + 60 * (1 - t))
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        # Logo
        scaled_logo = pygame.transform.scale(self.logo, (self.logo.get_width() // 5, self.logo.get_height() // 5))
        logo_x = WIDTH // 2 - scaled_logo.get_width() // 2
        logo_y = 45
        surface.blit(scaled_logo, (logo_x, logo_y))

        # Buttons
        for btn in self.buttons:
            bx = WIDTH // 2 - self.btn_w // 2
            by = btn["y"]
            hovered = (self.hovered == btn)
            bg = (80, 60, 180) if not hovered else (110, 90, 220)
            border = YELLOW if hovered else CARD_BORDER
            pygame.draw.rect(surface, bg, (bx, by, self.btn_w, self.btn_h), border_radius=10)
            pygame.draw.rect(surface, border, (bx, by, self.btn_w, self.btn_h), 3, border_radius=10)
            txt = self.font_btn.render(btn["label"], True, WHITE)
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2,
                               by + self.btn_h // 2 - txt.get_height() // 2))

        # Footer
        foot = self.font_sub.render("v1.0", True, DARK_GRAY)
        surface.blit(foot, (WIDTH // 2 - foot.get_width() // 2, HEIGHT - 40))

    def _hit(self, pos):
        mx, my = pos
        for btn in self.buttons:
            bx = WIDTH // 2 - self.btn_w // 2
            by = btn["y"]
            if bx <= mx <= bx + self.btn_w and by <= my <= by + self.btn_h:
                return btn
        return None

    def _toggle_stats(self):
        if self.stats_window:
            try:
                self.stats_window.quit()
                self.stats_window.destroy()
            except:
                pass
            self.stats_window = None
            if self.stats_thread and self.stats_thread.is_alive():
                self.stats_thread.join(timeout=1)
            self.stats_thread = None
        else:
            self.stats_thread = threading.Thread(target=self._create_stats_window)
            self.stats_thread.start()

    def _create_stats_window(self):
        self.stats_window = tk.Tk()
        self.stats_window.title("Game Statistics")
        notebook = ttk.Notebook(self.stats_window)
        stats = self._load_stats()

        # Tab 1: Card Frequency (Bar Chart)
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Card Frequency")
        if stats and 'card_freq' in stats and stats['card_freq']:
            fig1, ax1 = plt.subplots(figsize=(4, 2.5), dpi=100)
            items = sorted(stats['card_freq'].items(), key=lambda x: -x[1])[:10]
            names = [n for n, _ in items]
            counts = [c for _, c in items]
            ax1.bar(names, counts, color='skyblue')
            ax1.set_ylabel('Plays')
            ax1.set_title('Top 10 Card Frequency')
            ax1.tick_params(axis='x', rotation=30)
            fig1.tight_layout()
            canvas1 = FigureCanvasTkAgg(fig1, master=tab1)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(tab1, text="No card data.").pack()

        # Tab 2: Archetype (Pie Chart)
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Archetype")
        if stats:
            melee = stats.get('melee', 0)
            range_ = stats.get('range', 0)
            total = melee + range_
            if total > 0:
                fig2, ax2 = plt.subplots(figsize=(3.5, 2.5), dpi=100)
                ax2.pie([melee, range_], labels=["Melee", "Range"], autopct='%1.1f%%', colors=['#ff9999','#66b3ff'])
                ax2.set_title('Archetype Distribution')
                fig2.tight_layout()
                canvas2 = FigureCanvasTkAgg(fig2, master=tab2)
                canvas2.draw()
                canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                tk.Label(tab2, text="No archetype data.").pack()
        else:
            tk.Label(tab2, text="No archetype data.").pack()

        # Tab 3: Tower Damage (Line Graph)
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Tower Damage")
        if stats:
            # For line graph, show tower damage per game if available
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_stats.csv")
            tower_dmg_per_game = []
            if os.path.exists(filepath):
                with open(filepath, newline="") as f:
                    reader = csv.DictReader(f)
                    dmg = 0
                    for row in reader:
                        if row["event"] == "tower_damage":
                            try:
                                dmg += int(float(row["damage"]))
                            except Exception:
                                pass
                        if row["event"] == "game_over":
                            tower_dmg_per_game.append(dmg)
                            dmg = 0
            if tower_dmg_per_game:
                fig3, ax3 = plt.subplots(figsize=(4, 2.5), dpi=100)
                ax3.plot(range(1, len(tower_dmg_per_game)+1), tower_dmg_per_game, marker='o', color='orange')
                ax3.set_xlabel('Game #')
                ax3.set_ylabel('Tower Damage')
                ax3.set_title('Tower Damage per Game')
                fig3.tight_layout()
                canvas3 = FigureCanvasTkAgg(fig3, master=tab3)
                canvas3.draw()
                canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                tk.Label(tab3, text=f"Total damage taken: {stats.get('tower_dmg', 0)}").pack()
        else:
            tk.Label(tab3, text="No tower damage data.").pack()

        # Tab 4: Mana Expenditure (Line Graph)
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Mana Expenditure")
        if stats:
            # Show mana spent per game if available
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_stats.csv")
            mana_per_game = []
            if os.path.exists(filepath):
                with open(filepath, newline="") as f:
                    reader = csv.DictReader(f)
                    mana = 0
                    for row in reader:
                        if row["event"] == "card_played":
                            try:
                                mana += float(row["mana_cost"])
                            except Exception:
                                pass
                        if row["event"] == "game_over":
                            mana_per_game.append(mana)
                            mana = 0
            if mana_per_game:
                fig4, ax4 = plt.subplots(figsize=(4, 2.5), dpi=100)
                ax4.plot(range(1, len(mana_per_game)+1), mana_per_game, marker='o', color='green')
                ax4.set_xlabel('Game #')
                ax4.set_ylabel('Mana Spent')
                ax4.set_title('Mana Spent per Game')
                fig4.tight_layout()
                canvas4 = FigureCanvasTkAgg(fig4, master=tab4)
                canvas4.draw()
                canvas4.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                tk.Label(tab4, text=f"Total mana spent: {int(stats.get('total_mana', 0))}").pack()
        else:
            tk.Label(tab4, text="No mana data.").pack()

        # Tab 5: Positional Placement (Heatmap)
        tab5 = ttk.Frame(notebook)
        notebook.add(tab5, text="Positional Placement")
        if stats and 'grid_heat' in stats and stats['grid_heat']:
            fig5, ax5 = plt.subplots(figsize=(2.5, 2.5), dpi=100)
            grid = np.array(stats['grid_heat']).reshape((3, 3))
            im = ax5.imshow(grid, cmap='hot', interpolation='nearest')
            for i in range(3):
                for j in range(3):
                    ax5.text(j, i, str(grid[i, j]), ha='center', va='center', color='white', fontsize=10)
            ax5.set_xticks([])
            ax5.set_yticks([])
            ax5.set_title('Grid Placement Heatmap')
            fig5.colorbar(im, ax=ax5, fraction=0.046, pad=0.04)
            fig5.tight_layout()
            canvas5 = FigureCanvasTkAgg(fig5, master=tab5)
            canvas5.draw()
            canvas5.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(tab5, text="No grid placement data.").pack()

        notebook.pack(fill=tk.BOTH, expand=True)
        self.stats_window.mainloop()

    def _load_stats(self):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_stats.csv")
        if not os.path.exists(filepath):
            return None
        rows = []
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        if not rows:
            return None

        games = [r for r in rows if r["event"] == "game_over"]
        plays = [r for r in rows if r["event"] == "card_played"]
        tower_dmg_rows = [r for r in rows if r["event"] == "tower_damage"]

        num_games = len(games)
        best_wave = max((int(float(g["damage"])) for g in games), default=0)
        total_cards = len(plays)

        card_freq = {}
        melee_count = 0
        range_count = 0
        total_mana = 0.0
        grid_heat = [0] * 9

        for p in plays:
            name = p["card_name"]
            card_freq[name] = card_freq.get(name, 0) + 1
            atype = p.get("attack_type", "")
            if atype == "melee":
                melee_count += 1
            elif atype in ("range", "summon"):
                range_count += 1
            try:
                total_mana += float(p["mana_cost"])
            except (ValueError, KeyError):
                pass
            try:
                gs = int(p["grid_section"])
                if 0 <= gs < 9:
                    grid_heat[gs] += 1
            except (ValueError, KeyError):
                pass

        tower_dmg_total = 0
        for t in tower_dmg_rows:
            try:
                tower_dmg_total += int(float(t["damage"]))
            except (ValueError, KeyError):
                pass

        return {
            "num_games": num_games,
            "best_wave": best_wave,
            "total_cards": total_cards,
            "card_freq": card_freq,
            "melee": melee_count,
            "range": range_count,
            "total_mana": total_mana,
            "grid_heat": grid_heat,
            "tower_dmg": tower_dmg_total,
        }


class DeckScreen:
    """Deck builder: pick 8 cards from all available cards."""

    def __init__(self, current_deck):
        self.font_title = pygame.font.SysFont("arial", 30, bold=True)
        self.font = pygame.font.SysFont("arial", 16, bold=True)
        self.font_sm = pygame.font.SysFont("arial", 13)
        self.font_btn = pygame.font.SysFont("arial", 22, bold=True)
        self.deck = list(current_deck)  # list of card names (up to 8)
        self.scroll_y = 0
        self.max_deck = 8

        # Layout
        self.grid_cols = 4
        self.card_w = 90
        self.card_h = 110
        self.gap = 8
        self.grid_left = (WIDTH - (self.grid_cols * self.card_w +
                          (self.grid_cols - 1) * self.gap)) // 2
        self.grid_top = 90  # below title
        self.deck_display_y = HEIGHT - 140
        self.back_btn = pygame.Rect(20, HEIGHT - 40, 80, 32)
        self.clear_btn = pygame.Rect(WIDTH - 100, HEIGHT - 40, 80, 32)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Back button
            if self.back_btn.collidepoint(mx, my):
                return "back"
            # Clear button
            if self.clear_btn.collidepoint(mx, my):
                self.deck.clear()
                return None
            # Card grid click
            card_name = self._hit_grid(mx, my)
            if card_name:
                if card_name in self.deck:
                    self.deck.remove(card_name)
                elif len(self.deck) < self.max_deck:
                    self.deck.append(card_name)
            # Deck display click (remove card)
            deck_idx = self._hit_deck_display(mx, my)
            if deck_idx is not None and deck_idx < len(self.deck):
                self.deck.pop(deck_idx)

        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * 30
            self.scroll_y = max(0, self.scroll_y)
        return None

    def draw(self, surface):
        surface.fill((25, 20, 40))

        # Title
        title = self.font_title.render("DECK BUILDER", True, YELLOW)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
        hint = self.font_sm.render(
            f"Select {self.max_deck} cards  ({len(self.deck)}/{self.max_deck})", True, LIGHT_GRAY)
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 58))

        # Available cards grid
        for i, name in enumerate(ALL_CARD_NAMES):
            col = i % self.grid_cols
            row = i // self.grid_cols
            x = self.grid_left + col * (self.card_w + self.gap)
            y = self.grid_top + row * (self.card_h + self.gap) - self.scroll_y
            if y + self.card_h < self.grid_top - 10 or y > self.deck_display_y - 10:
                continue  # off-screen
            in_deck = name in self.deck
            self._draw_grid_card(surface, name, CARDS[name], x, y, in_deck)

        # Divider
        pygame.draw.line(surface, DARK_GRAY, (10, self.deck_display_y - 8),
                         (WIDTH - 10, self.deck_display_y - 8), 2)

        # Current deck display
        lbl = self.font.render("YOUR DECK:", True, WHITE)
        surface.blit(lbl, (20, self.deck_display_y))
        dw = 45
        dh = 45
        dgap = 5
        dx_start = (WIDTH - (8 * dw + 7 * dgap)) // 2
        for i in range(8):
            dx = dx_start + i * (dw + dgap)
            dy = self.deck_display_y + 26
            if i < len(self.deck):
                card = CARDS[self.deck[i]]
                pygame.draw.rect(surface, card["colour"], (dx, dy, dw, dh), border_radius=4)
                pygame.draw.rect(surface, WHITE, (dx, dy, dw, dh), 2, border_radius=4)
                # Cost
                cost_txt = self.font_sm.render(str(card["cost"]), True, WHITE)
                surface.blit(cost_txt, (dx + 2, dy + 2))
                # Short name
                short = self.deck[i][:6]
                ntxt = self.font_sm.render(short, True, WHITE)
                surface.blit(ntxt, (dx + dw // 2 - ntxt.get_width() // 2, dy + dh - 16))
            else:
                pygame.draw.rect(surface, DARK_GRAY, (dx, dy, dw, dh), border_radius=4)
                pygame.draw.rect(surface, GRAY, (dx, dy, dw, dh), 1, border_radius=4)

        # Avg elixir
        if self.deck:
            avg = sum(CARDS[n]["cost"] for n in self.deck) / len(self.deck)
            avg_txt = self.font_sm.render(f"Avg mana: {avg:.1f}", True, MANA_PURPLE)
            surface.blit(avg_txt, (WIDTH // 2 - avg_txt.get_width() // 2,
                                   self.deck_display_y + 86))

        # Buttons
        self._draw_button(surface, self.back_btn, "BACK", (100, 60, 60))
        self._draw_button(surface, self.clear_btn, "CLEAR", (60, 60, 100))

    def _draw_grid_card(self, surface, name, card, x, y, in_deck):
        bg = (50, 45, 70) if not in_deck else (70, 80, 50)
        border = GREEN if in_deck else (100, 90, 120)
        pygame.draw.rect(surface, bg, (x, y, self.card_w, self.card_h), border_radius=6)
        pygame.draw.rect(surface, border, (x, y, self.card_w, self.card_h), 2, border_radius=6)

        # Shape
        cx = x + self.card_w // 2
        cy = y + 48
        s = card["size"] + 2
        c = card["colour"]
        if card["shape"] == "square":
            pygame.draw.rect(surface, c, (cx - s, cy - s, s * 2, s * 2))
        elif card["shape"] == "circle":
            pygame.draw.circle(surface, c, (cx, cy), s)
        elif card["shape"] == "triangle":
            pygame.draw.polygon(surface, c, [(cx, cy - s), (cx - s, cy + s), (cx + s, cy + s)])
        elif card["shape"] == "diamond":
            pygame.draw.polygon(surface, c, [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)])

        # Cost
        pygame.draw.circle(surface, MANA_PURPLE, (x + 14, y + 14), 11)
        ct = self.font_sm.render(str(card["cost"]), True, WHITE)
        surface.blit(ct, (x + 14 - ct.get_width() // 2, y + 14 - ct.get_height() // 2))

        # Name
        ntxt = self.font_sm.render(name, True, WHITE)
        surface.blit(ntxt, (x + self.card_w // 2 - ntxt.get_width() // 2, y + self.card_h - 30))

        # Description
        desc = self.font_sm.render(card["description"][:20], True, GRAY)
        surface.blit(desc, (x + self.card_w // 2 - desc.get_width() // 2, y + self.card_h - 16))

        if in_deck:
            check = self.font.render("✓", True, GREEN)
            surface.blit(check, (x + self.card_w - 20, y + 4))

    def _draw_button(self, surface, rect, text, colour):
        pygame.draw.rect(surface, colour, rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, rect, 2, border_radius=8)
        txt = self.font_btn.render(text, True, WHITE)
        surface.blit(txt, (rect.centerx - txt.get_width() // 2,
                           rect.centery - txt.get_height() // 2))

    def _hit_grid(self, mx, my):
        for i, name in enumerate(ALL_CARD_NAMES):
            col = i % self.grid_cols
            row = i // self.grid_cols
            x = self.grid_left + col * (self.card_w + self.gap)
            y = self.grid_top + row * (self.card_h + self.gap) - self.scroll_y
            if x <= mx <= x + self.card_w and y <= my <= y + self.card_h:
                return name
        return None

    def _hit_deck_display(self, mx, my):
        dw = 45
        dh = 45
        dgap = 5
        dx_start = (WIDTH - (8 * dw + 7 * dgap)) // 2
        for i in range(8):
            dx = dx_start + i * (dw + dgap)
            dy = self.deck_display_y + 26
            if dx <= mx <= dx + dw and dy <= my <= dy + dh:
                return i
        return None


        return None
