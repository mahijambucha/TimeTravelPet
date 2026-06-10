import os

# Era list
eras = ["egypt", "greece", "medieval", "industrial", "modern"]

ERA_DISPLAY_NAMES = {
    "egypt": "Ancient Egypt",
    "greece": "Ancient Greece",
    "medieval": "Medieval Europe",
    "industrial": "Industrial Revolution",
    "modern": "Modern Era"
}

ERA_ACTION_ITEMS = {
    "egypt": {
        "feed": "assets/pets/images/egypt_bread.png",
        "play": "assets/pets/images/egypt_toy.jpeg",
        "rest": "assets/pets/images/egypt_bed.png",
        "clean": "assets/pets/images/egypt_water.png",
        "health": "assets/pets/images/egypt_herbs.png",
    },
    "greece": {
        "feed": "assets/pets/images/greece_grapes.png",
        "play": "assets/pets/images/greece_disc.png",
        "rest": "assets/pets/images/greece_cushion.png",
        "clean": "assets/pets/images/greece_water.png",
        "health": "assets/pets/images/greece_medicine.png"
    },
    "medieval": {
        "feed": "assets/pets/images/medieval_bread.png",
        "play": "assets/pets/images/medieval_ball.png",
        "rest": "assets/pets/images/medieval_strawbed.png",
        "clean": "assets/pets/images/medieval_bucket.png",
        "health": "assets/pets/images/medieval_potion.png"
    },
    "industrial": {
        "feed": "assets/pets/images/industrial_meal.png",
        "play": "assets/pets/images/industrial_toy.png",
        "rest": "assets/pets/images/industrial_bed.png",
        "clean": "assets/pets/images/industrial_tools.png",
        "health": "assets/pets/images/industrial_medicine.png"
    },
    "modern": {
        "feed": "assets/pets/images/modern_food.png",
        "play": "assets/pets/images/modern_game.png",
        "rest": "assets/pets/images/modern_bed.png",
        "clean": "assets/pets/images/modern_cleaner.png",
        "health": "assets/pets/images/modern_medkit.png"
    }
}

era_facts = {
    "egypt": [
        "Egyptians built pyramids using ramps and levers.",
        "Honey was used as a remedy for wounds in ancient Egypt.",
        "Papyrus was used for writing and making toys.",
        "The Nile River's floods made farming possible."
    ],
    "greece": [
        "Ancient Greeks invented the Olympic Games to honor Zeus.",
        "Democracy began in Athens, allowing citizens to vote.",
        "Athletic festivals included running, wrestling, and discus.",
        "Winners were crowned with olive wreaths."
    ],
    "medieval": [
        "Medieval towns had guilds for crafts and trades.",
        "Bread and cheese were staple foods.",
        "Healers used herbs for medicine.",
        "Feudal lords ruled over villages."
    ],
    "industrial": [
        "Steam engines powered trains and factories.",
        "Urbanization changed how people lived.",
        "Working conditions were often harsh.",
        "Vegetable stew was a common meal."
    ],
    "modern": [
        "Technology connects people worldwide.",
        "Modern medicine saves lives.",
        "Environmental awareness is important.",
        "Pets enjoy drone fetch and auto showers!"
    ]
}

ERA_COST_TABLE = {
    "Egypt": {
        "Fish": {"cost": 5, "effect": {"hunger": +15}},
        "Honey Remedy": {"cost": 10, "effect": {"health": +20}},
        "Papyrus Toy": {"cost": 8, "effect": {"happiness": +15}},
        "Nile Bath": {"cost": 12, "effect": {"energy": +20}}
    },
    "Greece": {
        "Olives": {"cost": 6, "effect": {"hunger": +15}},
        "Herbal Ointment": {"cost": 10, "effect": {"health": +20}},
        "Courtyard Mat": {"cost": 8, "effect": {"happiness": +15}},
        "Well Water": {"cost": 10, "effect": {"energy": +20}}
    },
    "Medieval": {
        "Bread & Cheese": {"cost": 6, "effect": {"hunger": +15}},
        "Healer Visit": {"cost": 15, "effect": {"health": +25}},
        "Jousting Game": {"cost": 10, "effect": {"happiness": +20}},
        "Sponge Bath": {"cost": 8, "effect": {"energy": +15}}
    },
    "Industrial": {
        "Vegetable Stew": {"cost": 7, "effect": {"hunger": +15}},
        "Doctor Visit": {"cost": 18, "effect": {"health": +25}},
        "Park Run": {"cost": 10, "effect": {"happiness": +20}},
        "Tin Tub Wash": {"cost": 9, "effect": {"energy": +15}}
    },
    "Modern": {
        "Pet Kibble": {"cost": 8, "effect": {"hunger": +15}},
        "Vet Checkup": {"cost": 20, "effect": {"health": +25}},
        "Drone Fetch": {"cost": 12, "effect": {"happiness": +20}},
        "Auto Shower": {"cost": 10, "effect": {"energy": +15}}
    }
}

COST_TABLE = {
    "Egypt":      {"food": 10, "play": 5,  "clean": 8,  "health": 15},
    "Greece":     {"food": 12, "play": 7,  "clean": 10, "health": 18},
    "Medieval":   {"food": 15, "play": 9,  "clean": 12, "health": 22},
    "Industrial": {"food": 18, "play": 12, "clean": 15, "health": 28},
    "Modern":     {"food": 25, "play": 18, "clean": 20, "health": 35}
}

# ERA_GOALS: each lambda applies a reward to pet/player
ERA_GOALS = {
    "egypt": {
        "name": "Golden Collar",
        "target": 100,
        "reward": "Hunger decay slows by 20%, +5 permanent Health, Feeding gives +5 extra Happiness",
        # reward: slows hunger decay, add permanent health, add feeding happiness bonus
        "apply_reward": lambda pet, player: (setattr(pet, "hunger_decay_bonus", 0.8),
                                             setattr(pet, "permanent_health", getattr(pet, "permanent_health", 0) + 5),
                                             setattr(pet, "feeding_bonus_happiness", 5))
    },
    "greece": {
        "name": "Olympic Training Kit",
        "target": 150,
        "reward": "Playing costs 5 less Energy, Playing gives +5 extra Happiness, +5 permanent Energy",
        # reward: reduce play energy cost, give play happiness bonus, permanent energy
        "apply_reward": lambda pet, player: (setattr(pet, "play_energy_cost_bonus", -5),
                                             setattr(pet, "play_happiness_bonus", 5),
                                             setattr(pet, "permanent_energy", getattr(pet, "permanent_energy", 0) + 5))
    },
    "medieval": {
        "name": "Alchemy Set",
        "target": 200,
        "reward": "Cleaning gives +5 extra Health, Medical care costs 5 fewer coins, +5 permanent Health",
        # reward: clean health bonus, player health cost bonus, permanent pet health
        "apply_reward": lambda pet, player: (setattr(pet, "clean_health_bonus", 5),
                                             setattr(player, "health_cost_bonus", -5),
                                             setattr(pet, "permanent_health", getattr(pet, "permanent_health", 0) + 5))
    },
    "industrial": {
        "name": "Steam Engine Upgrade",
        "target": 250,
        "reward": "Energy decay slows by 20%, Rest restores +5 extra Energy, +5 permanent Energy",
        # reward: energy decay slowdown, rest bonus, permanent energy
        "apply_reward": lambda pet, player: (setattr(pet, "energy_decay_bonus", 0.8),
                                             setattr(pet, "rest_energy_bonus", 5),
                                             setattr(pet, "permanent_energy", getattr(pet, "permanent_energy", 0) + 5))
    },
    "modern": {
        "name": "ai Enhancement Chip",
        "target": 300,
        "reward": "All actions give +2 bonus to their main stat, ai tips more frequent, +5 permanent Happiness",
        # reward: all actions bonus, ai tip bonus, permanent happiness
        "apply_reward": lambda pet, player: (setattr(pet, "all_action_bonus", 2),
                                             setattr(pet, "ai_tip_bonus", True),
                                             setattr(pet, "permanent_happiness", getattr(pet, "permanent_happiness", 0) + 5))
    }
}

MISSIONS = {
    "egypt": [
        {"name": "Collect Stones", "goal": "Click 3 times to collect stones", "type": "small", "progress": 0, "target": 3, "complete": False},
        {"name": "Build Ramp", "goal": "Click wood 2 times to build a ramp", "type": "small", "progress": 0, "target": 2, "complete": False},
        {"name": "Build Pyramid", "goal": "Click brick 5 times to build the pyramid", "type": "main", "progress": 0, "target": 5, "complete": False}
    ],
    "greece": [
        {"name": "Train Running", "goal": "Click shoes 3 times to train running", "type": "small", "progress": 0, "target": 3, "complete": False},
        {"name": "Throw Discus", "goal": "Click discus 2 times to throw discus", "type": "small", "progress": 0, "target": 2, "complete": False},
        {"name": "Win Olympics", "goal": "Click medal 5 times to win Olympics", "type": "main", "progress": 0, "target": 5, "complete": False}
    ],
    "medieval": [
        {"name": "Gather Herbs", "goal": "Click herbs 3 times to gather herbs", "type": "small", "progress": 0, "target": 3, "complete": False},
        {"name": "Mix Potions", "goal": "Click potions 2 times to mix potions", "type": "small", "progress": 0, "target": 2, "complete": False},
        {"name": "Craft Festival Potion", "goal": "Click wand 5 times to craft the potion", "type": "main", "progress": 0, "target": 5, "complete": False}
    ],
    "industrial": [
        {"name": "Collect Coal", "goal": "Click coal 3 times to collect coal", "type": "small", "progress": 0, "target": 3, "complete": False},
        {"name": "Repair Gear", "goal": "Click gear 2 times to repair gears", "type": "small", "progress": 0, "target": 2, "complete": False},
        {"name": "Fix Steam Engine", "goal": "Click engine 5 times to fix engine", "type": "main", "progress": 0, "target": 5, "complete": False}
    ],
    "modern": [
        {"name": "Collect Data", "goal": "Click graph 3 times to collect data", "type": "small", "progress": 0, "target": 3, "complete": False},
        {"name": "Prepare Slides", "goal": "Click projector 2 times to prepare slides", "type": "small", "progress": 0, "target": 2, "complete": False},
        {"name": "Present Timeline", "goal": "Click graph 5 times to present timeline", "type": "main", "progress": 0, "target": 5, "complete": False}
    ]
}