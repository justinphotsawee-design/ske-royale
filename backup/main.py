import pygame
import sys
from constants import WIDTH, HEIGHT, FPS, DEFAULT_DECK
from menu import TitleScreen, DeckScreen, StatsScreen
from game import Battle
import sounds


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SKE Royale")
    clock = pygame.time.Clock()

    # Persistent state
    player_deck = list(DEFAULT_DECK)

    # Screens
    title_screen = TitleScreen()
    deck_screen = DeckScreen(player_deck)
    stats_screen = StatsScreen()
    battle = None

    current = "title"  # "title" | "deck" | "stats" | "battle"
    sounds.play_music("menu")

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if current == "battle":
                    current = "title"
                    battle = None
                    sounds.play_music("menu")
                elif current in ("deck", "stats"):
                    current = "title"
                else:
                    running = False
                continue

            if current == "title":
                action = title_screen.handle_event(event)
                if action == "play":
                    if len(player_deck) == 8:
                        battle = Battle(player_deck)
                        current = "battle"
                        sounds.play_music("ingame")
                elif action == "deck":
                    deck_screen = DeckScreen(player_deck)
                    current = "deck"
                elif action == "stats":
                    current = "stats"

            elif current == "deck":
                action = deck_screen.handle_event(event)
                if action == "back":
                    if len(deck_screen.deck) == 8:
                        player_deck = list(deck_screen.deck)
                    current = "title"

            elif current == "stats":
                action = stats_screen.handle_event(event)
                if action == "back":
                    current = "title"

            elif current == "battle":
                result = battle.handle_event(event)
                if result == "done":
                    current = "title"
                    battle = None
                    sounds.play_music("menu")

        # Update
        if current == "battle" and battle:
            battle.update(dt)

        # Draw
        if current == "title":
            title_screen.draw(screen)
        elif current == "deck":
            deck_screen.draw(screen)
        elif current == "stats":
            stats_screen.draw(screen)
        elif current == "battle" and battle:
            battle.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
