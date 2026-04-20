# SKE Royale

## Project Description

- Project by: Photsawee Niwadtongrirk
- Game Genre: Strategy, Tower Defense

SKE Royale is a Clash Royale-inspired infinite wave survival game built in Python. You build a deck of 8 cards, then defend your tower against endless enemy waves by deploying units onto a 9-section arena grid. Mana regenerates over time, enemy waves scale in difficulty, and all your gameplay data is recorded and visualised in a statistics window.

---

## Installation
To Clone this project:
```sh
git clone https://github.com/justinphotsawee-design/ske-royale.git
```

To create and run Python Environment for This project:

Window:
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Mac:
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running Guide
After activating the Python environment, run the game with:

Window:
```bat
python main.py
```

Mac:
```sh
python3 main.py
```

---

## Tutorial / Usage

**Main Menu**
- **PLAY** — Start a battle. Requires a full deck of 8 cards.
- **DECK** — Open the deck builder to choose your 8 cards.
- **STATS** — Toggle the statistics window showing charts from past games.

**Deck Builder**
- Click any card to add it to your deck (highlighted in gold when selected).
- Click a selected card again to remove it.
- You need exactly 8 cards before you can start a game.
- Click **Back** to return to the menu (your deck is saved automatically if it is complete).

**In-Game**
- Click a card in the bottom panel to select it (highlighted in gold).
- Click anywhere in the 3×3 grid (lower half of the arena) to deploy the card there.
- Right-click to deselect a card without spending mana.
- Press **Escape** to forfeit the current run and return to the menu.
- The game ends when your tower's HP reaches zero. Click anywhere on the game-over screen to return to the menu.

**Mana**
- Starts at 5 and regenerates up to a maximum of 10.
- Regeneration rate slowly increases over time.
- Each card has a mana cost shown on its tile.

---

## Game Features

- **Infinite wave survival** — Enemies spawn in waves that grow larger and stronger every round (HP and damage scale each wave).
- **13-card pool** — Choose from Knight, Archers, Giant, Musketeer, Fireball, Mini PEKKA, Valkyrie, Hog Rider, Witch, Baby Dragon, Prince, Skeleton Army, Bomber, and Goblin Barrel.
- **Varied unit mechanics** — Melee, ranged, splash, summon (Witch spawns Skeletons), charge (Prince doubles first-hit damage), and flying (Baby Dragon) units.
- **Spell cards** — Fireball deals area damage anywhere on the arena; Goblin Barrel drops three Goblins at a chosen location.
- **Deck builder** — Fully customisable 8-card deck with a scrollable card grid.
- **Mana economy** — Mana regenerates over time and accelerates as the game progresses.
- **CSV statistics logging** — Every card play, tower damage event, and final wave number is appended to **game_stats.csv**.
- **Statistics viewer** — A Tkinter window with five tabs: card frequency bar chart, archetype pie chart, tower damage line graph, mana expenditure line graph, and a grid placement heatmap.
- **Background music and sound effects** — Separate menu and in-game tracks; attack sounds for different unit types.

---

## Known Bugs

- The statistics window must be closed before quitting the game via the window's X button, otherwise the background thread may keep the process alive.
- If **game_stats.csv** is deleted mid-session, the stats window will show empty charts until the next game over is recorded.

---

## Unfinished Works

- No audio volume controls or settings menu.
- Card descriptions in the deck builder are text-only; no card artwork.
- No character artwork (kind off intended because geometric aesthetics already looks nice.)

---

## External sources

[Sound Effects from Pixabay](https://pixabay.com/sound-effects/)
[Menu Theme Song by Naktigonis](https://www.youtube.com/watch?v=7iUcvHO1u34&list=PLGt9OOZXqp2JI1vE3olIgOUO-E3PREqRv&index=11)
[In-game Theme Song by Naktigonis](https://www.youtube.com/watch?v=jEufEiXyuxU&list=PLGt9OOZXqp2JI1vE3olIgOUO-E3PREqRv&index=16)
