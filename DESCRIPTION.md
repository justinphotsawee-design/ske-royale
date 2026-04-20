# Project Description

## 1. Project Overview

- **Project Name:** SKE Royale

- **Brief Description:**  
  SKE Royale is a real-time tower-defense survival game built in Python using the Pygame library. The player selects a deck of 8 cards before each run and then defends a single tower against endless waves of enemies by deploying units onto a 9-section grid arena. Each card costs mana to play, and mana regenerates automatically over time, creating a resource-management layer on top of the action.

  Gameplay continues until the player's tower is destroyed. Enemy waves grow larger and stronger with each passing wave, so the run ends when the player can no longer hold the line. After each game, all events are written to a CSV log and can be reviewed in a dedicated statistics window that displays interactive charts and heatmaps.

- **Problem Statement:**  
  While Clash Royale is a hugely popular card-battle game, it is mobile-only and ends each match in a few minutes, there is no PC version and no endless survival mode. SKE Royale fills that gap by bringing the same card-deployment and mana-management feel to the PC with an infinite wave format, so players can keep pushing for higher waves without a fixed end condition.

- **Target Users:**  
  Players who enjoy strategy or tower defense games which is infinite.

- **Key Features:**  
  - Infinite-wave survival gameplay with scaling enemy difficulty (HP and damage increase each wave)  
  - Custom deck builder allowing the player to choose any 8 cards from the full card pool before a run  
  - Mana economy system that regenerates over time and accelerates as the game progresses  
  - Automatic CSV statistics logging covering every card played, tower damage taken, and the final wave reached  
  - Tkinter-based statistics viewer with bar charts, line graphs, and a grid-placement heatmap powered by Matplotlib  

---

## 2. Concept

### 2.1 Background

- **Why this project exists:** There is no official PC version of Clash Royale, and no existing game combines its card-based, mana-driven gameplay with an infinite survival format on desktop. SKE Royale was built to provide exactly that experience.
- **What inspired the project:** The game design is inspired by Clash Royale, a mobile card-based strategy game. Its mechanics (mana, card costs, unit deployment, tower defense) translate naturally into distinct classes.
- **Importance:** By connecting programming concepts to a familiar and engaging game genre, the project makes abstract design patterns concrete and easier to understand.

### 2.2 Objectives

- Implement the five core classes defined in the project proposal (Character, Card, Tower, ManaManager, Stage) with clear attributes and behaviours.
- Deliver a complete and playable game loop: main menu > deck selection > infinite-wave battle > game over > statistics review.
- Collect structured gameplay data and present it through meaningful visualisations (bar charts, line graphs, heatmaps) that reveal real patterns in how the game was played.
- Keep the codebase modular so that each file (entities.py, game.py, menu.py, constants.py) has a single, well-defined responsibility.

---

## 3. UML Class Diagram

*(See attached PDF)*

---

## 4. Object-Oriented Programming Implementation

- **Character** (**entities.py**): Represents any unit on the battlefield, both player-deployed and enemy. Stores **name**, **health**, **speed**, **attack_type** (melee / range / summon), **damage**, **hit_speed**, and **attack_range**. Handles movement toward the nearest target, attacking, taking damage, and splash/summon mechanics (e.g. the Witch periodically spawns skeletons).

- **Card** (**entities.py**): Represents a playable item in the player's deck. Stores **name**, **cost**, and the number of **characters_to_be_summoned**. Exposes a **play()** method that checks mana affordability, deducts the cost via **ManaManager**, and returns a list of **Character** instances to be placed on the **Stage**.

- **Tower** (**entities.py**): Represents the player's home tower — the sole defensive structure whose destruction ends the run. Stores **health**, **damage**, **range**, and **hit_speed**. Automatically targets the nearest enemy and fires **Projectile** objects; draws a health bar above itself.

- **ManaManager** (**entities.py**): Controls the player's mana economy. Stores **current_mana**, **max_mana**, and **regen_rate**. Regenerates mana each frame (with a slow acceleration over time) and exposes **can_afford()** and **spend()** for the **Card** class to call.

- **Stage** (**game.py**): The central game-board controller. Stores the nine **grid_sections**, all active **player_characters**, **enemy_characters**, **projectiles**, and **effects**, plus a reference to the **Tower** and **ManaManager**. Drives the wave-spawning loop (increasing enemy count, HP, and damage each wave), resolves all entity updates and collisions each frame, and writes the stats log to CSV when the game ends.

- **TitleScreen** (**menu.py**): Renders the main menu (Play, Deck, Stats buttons) and manages the Tkinter statistics window. Toggling the Stats button opens or closes a separate thread running the Tkinter window; starting a game automatically closes it.

- **DeckScreen** (**menu.py**): Provides the deck-builder interface. Displays the full card pool in a scrollable grid and lets the player add or remove cards until exactly 8 are selected before returning to the main menu.

- **Projectile** (**entities.py**): A short lived helper that travels from a source position toward a locked-on target at a fixed speed, deals damage (with optional splash radius) on contact, and then marks itself dead for cleanup.

- **SpellEffect** (**entities.py**): A purely visual helper that renders an expanding circle at a spell's impact point for a brief duration, providing feedback for Fireball and Goblin Barrel plays.

---

## 5. Statistical Data

### 5.1 Data Recording Method

All gameplay events are accumulated in memory during a run inside **Stage.stats_log**, a list of dictionaries. When the tower is destroyed and the game ends, **Stage._save_stats()** appends every entry, plus a final **game_over** row recording the wave number reached, to a CSV file named **game_stats.csv** stored in the project directory. The file uses **csv.DictWriter** with append mode so data from multiple sessions accumulates without overwriting prior runs. If the file does not yet exist, a header row is written automatically.

Each row in the CSV contains the following fields:

| Field | Description |
|---|---|
| **time** | Elapsed game time in seconds when the event occurred |
| **event** | Event type: **card_played**, **tower_damage**, or **game_over** |
| **card_name** | Name of the card played (blank for non-card events) |
| **mana_cost** | Mana cost of the card played |
| **attack_type** | Attack type of the deployed unit (**melee**, **range**, or **summon**) |
| **grid_section** | Index (0–8) of the 9-section grid where the card was placed |
| **damage** | Damage value for **tower_damage** events; wave number for **game_over** |

### 5.2 Data Features

The statistics window (opened via the Stats button on the main menu) reads **game_stats.csv** and presents five data features, each on its own tab:

1. **Card Frequency (Bar Chart):** Shows how many times each card has been played across all sessions, sorted descending. Reveals which cards the player relies on most.

2. **Archetype Distribution (Pie Chart):** Breaks down all card plays into melee vs. ranged/summon categories. Shows whether the player favours aggressive frontline units or stand-off ranged strategies.

3. **Tower Damage per Game (Line Graph):** Plots the total damage the tower received in each individual game. An upward trend indicates that the player is surviving longer but taking more punishment from tougher waves.

4. **Mana Expenditure per Game (Line Graph):** Plots total mana spent across each game. Higher values reflect more active card deployment and longer survival times.

5. **Positional Placement (Heatmap):** Renders a 3×3 grid coloured by how many times the player has deployed cards into each grid section. Highlights positional tendencies, for example, whether the player defends centrally or favours a particular lane.

---

## 6. Changed Proposed Features

- **Enemy tower not implemented:** The proposal described a mirrored arena with both a player tower and an enemy tower that the player's units would march toward and destroy, ending the game in a win. The final implementation removes the enemy tower entirely and replaces the win condition with infinite wave survival, the run simply continues until the player's tower falls. This change was made to shift focus onto escalating difficulty and data collection rather than a binary win/lose outcome.

- **Tkinter statistics window instead of in-game stats screen:** The proposal described an in-game statistics overlay. The final implementation moves all statistics into a separate Tkinter window (toggled from the main menu) with tabbed charts. This keeps the in-game ui clean and allows the player to study their data without being in a live match.

---

## 7. External Sources

[Sound Effects from Pixabay](https://pixabay.com/sound-effects/)
[Menu Theme Song by Naktigonis](https://www.youtube.com/watch?v=7iUcvHO1u34&list=PLGt9OOZXqp2JI1vE3olIgOUO-E3PREqRv&index=11)
[In-game Theme Song by Naktigonis](https://www.youtube.com/watch?v=jEufEiXyuxU&list=PLGt9OOZXqp2JI1vE3olIgOUO-E3PREqRv&index=16)
