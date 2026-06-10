# Time Travel Pet

**Time Travel Pet** is an educational and interactive pet care game where you raise a virtual pet through five historical eras: Ancient Egypt, Ancient Greece, Medieval Europe, the Industrial Revolution, and the Modern Era. Each era features unique items, missions, and lessons that teach players about history, budgeting, and responsible care.

## Features

- **Pet Care Simulation:** Feed, play, clean, heal, and rest your pet, with actions and items changing by era.
- **Era Progression:** Unlock new eras by completing missions and maintaining your pet’s well-being.
- **Savings & Budget System:** Earn and spend ChronoCoins, manage a weekly budget, and set savings goals for permanent bonuses.
- **Missions & Rewards:** Complete era-specific missions to earn coins, unlock new eras, and evolve your pet.
- **Educational Content:** Each era includes historical facts and a lesson connecting history to gameplay.
- **Reports & Diary:** Track your actions, spending, and progress in a diary. Generate custom reports to analyze your play style.
- **Customizable Experience:** Choose your character, pet species, and pet name at the start of the game.
- **AI Tips:** Get helpful suggestions if your pet’s stats drop too low or if you overspend.

## How This Addresses the FBLA Prompt

**Virtual pet with naming and customization:** Players name their pet, choose a species (dog, cat, bird, rabbit), and select a player avatar at the start of the game.

**Pet care features:** All five required actions are implemented — Feed, Play, Rest, Clean, and Health Check — each with era-specific items and costs that change across all five historical eras.

**Reactions based on care level:** The pet's mood updates dynamically based on stat thresholds. Four states are implemented — happy, sad, sick, and energetic — each mapped to a distinct sprite for every pet species.

**Cost of care system:** Every action deducts ChronoCoins. Costs increase across eras (e.g., food costs 10 coins in Ancient Egypt and 25 coins in the Modern Era) to reflect real-world inflation and increasing cost of living.

**Running expense total:** The Diary and Financial Summary screens track all spending by action category and by era, giving the player a full breakdown of where their coins went.

**Savings goals:** Each era has a savings target with a permanent pet stat bonus as the reward, teaching players the value of delayed gratification and financial planning.

**Earning system:** Completing era missions rewards 50–100 ChronoCoins. Maintaining all pet stats above 70 awards a bonus coin reward, encouraging consistent responsible care.

**Pet development:** The pet evolves visually and mechanically through five historical eras. Completing all three missions per era unlocks the next era and triggers a personalized progress summary.


## Game Structure

- **main.py:** Main game loop, UI rendering, and core logic.
- **classes/**: Contains class definitions for `Player`, `Pet`, `Diary`, and `PetML`.
- **assets/**: Images for backgrounds, items, pets, and UI.
- **data/**: Stores save files and summaries in JSON format.

## How to Play

1. **Start the Game:** Launch the game and select your character and pet.
2. **Care for Your Pet:** Use the action buttons to feed, play, clean, heal, and rest your pet. Monitor their stats and happiness.
3. **Complete Missions:** Each era has unique missions. Complete them to earn coins and unlock the next era.
4. **Manage Your Budget:** Earn ChronoCoins, spend wisely, and deposit savings to reach era-specific goals for permanent bonuses.
5. **Learn History:** Read era facts and lessons to connect gameplay with real historical concepts.
6. **Track Progress:** Use the diary and custom report screens to review your actions and spending.

## Controls

- **Mouse:** Click buttons and interactive objects.
- **Keyboard:** Use arrow keys to scroll in reports and popups. Press `Esc` to exit screens.
- **Navigation:** Use on-screen navigation buttons for Home and Start.

## Project Structure

```
.
├── main.py
├── diary.py
├── player.py
├── classes/
│   ├── diary.py
│   ├── pet.py
│   ├── player.py
│   └── pet_ml.py
├── assets/
│   ├── backgrounds/
│   ├── items/
│   ├── pets/
│   └── player/
├── data/
│   ├── diary.json
│   ├── era_summaries.json
│   ├── finance.json
│   └── save.json
├── README.md
└── project.docx
```

## Requirements

- Python 3.10+
- [pygame](https://www.pygame.org/) library

Install dependencies with:

```sh
pip install pygame
```

## Running the Game

Run the main script:

```sh
python main.py
```

## Educational Goals

- Teach players about historical eras and their innovations.
- Encourage responsible budgeting and saving.
- Promote balanced decision-making and care.

---

Enjoy raising your pet through time and learning history along the way!