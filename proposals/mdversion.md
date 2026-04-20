SKE Royale  

By Photsawee Niwadtongrirk  


## 1. Project Overview

SKE Royale is an infinite singleplayer strategy card game that combines deck building mechanics with lane-based tower defense, where players deploy character cards to defend their tower against endless waves of bot enemies until their health pool is depleted.


## 2. Project Review

This project is inspired by the mobile game Clash Royale. While Clash Royale is a competitive multiplayer game with set win/loss conditions based on destroying the opponent's towers, SKE Royale modifies the concept into an endless singleplayer survival game that you can enjoy alone. The project builds upon the original by integrating gameplay analytics, providing players with an end screen summary of their performance (damage dealt, cards played, mana used) and generating post-match statistical analysis of their strategic habits.


## 3. Programming Development


### 3.1 Game Concept

The objective is to survive for as long as possible against infinitely scaling waves of enemies. Players use a continuously regenerating mana pool to play cards that spawn characters to defend their single King Tower. Once the player's tower reaches zero HP, the game ends and it will move to a summary screen displaying total damage dealt, total cards played, and total mana consumed.

Key features that we are measuring in the data analytics tab include real-time resource management, 9-grid positional strategy, and continuous data logging for performance analysis.


### 3.2 Object-Oriented Programming Implementation

The game will implement the following five core classes:

- Character: Represents units on the board. Key attributes include Name, Health, Speed, AttackType (melee, range, summon), and Damage. Its role is to move along the stage and fight enemies.

- Card: Represents the playable deck items. Key attributes include Name, CardImage, Cost, and CharactersToBeSummoned. Its role is to deduct mana and spawn the corresponding Character.

- Tower: Represents the player's defensive structure. Key attributes include Health and TowerImage. Its role is to act as the primary health pool; when its health reaches zero, the infinite run ends.

- ManaManager: Controls the player's economy. Key attributes include CurrentMana, MaxMana, and RegenRate. Its role is to regenerate mana over time and check if a player can afford to play a Card.

- Stage: Represents the game board and wave logic. Key attributes include GridSections (the 9 map sections), ActiveEntities, and WaveNumber. Its role is to handle coordinate positioning, spawn infinite enemy waves, and trigger the end-screen summary.


### 3.3 Algorithms Involved

- Event-Driven Mechanics: The game loop will use event listeners for card selection, grid placement, and mana regeneration.

- Rule-Based Logic: Used for scaling the difficulty of the infinite enemy waves over time.

- Collision Detection and Bots: Pygame's bounding boxes will detect when characters enter attack range of enemies or the tower.


## 4. Statistical Data (Prop Stats)


### 4.1 Data Features

The game will continuously track the following five features throughout the infinite run, ensuring each feature generates well over 100 rows of data:

- Card Play Frequency: How many times each specific card is played.

- Archetype Preference: The frequency of playing melee characters versus ranged characters.

- Tower Damage Events: A log tracking every time the tower takes damage, recording the specific damage amount and timestamp.

- Mana Expenditure: A continuous track of how many times mana is used and the specific cost per action.

- Positional Placement: A log dividing the player's side of the map into 9 sections, tracking the exact grid coordinates where cards are deployed.


### 4.2 Data Recording Method

The statistics will be saved locally into a CSV file. I will make a function that will append new rows to the file continuously as the player survives the infinite waves.


### 4.3 Data Analysis Report

The recorded data will be analyzed using Python's statistical and visualization libraries. The analysis will be presented using:

- Bar Charts: To compare the usage frequency of individual cards and the ratio of melee vs. ranged plays.

- Line Graphs: To illustrate mana usage trends and tower damage taken over the duration of the run.

- Heatmaps: To visually map out the player's most heavily utilized areas across the 9 grid sections.


## 5. Project Planning Timeline

| Week | Task |
|-----|-----|
| Week 8 | Proposal submission / Project initiation |
| Week 9 | Core gameloop setup, Stage (infinite wave logic), and ManaManager |
| Week 10 | Class implementation: Cards, Characters, and Tower |
| Week 11 | Collision logic, combat mechanics, and end screen implementation |
| Week 12 | Implement CSV statistical data collection |
| Week 13 | Data analysis and chart generation |
| Week 14 | Submission week (Draft) |


## 6. Document version

Version: 1.0
Date: 11 March 2026
Editor: Photsawee Niwadtongrirk