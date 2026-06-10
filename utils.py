# filepath: /Users/devangipatel/Downloads/TimeTravelPet/utils.py
import os
import json
import pygame

def load_placeholder(path, size):
    """Load an image and scale, or return a simple placeholder surface."""
    try:
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, size)
    except Exception:
        pass
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((200, 200, 200, 255))
    pygame.draw.rect(surf, (120, 120, 120), surf.get_rect(), 3)
    return surf


def clamp_scroll(scroll, min_v, max_v):
    return max(min_v, min(max_v, scroll))


def save_game(data, username, filename=None):
    """Persist data to data/{username}/save.json by default."""
    try:
        user_dir = os.path.join('data', username)
        os.makedirs(user_dir, exist_ok=True)
        if filename is None:
            filename = os.path.join(user_dir, 'save.json')
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def load_game(username, filename=None):
    """Load and return saved dict for username or None."""
    try:
        if filename is None:
            filename = os.path.join('data', username, 'save.json')
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception:
        return None
    return None


def persist_game_state(username, current_era, unlocked_eras, pet, player):
    os.makedirs(os.path.join('data', username), exist_ok=True)
    save_game({
        'current_era': current_era,
        'unlocked_eras': unlocked_eras,
        'hunger': getattr(pet, 'hunger', 50),
        'happiness': getattr(pet, 'happiness', 50),
        'energy': getattr(pet, 'energy', 50),
        'health': getattr(pet, 'health', 50),
        'credits': getattr(player, 'credits', getattr(player, 'chronocoins', 0)),
        'weekly_budget': getattr(player, 'weekly_budget', getattr(player, 'budget', 0)),
        'budget_spent': getattr(player, 'budget_spent', 0),
        'savings': getattr(player, 'savings', 0)
    }, username)
