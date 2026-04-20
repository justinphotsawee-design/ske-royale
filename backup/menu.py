import pygame
from constants import *


class TitleScreen:
    """Main menu with Play, Deck, Stats buttons."""

    def __init__(self):
        self.font_title = pygame.font.SysFont("arial", 52, bold=True)
        self.font_sub = pygame.font.SysFont("arial", 20)
        self.font_btn = pygame.font.SysFont("arial", 28, bold=True)
        self.buttons = [
            {"label": "PLAY",  "action": "play",  "y": 420},
            {"label": "DECK",  "action": "deck",  "y": 510},
            {"label": "STATS", "action": "stats", "y": 600},
        ]
        self.btn_w = 240
        self.btn_h = 60
        self.hovered = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self._hit(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            btn = self._hit(event.pos)
            if btn:
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

        # Title
        title = self.font_title.render("SKE ROYALE", True, YELLOW)
        shadow = self.font_title.render("SKE ROYALE", True, (80, 60, 0))
        surface.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 3, 153))
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        # Subtitle
        sub = self.font_sub.render("A Clash-Royale-inspired project", True, LIGHT_GRAY)
        surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 220))

        # Decorative crown
        cx, cy = WIDTH // 2, 310
        crown_pts = [
            (cx - 40, cy + 10), (cx - 30, cy - 15), (cx - 15, cy),
            (cx, cy - 25), (cx + 15, cy), (cx + 30, cy - 15), (cx + 40, cy + 10),
        ]
        pygame.draw.polygon(surface, YELLOW, crown_pts)
        pygame.draw.polygon(surface, (180, 150, 20), crown_pts, 2)
        pygame.draw.rect(surface, YELLOW, (cx - 40, cy + 10, 80, 14))

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
        self.card_w = 115
        self.card_h = 140
        self.gap = 10
        self.grid_left = (WIDTH - (self.grid_cols * self.card_w +
                          (self.grid_cols - 1) * self.gap)) // 2
        self.grid_top = 90  # below title
        self.deck_display_y = HEIGHT - 180
        self.back_btn = pygame.Rect(20, HEIGHT - 50, 100, 40)
        self.clear_btn = pygame.Rect(WIDTH - 120, HEIGHT - 50, 100, 40)

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
        dw = 55
        dh = 55
        dgap = 6
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
            avg_txt = self.font_sm.render(f"Avg elixir: {avg:.1f}", True, ELIXIR_PURPLE)
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
        pygame.draw.circle(surface, ELIXIR_PURPLE, (x + 14, y + 14), 11)
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
        dw = 55
        dh = 55
        dgap = 6
        dx_start = (WIDTH - (8 * dw + 7 * dgap)) // 2
        for i in range(8):
            dx = dx_start + i * (dw + dgap)
            dy = self.deck_display_y + 26
            if dx <= mx <= dx + dw and dy <= my <= dy + dh:
                return i
        return None


class StatsScreen:
    """Placeholder stats screen."""

    def __init__(self):
        self.font_title = pygame.font.SysFont("arial", 30, bold=True)
        self.font = pygame.font.SysFont("arial", 18)
        self.font_btn = pygame.font.SysFont("arial", 22, bold=True)
        self.back_btn = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 80, 120, 45)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.collidepoint(event.pos):
                return "back"
        return None

    def draw(self, surface):
        surface.fill((25, 20, 40))
        title = self.font_title.render("STATS", True, YELLOW)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        msg = self.font.render("Coming soon...", True, GRAY)
        surface.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 20))

        pygame.draw.rect(surface, (100, 60, 60), self.back_btn, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.back_btn, 2, border_radius=8)
        txt = self.font_btn.render("BACK", True, WHITE)
        surface.blit(txt, (self.back_btn.centerx - txt.get_width() // 2,
                           self.back_btn.centery - txt.get_height() // 2))
