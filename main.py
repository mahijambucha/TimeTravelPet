# ============================================================
# Imports & Initialization
    #- Imports all required external libraries.
    #- Imports custom game classes (Player, Pet, Diary, Petml).
    #- Initializes pygame.
    #- Sets up window, display settings, font, and clock.

# ============================================================
import pygame
import sys
import os
import random
import json
import datetime
import math

from classes.player import Player
from classes.pet import Pet
from classes.diary import Diary
from classes.pet_ml import Petml

pygame.init()
# Initialize mixer and preload error sound (optional). Safe-fail if audio unavailable.
try:
    pygame.mixer.init()
except Exception:
    pass
ERROR_SOUND = None
try:
    err_path = os.path.join("assets", "sounds", "wrong.mp3")
    if os.path.exists(err_path):
        ERROR_SOUND = pygame.mixer.Sound(err_path)
except Exception:
    ERROR_SOUND = None

def play_error_sound():
    """Play a short error sound if available (safe no-op otherwise)."""
    global ERROR_SOUND
    try:
        if ERROR_SOUND:
            ERROR_SOUND.play()
    except Exception:
        pass
# Initialize mixer and preload confirm sound (safe no-op if audio unavailable)
try:
    pygame.mixer.init()
except Exception:
    pass
CONFIRM_SOUND = None
try:
    confirm_path = os.path.join("assets", "sounds", "correct.mp3")
    if os.path.exists(confirm_path):
        CONFIRM_SOUND = pygame.mixer.Sound(confirm_path)
except Exception:
    CONFIRM_SOUND = None

def play_confirm_sound():
    """Play confirm/continue/start sound if available (no-op on error)."""
    global CONFIRM_SOUND
    try:
        if CONFIRM_SOUND:
            CONFIRM_SOUND.play()
    except Exception:
        pass
WIDTH, HEIGHT = 960, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Time Travel Pet")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)



# ============================================================
# Utility Functions
   # - Handle reusable operations (image loading, saving, scrolling).
   # - Prevent code duplication across the program.
   #- Improve readability by isolating repeated logic.
# ============================================================
def load_placeholder(path, size):
    # ============================================================
    # If the file does not exist or fails to load:
    # - Returns a visually styled placeholder surface.
    # - Prevents the program from crashing due to missing assets.
    # ============================================================
    try:
        print("Trying to load:", path)
        if os.path.exists(path):
            img = pygame.image.load(path)
            return pygame.transform.scale(img, size)
    except Exception as e:
        print(f"Failed to load {path}: {e}")
    surf = pygame.Surface(size)
    surf.fill((181, 101, 29))
    pygame.draw.rect(surf, (100,100,100), surf.get_rect(), 4)
    return surf

def clamp_scroll(scroll, total_height, screen_height):
    """Clamp scroll value to content height."""
    return min(max(scroll, 0), max(0, total_height - screen_height))

# Per-user save/load helpers
def save_game(data, username):
    path = f"data/{username}"
    os.makedirs(path, exist_ok=True)
    with open(f"{path}/save.json", "w") as f:
        json.dump(data, f, indent=2)

def load_game(username):
    path = f"data/{username}/save.json"
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None
def persist_game_state(username, current_era, unlocked_eras, pet, player):
    os.makedirs(f"data/{username}", exist_ok=True)
    save_game({
        "current_era": current_era,
        "unlocked_eras": unlocked_eras,
        "hunger": pet.hunger,
        "happiness": pet.happiness,
        "energy": pet.energy,
        "health": pet.health,
        "credits": getattr(player, "credits", getattr(player, "chronocoins", 0)),
        "weekly_budget": getattr(player, "weekly_budget", getattr(player, "budget", 0)),
        "budget_spent": getattr(player, "budget_spent", 0),
        "savings": getattr(player, "savings", 0)
    }, username)
    
# Login screen (returns chosen username string)
# ...existing code...
def login_screen(screen, font):
    import os
    import hashlib
    WIDTH, HEIGHT = screen.get_size()

    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    label_font = pygame.font.SysFont("Arial", 20)
    btn_font = pygame.font.SysFont("Arial", 20, bold=True)

    # Visual constants (baby-blue / pastel)
    BG_COLOR = (200, 230, 255)
    CIRCLE_COLOR = (225, 243, 255)
    TITLE_COLOR = (100, 70, 160)
    LABEL_COLOR = (40, 80, 140)
    INPUT_BORDER = (210, 160, 190)
    WARN_COLOR = (255, 127, 80)
    SHADOW = (170, 190, 215)
    START_BG = (240, 248, 255)
    START_ACCENT = (80, 160, 220)
    START_BORDER = (255, 221, 51)

    # Load existing users
    existing_users = []
    if os.path.exists("data"):
        for name in sorted(os.listdir("data")):
            if os.path.isdir(os.path.join("data", name)):
                existing_users.append(name)

    # State
    username_input = ""
    password_input = ""
    mode = "choose"
    selected_returning = None
    warn_msg = ""
    attempts = {}
    username_active = False
    password_active = False
    if not existing_users:
        mode = "new"
        username_active = True

    def cursor_visible():
        return (pygame.time.get_ticks() // 500) % 2 == 0

    def draw_input_box(rect, text, active=False, password=False, placeholder=""):
        shadow_rect = rect.move(4, 8)
        pygame.draw.rect(screen, SHADOW, shadow_rect, border_radius=14)
        pygame.draw.rect(screen, (255,255,255), rect, border_radius=14)
        pygame.draw.rect(screen, INPUT_BORDER, rect, 2, border_radius=14)
        display = text if text else placeholder
        if password and text:
            display = "*" * len(text)
        color = (0,0,0) if text else (120,120,120)
        txt_surf = label_font.render(display, True, color)
        screen.blit(txt_surf, (rect.x + 14, rect.y + rect.h//2 - txt_surf.get_height()//2))
        if active and cursor_visible():
            caret_x = rect.x + 14 + txt_surf.get_width() + 2
            caret_y1 = rect.y + 8
            caret_y2 = rect.y + rect.h - 8
            pygame.draw.line(screen, (0,0,0), (caret_x, caret_y1), (caret_x, caret_y2), 2)

    # Layout tuning: much more vertical spacing
    content_w = min(860, WIDTH - 160)
    top_margin = 80
    spacing = 36
    input_h = 52
    input_w = min(520, content_w)

    while True:
        screen.fill(BG_COLOR)
        WIDTH, HEIGHT = screen.get_size()

        # Soft circle behind content (centered)
        pygame.draw.circle(screen, CIRCLE_COLOR, (WIDTH//2, HEIGHT//2 - 20), 320)

        # Title
        title = title_font.render("Time Travel Pet", True, TITLE_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, top_margin - 24))

        # Vertical layout start (centered column)
        cx = WIDTH // 2
        y = top_margin + title.get_height()

        # Returning profiles grid (two rows)
        profile_rects = []
        if mode == "choose" and existing_users:
            lbl = label_font.render("Returning player? Select your profile:", True, LABEL_COLOR)
            screen.blit(lbl, (cx - lbl.get_width()//2, y))
            y += lbl.get_height() + spacing

            cols = min(4, max(1, len(existing_users)))
            rows = min(2, math.ceil(len(existing_users) / cols))
            bw, bh = 180, 56
            grid_w = cols * bw + (cols - 1) * 16
            start_x = cx - grid_w//2
            for idx, name in enumerate(existing_users):
                r = idx // cols
                c = idx % cols
                bx = start_x + c * (bw + 16)
                by = y + r * (bh + 16)
                rect = pygame.Rect(bx, by, bw, bh)
                profile_rects.append((rect, name))
                pygame.draw.rect(screen, SHADOW, rect.move(4,8), border_radius=12)
                pygame.draw.rect(screen, (90,150,200), rect, border_radius=12)
                pygame.draw.rect(screen, (120,205,230), rect, 2, border_radius=12)
                txt = btn_font.render(name.capitalize(), True, (255,255,255))
                screen.blit(txt, (rect.x + rect.w//2 - txt.get_width()//2, rect.y + rect.h//2 - txt.get_height()//2))
            y += rows * (bh + 16) + spacing

        # New / Returning area (centered column, stacked inputs)
        block_x = cx - input_w//2

        if mode == "returning" and selected_returning:
            welcome = label_font.render(f"Welcome back, {selected_returning.capitalize()}!", True, LABEL_COLOR)
            prompt = label_font.render("Enter your password:", True, LABEL_COLOR)
            screen.blit(welcome, (cx - welcome.get_width()//2, y))
            y += welcome.get_height() + 8
            screen.blit(prompt, (cx - prompt.get_width()//2, y))
            y += prompt.get_height() + 12

            pass_box = pygame.Rect(block_x, y, input_w, input_h)
            draw_input_box(pass_box, password_input, active=password_active or True, password=True, placeholder="Password")
            y += input_h + spacing

            # Login button (centered)
            login_rect = pygame.Rect(cx - 120, y, 240, 56)
            pygame.draw.rect(screen, (0,150,100), login_rect, border_radius=28)
            pygame.draw.rect(screen, (100,230,220), login_rect, 3, border_radius=28)
            login_txt = btn_font.render("Log In", True, (255,255,255))
            screen.blit(login_txt, (login_rect.x + login_rect.w//2 - login_txt.get_width()//2, login_rect.y + login_rect.h//2 - login_txt.get_height()//2))
            y += login_rect.h + spacing

            if attempts.get(selected_returning, 0) >= 5:
                warn_msg = "Too many failed attempts. Please restart the game."

        else:
            # New player stacked inputs with larger vertical spacing
            new_lbl = label_font.render("New player? Create an account:", True, LABEL_COLOR)
            screen.blit(new_lbl, (cx - new_lbl.get_width()//2, y))
            y += new_lbl.get_height() + spacing

            # Username (stacked)
            user_lbl = label_font.render("Username:", True, LABEL_COLOR)
            screen.blit(user_lbl, (block_x, y))
            y += user_lbl.get_height() + 6
            user_box = pygame.Rect(block_x, y, input_w, input_h)
            draw_input_box(user_box, username_input, active=username_active, password=False, placeholder="Letters only")
            y += input_h + spacing

            pass_lbl = label_font.render("Password:", True, LABEL_COLOR)
            screen.blit(pass_lbl, (block_x, y))
            y += pass_lbl.get_height() + 6
            pass_box = pygame.Rect(block_x, y, input_w, input_h)
            draw_input_box(pass_box, password_input, active=password_active, password=True, placeholder="Password")
            y += input_h + spacing

            # Create account button
            create_rect = pygame.Rect(cx - 140, y, 280, 60)
            pygame.draw.rect(screen, (0,140,110), create_rect, border_radius=30)
            pygame.draw.rect(screen, (100,230,220), create_rect, 3, border_radius=30)
            c_txt = btn_font.render("Create Account", True, (255,255,255))
            screen.blit(c_txt, (create_rect.x + create_rect.w//2 - c_txt.get_width()//2, create_rect.y + create_rect.h//2 - c_txt.get_height()//2))
            y += create_rect.h + spacing

        # Improved "Start Without Login" pill (drop shadow + accent)
        start_pill_w, start_pill_h = 260, 56
        start_pill_x = WIDTH - start_pill_w - 28
        start_pill_y = HEIGHT - start_pill_h - 28
        shadow = pygame.Rect(start_pill_x + 6, start_pill_y + 8, start_pill_w, start_pill_h)
        pygame.draw.rect(screen, (150, 170, 190), shadow, border_radius=40)
        pill = pygame.Rect(start_pill_x, start_pill_y, start_pill_w, start_pill_h)
        pygame.draw.rect(screen, START_BG, pill, border_radius=40)
        pygame.draw.rect(screen, START_ACCENT, pill, 3, border_radius=40)
        # little icon circle
        icon_r = 18
        icon_rect = pygame.Rect(pill.x + 14, pill.y + (pill.h - icon_r*2)//2, icon_r*2, icon_r*2)
        pygame.draw.circle(screen, START_ACCENT, icon_rect.center, icon_r)
        pygame.draw.circle(screen, START_BORDER, icon_rect.center, icon_r, 2)
        # text
        start_txt = btn_font.render("Start Without Login", True, (30,30,30))
        screen.blit(start_txt, (pill.x + 14 + icon_r*2 + 12, pill.y + pill.h//2 - start_txt.get_height()//2))

        # Warning text under the content area
        if warn_msg:
            wsurf = label_font.render(warn_msg, True, WARN_COLOR)
            screen.blit(wsurf, (cx - wsurf.get_width()//2, y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                # Start without login pill
                if pill.collidepoint(pos):
                    return None
                # Profile grid clicks
                if mode == "choose" and profile_rects:
                    for rect, name in profile_rects:
                        if rect.collidepoint(pos):
                            selected_returning = name
                            password_input = ""
                            warn_msg = ""
                            mode = "returning"
                            username_active = False
                            password_active = True
                            break
                    # click roughly in new area to switch to create
                    create_area = pygame.Rect(cx - input_w//2, top_margin + 180, input_w, 160)
                    if create_area.collidepoint(pos):
                        mode = "new"
                        username_input = ""
                        password_input = ""
                        warn_msg = ""
                        username_active = True
                        password_active = False
                        continue

                # Returning user login click
                if mode == "returning" and selected_returning:
                    login_rect = pygame.Rect(cx - 120, y - spacing - 56, 240, 56)  # login button location computed earlier
                    if login_rect.collidepoint(pos) and attempts.get(selected_returning, 0) < 5:
                        acct_path = os.path.join("data", selected_returning, "account.json")
                        try:
                            with open(acct_path, "r") as f:
                                acct = json.load(f)
                            stored = acct.get("password_hash", "")
                            typed_hash = hashlib.sha256(password_input.strip().encode()).hexdigest()
                            if typed_hash == stored:
                                return selected_returning
                            else:
                                attempts[selected_returning] = attempts.get(selected_returning, 0) + 1
                                if attempts[selected_returning] >= 5:
                                    warn_msg = "Too many failed attempts. Please restart the game."
                                else:
                                    warn_msg = "Incorrect password. Try again."
                                password_input = ""
                        except Exception:
                            warn_msg = "Account file missing or corrupted."
                    # clicking left area returns to create/new
                    if pygame.Rect(block_x, top_margin + 180, input_w, 40).collidepoint(pos):
                        mode = "new"
                        username_input = ""
                        password_input = ""
                        username_active = True
                        password_active = False

                # New-account clicks: activate stacked inputs or create
                if mode != "returning":
                    user_box = pygame.Rect(block_x, top_margin + title.get_height() + 60 + (0 if not profile_rects else len(profile_rects)*10), input_w, input_h)
                    user_box = pygame.Rect(block_x, y - (input_h + spacing)*3, input_w, input_h)  # safe fallback region
                    # precise boxes (recompute local positions for reliable clicks)
                    # easier: hit test on visible input rectangles by re-creating them
                    # Username location:
                    cursor_y = top_margin + title.get_height()
                    if mode == "choose" and existing_users:
                        cursor_y += lbl.get_height() + spacing
                        rows = min(2, math.ceil(len(existing_users) / min(4, max(1, len(existing_users)))))
                        cursor_y += rows * (56 + 16) + spacing
                    # new area boxes positions (stacked)
                    u_box = pygame.Rect(block_x, cursor_y + new_lbl.get_height() + spacing, input_w, input_h)
                    p_box = pygame.Rect(block_x, u_box.y + input_h + spacing + label_font.get_height() + 6, input_w, input_h)
                    create_rect = pygame.Rect(cx - 140, p_box.y + input_h + spacing, 280, 60)
                    if u_box.collidepoint(pos):
                        username_active = True; password_active = False
                    elif p_box.collidepoint(pos):
                        password_active = True; username_active = False
                    elif create_rect.collidepoint(pos):
                        name = username_input.strip().lower()
                        pw = password_input
                        if len(name) < 2 or not name.isalpha():
                            warn_msg = "Username must be letters only, at least 2 characters."
                            continue
                        if len(pw) < 4:
                            warn_msg = "Password must be at least 4 characters."
                            password_input = ""
                            continue
                        user_dir = os.path.join("data", name)
                        if os.path.exists(user_dir):
                            warn_msg = "Username already taken. Please choose another."
                            continue
                        try:
                            os.makedirs(user_dir, exist_ok=True)
                            acct = {"username": name, "password_hash": hashlib.sha256(pw.strip().encode()).hexdigest()}
                            with open(os.path.join(user_dir, "account.json"), "w") as f:
                                json.dump(acct, f)
                            return name
                        except Exception:
                            warn_msg = "Failed to create account. Check permissions."

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_TAB:
                    username_active, password_active = (not username_active), (not password_active)
                    continue

                if mode == "returning" and selected_returning:
                    if attempts.get(selected_returning, 0) >= 5:
                        continue
                    if event.key == pygame.K_RETURN:
                        acct_path = os.path.join("data", selected_returning, "account.json")
                        try:
                            with open(acct_path, "r") as f:
                                acct = json.load(f)
                            stored = acct.get("password_hash", "")
                            typed_hash = hashlib.sha256(password_input.strip().encode()).hexdigest()
                            if typed_hash == stored:
                                return selected_returning
                            else:
                                attempts[selected_returning] = attempts.get(selected_returning, 0) + 1
                                if attempts[selected_returning] >= 5:
                                    warn_msg = "Too many failed attempts. Please restart the game."
                                else:
                                    warn_msg = "Incorrect password. Try again."
                                password_input = ""
                        except Exception:
                            warn_msg = "Account file missing or corrupted."
                    elif event.key == pygame.K_BACKSPACE:
                        password_input = password_input[:-1]
                    else:
                        if event.unicode and len(password_input) < 64:
                            password_input += event.unicode
                else:
                    if event.key == pygame.K_RETURN:
                        name = username_input.strip().lower()
                        pw = password_input
                        if len(name) < 2 or not name.isalpha():
                            warn_msg = "Username must be letters only, at least 2 characters."
                            continue
                        if len(pw) < 4:
                            warn_msg = "Password must be at least 4 characters."
                            password_input = ""
                            continue
                        user_dir = os.path.join("data", name)
                        if os.path.exists(user_dir):
                            warn_msg = "Username already taken. Please choose another."
                            continue
                        try:
                            os.makedirs(user_dir, exist_ok=True)
                            acct = {"username": name, "password_hash": hashlib.sha256(pw.strip().encode()).hexdigest()}
                            with open(os.path.join(user_dir, "account.json"), "w") as f:
                                json.dump(acct, f)
                            return name
                        except Exception:
                            warn_msg = "Failed to create account. Check permissions."
                    elif event.key == pygame.K_BACKSPACE:
                        if password_active and password_input:
                            password_input = password_input[:-1]
                        elif username_active and username_input:
                            username_input = username_input[:-1]
                    else:
                        ch = event.unicode
                        if ch:
                            if username_active:
                                if ch.isalpha() and len(username_input) < 16:
                                    username_input += ch
                            elif password_active:
                                if len(password_input) < 64 and 32 <= ord(ch) <= 126:
                                    password_input += ch
                            else:
                                if ch.isalpha() and len(username_input) < 16:
                                    username_input += ch
                                elif len(password_input) < 64 and 32 <= ord(ch) <= 126:
                                    password_input += ch
        # redraw loop continues
# Call login screen and then initialize per-user state
username = login_screen(screen, font)

# Instantiate diary per user
diary = Diary(username=username)
# ...existing code...
# ================================================
# Game Data & Constants
    #- Era lists
    #- Item data
    #- Arrays
    #- Cost tables
    #- Missions
    #- Rewards
    #- Educational lesson content

    #Benefits:
    #- Keeps configuration separate from logic.
    #- Makes balancing or editing easier.
    #- Improves readability and scalability.
    #- Demonstrates strong program organization.
# ============================================================
eras = ["egypt", "greece", "medieval", "industrial", "modern"]
era_items = {
    "egypt": ["bread", "honey remedy", "papyrus toy", "nile bath"],
    "greece": ["olives", "herbal salve", "discus toy", "spring bath"],
    "medieval": ["bread & cheese", "sponge bath", "jousting game", "healer visit"],
    "industrial": ["vegetable stew", "tin tub wash", "park run", "doctor visit"],
    "modern": ["pet kibble", "auto shower", "drone fetch", "vet checkup"]
}
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
era_costs = {
    "egypt": [5, 8, 4, 6],
    "greece": [6, 9, 5, 7],
    "medieval": [7, 10, 6, 8],
    "industrial": [8, 12, 7, 9],
    "modern": [10, 15, 8, 12]
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

COST_TABLE = {
    "Egypt":      {"food": 10, "play": 5,  "clean": 8,  "health": 15},
    "Greece":     {"food": 12, "play": 7,  "clean": 10, "health": 18},
    "Medieval":   {"food": 15, "play": 9,  "clean": 12, "health": 22},
    "Industrial": {"food": 18, "play": 12, "clean": 15, "health": 28},
    "Modern":     {"food": 25, "play": 18, "clean": 20, "health": 35}
}

ERA_GOALS = {
    # ============================================================
    # Defines:
    #   - Savings target per era.
    #   - Reward name.
    #   - Permanent gameplay bonuses.
    #   - Lambda-based reward application.
    # ============================================================
    "egypt": {
        "name": "Golden Collar",
        "target": 100,
        "reward": "Hunger decay slows by 20%, +5 permanent Health, Feeding gives +5 extra Happiness",
        "apply_reward": lambda pet, player: (
            setattr(pet, "hunger_decay_bonus", 0.8),
            setattr(pet, "permanent_health", getattr(pet, "permanent_health", 0) + 5),
            setattr(pet, "feeding_bonus_happiness", 5)
        )
    },
    "greece": {
        "name": "Olympic Training Kit",
        "target": 150,
        "reward": "Playing costs 5 less Energy, Playing gives +5 extra Happiness, +5 permanent Energy",
        "apply_reward": lambda pet, player: (
            setattr(pet, "play_energy_cost_bonus", -5),
            setattr(pet, "play_happiness_bonus", 5),
            setattr(pet, "permanent_energy", getattr(pet, "permanent_energy", 0) + 5)
        )
    },
    "medieval": {
        "name": "Alchemy Set",
        "target": 200,
        "reward": "Cleaning gives +5 extra Health, Medical care costs 5 fewer coins, +5 permanent Health",
        "apply_reward": lambda pet, player: (
            setattr(pet, "clean_health_bonus", 5),
            setattr(player, "health_cost_bonus", -5),
            setattr(pet, "permanent_health", getattr(pet, "permanent_health", 0) + 5)
        )
    },
    "industrial": {
        "name": "Steam Engine Upgrade",
        "target": 250,
        "reward": "Energy decay slows by 20%, Rest restores +5 extra Energy, +5 permanent Energy",
        "apply_reward": lambda pet, player: (
            setattr(pet, "energy_decay_bonus", 0.8),
            setattr(pet, "rest_energy_bonus", 5),
            setattr(pet, "permanent_energy", getattr(pet, "permanent_energy", 0) + 5)
        )
    },
    "modern": {
        "name": "ai Enhancement Chip",
        "target": 300,
        "reward": "All actions give +2 bonus to their main stat, ai tips more frequent, +5 permanent Happiness",
        "apply_reward": lambda pet, player: (
            setattr(pet, "all_action_bonus", 2),
            setattr(pet, "ai_tip_bonus", True),
            setattr(pet, "permanent_happiness", getattr(pet, "permanent_happiness", 0) + 5)
        )
    }
}

ERA_LESSONS = {
    # ============================================================
    # Each entry includes:
    #    - Title
    #    - Historical explanation
    #    - Explicit connection to gameplay mechanics
    # ============================================================
    "egypt": {
        "title": "Engineering the Pyramids",
        "lesson_text": (
            "Ancient Egyptians built massive pyramids using advanced engineering techniques. "
            "Workers transported stone blocks along the Nile River and used ramps to lift materials. "
            "Agriculture thrived because the Nile flooded yearly, providing fertile soil. "
            "Early medicine used herbs and honey as treatments."
        ),
        "gameplay_connection": (
            "Managing food and resources reflects how Egyptians depended on planning and engineering to survive."
        )
    },
    "greece": {
        "title": "Democracy and the Olympics",
        "lesson_text": (
            "Ancient Greece introduced early democracy where citizens voted on decisions. "
            "City-states valued philosophy, athletics, and civic duty. The Olympic Games celebrated discipline and strength. "
            "Education and balanced thinking were important in Greek society."
        ),
        "gameplay_connection": (
            "Training and competing in mini-Olympics reflects Greek values of discipline and civic pride."
        )
    },
    "medieval": {
        "title": "Feudal Society and Medieval Life",
        "lesson_text": (
            "Medieval Europe operated under a feudal system where kings granted land to nobles, who relied on knights and peasants. "
            "Most people worked in agriculture. Medicine used herbal remedies and superstition. Guilds controlled trades and crafts."
        ),
        "gameplay_connection": (
            "Crafting potions and managing resources reflects medieval reliance on herbs and local healers."
        )
    },
    "industrial": {
        "title": "Industry and Urban Growth",
        "lesson_text": (
            "The Industrial Revolution transformed society through machines, factories, and steam power. "
            "Cities expanded as people moved for jobs. Working conditions were often harsh, but innovation improved transportation and manufacturing."
        ),
        "gameplay_connection": (
            "Repairing engines and managing energy reflects industrial innovation and labor demands."
        )
    },
    "modern": {
        "title": "Technology and Global Responsibility",
        "lesson_text": (
            "The modern era is defined by digital communication, artificial intelligence, and global connection. "
            "Advances in medicine and environmental awareness shape society. Balancing innovation with sustainability is essential."
        ),
        "gameplay_connection": (
            "Stabilizing the time core and analyzing data reflects modern reliance on technology and information systems."
        )
    }
}
# ============================================================
# UI Rendering & Navigation
    # All user interface screens and navigation systems are
    # defined in this section.
    #
    # Each function:
    # - Has a single responsibility.
    # - Handles its own rendering loop.
    # - Manages input locally.
    # - Returns cleanly to main loop when complete.
# ============================================================ 
def draw_nav_buttons(screen, show_home=True, show_start=True):
    WIDTH, HEIGHT = screen.get_size()
    btn_w, btn_h = 80, 36
    gap = 12
    font = pygame.font.SysFont("Arial", 18, bold=True)
    buttons = {}
    if show_home:
        home_rect = pygame.Rect(WIDTH - btn_w*2 - gap*2, gap, btn_w, btn_h)
        pygame.draw.rect(screen, (200,230,255), home_rect, border_radius=10)
        pygame.draw.rect(screen, (80,120,200), home_rect, 2, border_radius=10)
        home_txt = font.render("Home", True, (0,0,80))
        screen.blit(home_txt, (home_rect.x + (btn_w-home_txt.get_width())//2, home_rect.y + (btn_h-home_txt.get_height())//2))
        buttons["home"] = home_rect
    if show_start:
        # Place Start next to Map at the bottom right
        start_rect = pygame.Rect(WIDTH - 120, HEIGHT - 60, 100, 44)
        pygame.draw.rect(screen, (255,230,200), start_rect, border_radius=10)
        pygame.draw.rect(screen, (200,120,80), start_rect, 2, border_radius=10)
        start_txt = font.render("Restart", True, (80,40,0))
        screen.blit(start_txt, (start_rect.x + (100-start_txt.get_width())//2, start_rect.y + (44-start_txt.get_height())//2))
        buttons["start"] = start_rect
    return buttons

def show_pet_care_guide(screen, font, pet, player, eras, current_era):
    # ============================================================ 
    # Includes:
    # - Stat recommendations.
    # - Action frequency guidance.
    # - Current era modifiers.
    # - Savings goal progress bar.
    # ============================================================ 
    WIDTH, HEIGHT = screen.get_size()
    scroll = 0
    small_font = pygame.font.SysFont("Arial", 18)
    title_font = pygame.font.SysFont("Arial", 28, bold=True)
    section_font = pygame.font.SysFont("Arial", 22, bold=True)
    text_font = pygame.font.SysFont("Arial", 20)

    # --- Dynamic era needs ---
    era_idx = current_era if isinstance(current_era, int) else getattr(pet, "era_level", 0)
    if not (0 <= era_idx < len(eras)):
        era_idx = getattr(pet, "era_level", 0)
    needs = pet.needs_by_era[era_idx]
    stat_cap = needs["stat_cap"]
    hunger_rate = needs["hunger_rate"]
    energy_rate = needs["energy_rate"]

    # --- Pet Care Instructions ---
    lines = [
        (title_font, "How to Care for Your Pet", (80, 60, 0)),
        (text_font, ""),
        (section_font, "Ideal Stat Ranges", (0, 80, 120)),
        (text_font, "  Hunger: 50–90"),
        (text_font, "  Happiness: Above 60"),
        (text_font, "  Energy: Above 40"),
        (text_font, "  Health: Above 70"),
        (text_font, ""),
        (section_font, "Recommended Action Frequency", (0, 80, 120)),
        (section_font, "Feed:", (0, 80, 120)),
        (text_font, "  - When hunger < 50"),
        (text_font, "  - 2–3 times per day"),
        (text_font, "  - Overfeeding above 90 reduces health slightly"),
        (section_font, "Play:", (0, 80, 120)),
        (text_font, "  - When happiness < 60"),
        (text_font, "  - 1–2 times per day"),
        (text_font, "  - Do not play if energy < 30"),
        (section_font, "Rest:", (0, 80, 120)),
        (text_font, "  - When energy < 40"),
        (text_font, "  - At least once per day"),
        (section_font, "Clean:", (0, 80, 120)),
        (text_font, "  - Every 2–3 days"),
        (text_font, "  - Required if health < 70"),
        (section_font, "Health Care:", (0, 80, 120)),
        (text_font, "  - Only when health < 50"),
        (text_font, "  - Costs coins"),
        (text_font, ""),
        (section_font, "What You Should Learn", (120, 60, 0)),
        (text_font, "Balance!"),
        (text_font, "Play too much → pet gets hungry + tired"),
        (text_font, "Feed too much → pet becomes unhealthy"),
        (text_font, "Never clean → health slowly drains"),
        (text_font, "Never rest → mood becomes sad"),
        (text_font, ""),
        (section_font, f"Current Era: {ERA_DISPLAY_NAMES.get(eras[era_idx], eras[era_idx].capitalize())}", (0, 80, 120)),
        (text_font, f"Stat Cap: {stat_cap}"),
        (text_font, f"Hunger decreases at {hunger_rate}x speed"),
        (text_font, f"Energy decreases at {energy_rate}x speed"),
        (text_font, ""),
    ]

    # --- Savings Goal Section as lines (use canonical savings fields) ---
    goal = ERA_GOALS[eras[era_idx]]
    targ = getattr(player, "savings_goal_target", getattr(player, "goal_target_amount", goal.get("target", 100)))
    prog = getattr(player, "savings", getattr(player, "goal_progress", 0))
    goal_lines = [
        (section_font, "Savings Goal", (180, 140, 0)),
        (text_font, f"  Goal: {goal['name']}"),
        (text_font, f"  Target: {targ} ChronoCoins"),
        (text_font, f"  Your Progress: {prog} / {targ}"),
        (text_font, f"  Reward: {goal['reward']}"),
        (text_font, "  Earn coins by caring for your pet and completing missions."),
        (text_font, "  When you reach your goal, your pet gets a permanent bonus!"),
        (text_font, ""),  # Spacer
    ]

    # Combine all lines for scrolling
    all_lines = lines + goal_lines

    # Pre-render all lines for consistent spacing
    rendered_lines = []
    for entry in all_lines:
        if len(entry) == 3:
            fnt, text, color = entry
        else:
            fnt, text = entry
            color = (0,0,0)
        rendered_lines.append((fnt.render(text, True, color), fnt))

    # For the progress bar, remember its y position
    progress_bar_index = len(rendered_lines) - 4  # After "Your Progress" line

    row_height = 32
    running = True
    while running:
        pet_x = WIDTH//2 + 100
        pet_y = HEIGHT//2 - pet.sprite.get_height()//2
        screen.fill((245,245,220))
        nav_btns = draw_nav_buttons(screen, show_home=True, show_start=True)
        y = 30 - scroll
        progress_bar_drawn = False
        for idx, (surf, fnt) in enumerate(rendered_lines):
            screen.blit(surf, (60, y))
            # Draw the progress bar just after the "Your Progress" line
            if idx == progress_bar_index and not progress_bar_drawn:
                # Use canonical savings fields for the progress bar (avoid 0/0)
                targ = getattr(player, "savings_goal_target", getattr(player, "goal_target_amount", 100))
                prog = getattr(player, "savings", getattr(player, "goal_progress", 0))
                if targ and targ > 0:
                    bar_w = 520
                    bar_h = 24
                    bar_x = 60 + 30
                    bar_y = y + row_height + 8
                    progress = min(prog, targ)
                    pygame.draw.rect(screen, (200,200,200), (bar_x, bar_y, bar_w, bar_h), border_radius=10)
                    fill_w = int(bar_w * (progress / targ))
                    pygame.draw.rect(screen, (80,200,80), (bar_x, bar_y, fill_w, bar_h), border_radius=10)
                    pygame.draw.rect(screen, (100,100,100), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)
                    if getattr(player, "goal_completed", False):
                        complete_txt = text_font.render("Goal Complete! Reward Unlocked!", True, (200,120,0))
                        screen.blit(complete_txt, (bar_x, bar_y + bar_h + 8))
                    y += bar_h + 16  # Add extra space for bar
                progress_bar_drawn = True
            y += row_height if fnt != title_font else 38

        # Calculate total content height for scrolling
        total_content_height = y + 40  # y is now the bottom after all content

        nav_txt = small_font.render("Up/Down or Mouse Wheel to scroll, Esc to return", True, (100,100,100))
        screen.blit(nav_txt, (screen.get_width()//2 - nav_txt.get_width()//2, screen.get_height()-40))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  # This will exit the guide and return to the main loop
                if event.key == pygame.K_DOWN:
                    scroll = min(scroll + row_height, max(0, total_content_height - screen.get_height()))
                if event.key == pygame.K_UP:
                    scroll = max(0, scroll - row_height)
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Return to main loop when Home clicked (with top-right fallback)
                if ("home" in nav_btns and nav_btns["home"].collidepoint(event.pos)) or pygame.Rect(WIDTH-240, 0, 240, 48).collidepoint(event.pos):
                    pygame.event.clear()
                    return  # Return to main loop (current era)
                if "start" in nav_btns and nav_btns["start"].collidepoint(event.pos):
                    pygame.quit()
                    os.execl(sys.executable, sys.executable, *sys.argv)  # Restart to start page
                if event.button == 4:  # Scroll up
                    scroll = max(0, scroll - row_height)
                if event.button == 5:  # Scroll down
                    scroll = min(scroll + row_height, max(0, total_content_height - screen.get_height()))

def customization_page(screen, font):
    # ============================================================ 
    #Allows:
    #- Character selection.
    #- Pet selection.
    #- Pet naming input.
    #- Confirmation validation.
    # ============================================================ 
    character_names = ["alex", "maria", "carlos", "grace"]
    character_imgs = ["boy1.png", "girl1.png", "boy2.png", "girl2.png"]
    pet_names = ["dog", "bunny", "bird", "cat"]
    pet_imgs = ["dog.png", "bunny.png", "bird.png", "cat.png"]
    selected_char = 0
    selected_pet = 0
    pet_name = ""
    input_active = False

    while True:
        WIDTH, HEIGHT = screen.get_size()
        screen.fill((173, 216, 230))
        nav_btns = draw_nav_buttons(screen, show_home=True, show_start=True)
        scale = HEIGHT / 540

        char_img_size = int(120 * scale)
        pet_img_size = char_img_size
        input_box_height = int(40 * scale)
        input_box_width = int(240 * scale)
        confirm_height = int(50 * scale)
        confirm_width = int(160 * scale)
        margin_x = int(120 * scale)
        gap = int(40 * scale)
        font_size = max(18, int(24 * scale))
        font = pygame.font.SysFont("Arial", font_size)

        y = int(30 * scale)
        instr = font.render("Choose your character", True, (255,255,255))
        screen.blit(instr, (WIDTH//2 - instr.get_width()//2, y))
        y += instr.get_height() + gap//2

        # Character chooser
        for i, (name, img_file) in enumerate(zip(character_names, character_imgs)):
            rect_x = margin_x + i * ((WIDTH - 2*margin_x - char_img_size*4)//3 + char_img_size)
            rect = pygame.Rect(rect_x, y, char_img_size, char_img_size)
            # Draw highlight first, with larger inflate and larger border radius
            if i == selected_char:
                highlight_rect = rect.inflate(int(18*scale), int(18*scale))
                pygame.draw.rect(screen, (255, 221, 51), highlight_rect, border_radius=int(32*scale))
            # Draw main border on top
            pygame.draw.rect(screen, (220,180,180), rect, border_radius=int(20*scale))
            img = load_placeholder(f"assets/player/{img_file}", (char_img_size, char_img_size))
            screen.blit(img, rect.topleft)
            label = font.render(name.capitalize(), True, (0,0,0))
            screen.blit(label, (rect.x + rect.width//2 - label.get_width()//2, rect.y + rect.height + int(10*scale)))
        y += char_img_size + int(40 * scale)

        # Pet chooser instruction
        pet_instr = font.render("Choose your pet", True, (255,255,255))
        screen.blit(pet_instr, (WIDTH//2 - pet_instr.get_width()//2, y))
        y += pet_instr.get_height() + gap//2

        # Pet chooser
        for i, (name, img_file) in enumerate(zip(pet_names, pet_imgs)):
            rect_x = margin_x + i * ((WIDTH - 2*margin_x - pet_img_size*4)//3 + pet_img_size)
            rect = pygame.Rect(rect_x, y, pet_img_size, pet_img_size)
            if i == selected_pet:
                highlight_rect = rect.inflate(int(18*scale), int(18*scale))
                pygame.draw.rect(screen, (255, 221, 51), highlight_rect, border_radius=int(32*scale))
            pygame.draw.rect(screen, (220,220,180), rect, border_radius=int(20*scale))
            img = load_placeholder(f"assets/pets/{pet_names[i]}/{pet_names[i]}.png", (pet_img_size, pet_img_size))
            screen.blit(img, rect.topleft)
            label = font.render(name.capitalize(), True, (0,0,0))
            screen.blit(label, (rect.x + rect.width//2 - label.get_width()//2, rect.y + rect.height + int(10*scale)))
        y += pet_img_size + int(40 * scale)

        y += int(30 * scale)

        row_y = y

        name_instr = font.render("Name your pet:", True, (255,255,255))
        input_box = pygame.Rect(WIDTH//2 - input_box_width - confirm_width//2 - int(10*scale), row_y, input_box_width, input_box_height)
        screen.blit(name_instr, (input_box.x, row_y - name_instr.get_height() - int(5*scale)))

        confirm_rect = pygame.Rect(WIDTH//2 + input_box_width//2 + int(10*scale), row_y, confirm_width, confirm_height)
        # --- Draw highlight for name input if active ---
        if input_active:
            highlight_rect = input_box.inflate(int(18*scale), int(18*scale))
            pygame.draw.rect(screen, (255, 221, 51), highlight_rect, border_radius=int(24*scale))
        pygame.draw.rect(screen, (255,255,255), input_box, 2, border_radius=int(12*scale))
        name_surface = font.render(pet_name, True, (0,0,0))
        screen.blit(name_surface, (input_box.x+int(10*scale), input_box.y+input_box_height//2 - name_surface.get_height()//2))

        pygame.draw.rect(screen, (255,192,77), confirm_rect, border_radius=int(20*scale))
        confirm_txt = font.render("Confirm", True, (0,0,0))
        screen.blit(confirm_txt, (confirm_rect.x + confirm_rect.width//2 - confirm_txt.get_width()//2, confirm_rect.y + confirm_rect.height//2 - confirm_txt.get_height()//2))

        y += max(input_box_height, confirm_height) + gap

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                # Nav buttons: Home -> return, Restart -> restart app
                if "home" in nav_btns and nav_btns["home"].collidepoint(pos):
                    return
                if "start" in nav_btns and nav_btns["start"].collidepoint(pos):
                    play_confirm_sound()
                    pygame.quit()
                    os.execl(sys.executable, sys.executable, *sys.argv)
                # Character selection
                for i in range(4):
                    rect_x = margin_x + i * ((WIDTH - 2*margin_x - char_img_size*4)//3 + char_img_size)
                    rect = pygame.Rect(rect_x, int(30*scale) + instr.get_height() + gap//2, char_img_size, char_img_size)
                    if rect.collidepoint(pos):
                        selected_char = i
                # Pet selection
                for i in range(4):
                    rect_x = margin_x + i * ((WIDTH - 2*margin_x - pet_img_size*4)//3 + pet_img_size)
                    rect = pygame.Rect(rect_x, int(30*scale) + instr.get_height() + gap//2 + char_img_size + int(40*scale) + pet_instr.get_height() + gap//2, pet_img_size, pet_img_size)
                    if rect.collidepoint(pos):
                        selected_pet = i
                # Input box activation
                if input_box.collidepoint(pos):
                    input_active = True
                else:
                    input_active = False
                # --- Confirm button logic (ONLY validate on confirm click) ---
                if confirm_rect.collidepoint(pos):
                    if not pet_name.strip():
                        show_name_warning(screen, font, "You must enter a name to continue!")
                    elif not pet_name.isalpha():
                        show_name_warning(screen, font, "Only letters are allowed!")
                    else:
                        play_confirm_sound()
                        return character_imgs[selected_char], pet_names[selected_pet], pet_name.strip(), screen
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    if not pet_name.strip():
                        show_name_warning(screen, font, "You must enter a name to continue!")
                    elif not any(c.isalpha() for c in pet_name) or not pet_name.isalpha():
                        show_name_warning(screen, font, "Only letters are allowed!")
                    else:
                        play_confirm_sound()
                        return character_imgs[selected_char], pet_names[selected_pet], pet_name.strip(), screen
                elif event.key == pygame.K_BACKSPACE:
                    pet_name = pet_name[:-1]
                elif event.unicode and len(pet_name) < 16:
                    pet_name += event.unicode
       
def draw_stats_box(screen, pet, WIDTH, HEIGHT):
    stats_box_x = 10
    stats_box_y = HEIGHT//2 - 120
    stats_box_width = 300
    stats_box_height = 240

    pygame.draw.rect(screen, (240, 240, 240), (stats_box_x, stats_box_y, stats_box_width, stats_box_height), border_radius=15)
    pygame.draw.rect(screen, (100, 100, 100), (stats_box_x, stats_box_y, stats_box_width, stats_box_height), 3, border_radius=15)

    title_font = pygame.font.SysFont("Arial", 20, bold=True)
    title_txt = title_font.render("Pet Stats", True, (0, 0, 0))
    screen.blit(title_txt, (stats_box_x + stats_box_width//2 - title_txt.get_width()//2, stats_box_y + 10))

    stat_font = pygame.font.SysFont("Arial", 18)
    stat_names = ["Hunger", "Happiness", "Energy", "Health"]
    y_offset = stats_box_y + 45
    for stat_name in stat_names:
        stat_key = stat_name.lower()
        # Use getattr to get the value from the Pet object
        stat_value = getattr(pet, stat_key, 0)
        stat_label = stat_font.render(f"{stat_name}:", True, (0, 0, 0))
        screen.blit(stat_label, (stats_box_x + 10, y_offset))
        bar_x = stats_box_x + 10
        bar_y = y_offset + 20
        bar_width = stats_box_width - 60
        bar_height = 15
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), border_radius=7)
        green_width = int((min(stat_value, 100) / 100) * bar_width)
        if green_width > 0:
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, green_width, bar_height), border_radius=7)
        if stat_value < 100:
            red_start_x = bar_x + green_width
            red_width = bar_width - green_width
            if red_width > 0:
                pygame.draw.rect(screen, (255, 0, 0), (red_start_x, bar_y, red_width, bar_height), border_radius=7)
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=7)
        value_txt = stat_font.render(str(int(stat_value)), True, (0, 0, 0))
        screen.blit(value_txt, (bar_x + bar_width + 25, bar_y - 2))
        y_offset += 45

def era_map_screen(screen, font, unlocked_eras, current_era):
    pet_img_size = 120
    while True:
        # Use the requested single background file for the era map screen
        map_bg = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "backgrounds", "era_bg.png")).convert()
        map_bg = pygame.transform.scale(map_bg, screen.get_size())
        screen.blit(map_bg, (0, 0))

        # --- Draw centered avatar and pet in map screen ---
        WIDTH, HEIGHT = screen.get_size()
        # load avatar (fallback to placeholder)
        try:
            avatar_img = load_placeholder(f"assets/player/{player.avatar}", (120,180))
        except Exception:
            avatar_img = pygame.Surface((120,-100))
            avatar_img.fill((200,200,200))

        # force a "happy" pet image if available, else fallback to current sprite
        pet_happy_path = f"assets/pets/{pet.species}/{pet.species}_happy.png"
        if os.path.exists(pet_happy_path):
            pet_img = pygame.image.load(pet_happy_path).convert_alpha()
        else:
            pet_img = pet.sprite
        pet_img = pygame.transform.smoothscale(pet_img, getattr(pet, "PET_DISPLAY_SIZE", (120,120)))

        center_x = WIDTH // 2
        center_y = HEIGHT // 2 + 60
        avatar_rect = avatar_img.get_rect(center=(center_x - 90, center_y))
        pet_rect = pet_img.get_rect(center=(center_x + 90, center_y))

        screen.blit(avatar_img, avatar_rect)
        screen.blit(pet_img, pet_rect)
        nav_btns = draw_nav_buttons(screen, show_home=False, show_start=True)
        txt = font.render("Select Era", True, (255,255,255))
        screen.blit(txt, (WIDTH//2-80, 40))
        for i, era in enumerate(unlocked_eras):
            rect = pygame.Rect(120+i*160, 200, 120, 120)
            pygame.draw.rect(screen, (180,220,180) if i==current_era else (220,180,180), rect, border_radius=30)
            # Load and draw the era background as a thumbnail
            img = load_placeholder(f"assets/backgrounds/{era}.png", (pet_img_size, pet_img_size))
            screen.blit(img, rect.topleft)
            label = font.render(era.capitalize(), True, (0,0,0))
            padding_x = 10
            padding_y = 6
            label_rect = label.get_rect()
            box_w = label_rect.width + padding_x * 2
            box_h = label_rect.height + padding_y * 2
            box_x = rect.x + rect.width//2 - box_w//2
            box_y = rect.y + rect.height + 8
            # light blue fill, darker blue border
            pygame.draw.rect(screen, (173,216,230), (box_x, box_y, box_w, box_h), border_radius=8)
            pygame.draw.rect(screen, (30,100,200), (box_x, box_y, box_w, box_h), 2, border_radius=8)
            screen.blit(label, (box_x + padding_x, box_y + padding_y))
        nav_txt = font.render("Click era to travel", True, (200,200,200))
        screen.blit(nav_txt, (WIDTH//2-80, HEIGHT-40))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for i in range(len(unlocked_eras)):
                    if pygame.Rect(120+i*160, 200, 120, 120).collidepoint(pos):
                        return i
        pygame.display.flip()
        clock.tick(30)

def help_screen(screen, font):
    instructions = [
       "🐾 HELP MENU CONTENT",
       "",
       "🏠 Welcome to Time Travel Pet!",
       "Time Travel Pet is an interactive virtual pet game where you care for your pet across different historical eras while managing a budget.",
       "",
       "Your goal is to:",
       "- Keep your pet healthy and happy",
       "- Manage your in-game currency responsibly",
       "- Complete savings goals",
       "- Unlock era rewards",
       "- Learn about financial responsibility",
       "",
       "🎮 Getting Started",
       "- Choose your pet type.",
       "- Enter a valid name (must contain at least one letter).",
       "- Begin caring for your pet by using the action buttons.",
       "",
       "🐶 Pet Stats Explained",
       "Your pet has four main stats:",
       "",
       "🍖 Hunger: Decreases over time, feed your pet to increase hunger. If too low, your pet may become sick.",
       "😊 Happiness: Increases when you play, decreases if ignored. Low happiness affects mood.",
       "⚡ Energy: Decreases when playing, increases when resting. Low energy limits activity.",
       "❤️ Health: Affected by hunger and cleanliness. Visit the vet to restore health. If too low, your pet becomes sick.",
       "- Stats range from 0 to 100.",
       "",
       "🎭 Mood System",
       "Your pet’s appearance changes based on its stats:",
       "- 😊 Happy — Balanced care",
       "- 😢 Sad — Low happiness",
       "- 🤒 Sick — Low health",
       "- ⚡ Energetic — High energy",
       "- The sprite updates automatically based on conditions.",
       "",
       "💰 Cost of Care System",
       "Each action costs ChronoCoins:",
       "- Feed → Costs coins (food expense)",
       "- Play → Costs coins (toy/activity expense)",
       "- Medical Care → Costs coins (vet expense)",
       "- You must manage your coins wisely.",
       "",
       "🪙 In-Game Currency (ChronoCoins)",
       "- You start with a limited amount.",
       "- Spending too much may prevent you from caring for your pet.",
       "- The ml will warn you about overspending.",
       "- Some eras include savings goals for rewards.",
       "- If coins run out, actions draw from your weekly budget.",
       "- Budget updates every minute, and overspending will trigger warnings.",
       "",
       "📊 Diary & Reports",
       "The Diary tracks:",
       "- Every action taken",
       "- Spending by category",
       "- Most frequent action",
       "- Most recent action",
       "- All data is saved in a JSON file so progress continues between sessions.",
       "- Reports let you analyze:",
       "  - How balanced your care is",
       "  - Where your money is going",
       "  - Whether you are overspending",
       "",
       "🤖 Machine Learning Assistant",
       "The ml gives helpful tips when:",
       "- Hunger is too low",
       "- Health is critical",
       "- Energy is too low",
       "- You are overspending",
       "- The ml helps guide responsible pet ownership and budgeting.",
       "",
       "🏛 Era System",
       "Each historical era changes gameplay:",
       "- Hunger decay rates may change",
       "- Health limits may change",
       "- Savings goals may vary",
       "- Rewards may unlock",
       "- This adds educational context and strategic planning.",
       "",
       "🔁 Restarting the Game",
       "The Restart button resets:",
       "- Pet stats",
       "- Currency",
       "- Diary data",
       "- Use this if you want to start fresh.",
       "",
       "❗ Input Rules",
       "- Pet name must contain at least one alphabetical character.",
       "- Actions cannot be performed if you do not have enough coins.",
       "- Stats are capped between 0 and 100.",
       "",
       "🛠 Troubleshooting",
       "If something seems wrong:",
       "- Make sure your pet has enough coins for actions.",
       "- Check the Diary to review recent actions.",
       "- Restart the game if needed.",
       "",
       "🏆 Winning the Game",
       "You succeed when:",
       "- Your pet remains healthy and happy.",
       "- You complete savings goals.",
       "- You manage your budget responsibly.",
       "",
       "🎯 Educational Purpose",
       "This game teaches:",
       "- Financial responsibility",
       "- Budget management",
       "- Cause and effect decision making",
       "- Basic programming logic concepts",
       "",
       "🚀 Advanced Tips",
       "- Balance feeding and playing.",
       "- Don’t ignore health.",
       "- Save coins for emergencies.",
       "- Check the Diary often.",
       "",
       "Press ESC to return."


    ]
    scroll = 0
    line_height = font.get_height() + 8
    while True:
        screen.fill((173,216,230))
        nav_btns = draw_nav_buttons(screen, show_home=True, show_start=True)
        lines_per_page = (screen.get_height() - 80) // line_height
        for i, line in enumerate(instructions[scroll:scroll+lines_per_page]):
            txt = font.render(line, True, (0,0,0))
            screen.blit(txt, (40, 40 + i*line_height))
        nav_txt = font.render("Up/Down to scroll, Esc to exit", True, (0,0,0))
        screen.blit(nav_txt, (40, screen.get_height()-40))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return
                if event.key == pygame.K_DOWN:
                    scroll = min(len(instructions)-lines_per_page, scroll+1)
                if event.key == pygame.K_UP:
                    scroll = max(0, scroll-1)
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Home click (nav button or top-right fallback) — clear pending events so one click is enough
                if ("home" in nav_btns and nav_btns["home"].collidepoint(event.pos)) or pygame.Rect(WIDTH-240, 0, 240, 48).collidepoint(event.pos):
                    pygame.event.clear()
                    return
                # Restart button (exact same behavior as keyboard)
                if ("start" in nav_btns and nav_btns["start"].collidepoint(event.pos)):
                    play_confirm_sound()
                    pygame.quit()
                    os.execl(sys.executable, sys.executable, *sys.argv)
                # Mouse wheel: 4 = up, 5 = down
                if event.button == 4:
                    scroll = max(0, scroll-1)
                if event.button == 5:
                    scroll = min(len(instructions)-lines_per_page, scroll+1)

def draw_mission_help_box(screen, font, state, box_x=None, box_y=None):
    """
    Draws an interactive help box for the Missions section in the bottom-right corner.
    - state: "menu", "how", "coins", or "complete"
    Returns: list of (rect, state) for clickable buttons.
    """
    WIDTH, HEIGHT = screen.get_size()
    box_w = min(320, WIDTH // 4)
    box_h = min(320, HEIGHT // 3)
    # Default: bottom-right
    if box_x is None:
        box_x = WIDTH - box_w - 24
    if box_y is None:
        box_y = HEIGHT - box_h - 24
    box_color = (180, 220, 255)
    border_color = (100, 140, 180)
    padding = 18

    pygame.draw.rect(screen, box_color, (box_x, box_y, box_w, box_h), border_radius=18)
    pygame.draw.rect(screen, border_color, (box_x, box_y, box_w, box_h), 3, border_radius=18)

    heading_font = pygame.font.SysFont("Arial", 22, bold=True)
    btn_font = pygame.font.SysFont("Arial", 18, bold=True)
    text_font = pygame.font.SysFont("Arial", 16)

    if state == "menu":
        title = heading_font.render("Need Help?", True, (0, 40, 80))
        screen.blit(title, (box_x + (box_w - title.get_width()) // 2, box_y + padding))
        btn_w = box_w - 2 * padding
        btn_h = 38
        btn_gap = 12
        btns = []
        btn_labels = [
            ("How missions work", "how"),
            ("How missions give you coins", "coins"),
            ("After missions are completed", "complete"),
        ]
        for i, (label, next_state) in enumerate(btn_labels):
            btn_rect = pygame.Rect(
                box_x + padding,
                box_y + padding + title.get_height() + 18 + i * (btn_h + btn_gap),
                btn_w,
                btn_h
            )
            pygame.draw.rect(screen, (255, 255, 255), btn_rect, border_radius=10)
            pygame.draw.rect(screen, border_color, btn_rect, 2, border_radius=10)
            btn_text = btn_font.render(label, True, (0, 60, 120))
            screen.blit(btn_text, (btn_rect.x + (btn_w - btn_text.get_width()) // 2, btn_rect.y + (btn_h - btn_text.get_height()) // 2))
            btns.append((btn_rect, next_state))
        return btns

    answer_texts = {
        "how": "Missions are small tasks that help you unlock the next era, finish 3 missions to complete this era.",
        "coins": "When you complete a mission successfully, you earn coins. Coins can be used to buy food, toys, and other supplies for your pet.",
        "complete": "When a mission is completed, your pet receives rewards such as happiness boosts, experience, or coins. A new era will also be unlocked with info on what the era is like."
    }
    answer = answer_texts.get(state, "")
    def draw_multiline(text, font, color, x, y, max_width):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = current + (" " if current else "") + word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        for i, line in enumerate(lines):
            surf = font.render(line, True, color)
            screen.blit(surf, (x, y + i * (font.get_height() + 4)))
        return y + len(lines) * (font.get_height() + 4)

    answer_title = heading_font.render("Mission Help", True, (0, 40, 80))
    screen.blit(answer_title, (box_x + (box_w - answer_title.get_width()) // 2, box_y + padding))
    text_y = box_y + padding + answer_title.get_height() + 12
    text_y = draw_multiline(answer, text_font, (0, 0, 0), box_x + padding, text_y, box_w - 2 * padding)
    btn_w = box_w - 2 * padding
    btn_h = 36
    btn_rect = pygame.Rect(box_x + padding, box_y + box_h - btn_h - padding, btn_w, btn_h)
    pygame.draw.rect(screen, (255, 255, 255), btn_rect, border_radius=10)
    pygame.draw.rect(screen, border_color, btn_rect, 2, border_radius=10)
    btn_text = btn_font.render("Return", True, (0, 60, 120))
    screen.blit(btn_text, (btn_rect.x + (btn_w - btn_text.get_width()) // 2, btn_rect.y + (btn_h - btn_text.get_height()) // 2))
    return [(btn_rect, "menu")]

def cost_guide_screen(screen, font):
    scroll = 0
    y_start = 30
    small_font = pygame.font.SysFont("Arial", 18)
    era_titles = [
        ("Egypt", "🏺 Ancient Egypt"),
        ("Greece", "🏛️ Classical Greece"),
        ("Medieval", "🏰 Medieval Europe"),
        ("Industrial", "🚂 Industrial Revolution"),
        ("Modern", "🌆 Modern Era")
    ]
    # Set column pixel positions
    col_item = 80
    col_cost = 260
    col_effect = 340
    row_height = 24

    while True:
        screen.fill((245,245,220))
        nav_btns = draw_nav_buttons(screen, show_home=True, show_start=True)
        y = y_start - scroll
        title = font.render("🕰️ Era Item Cost Chart", True, (0,0,0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, y))
        y += 50
        for era_key, era_label in era_titles:
            screen.blit(small_font.render(era_label, True, (0,0,128)), (col_item, y))
            y += 28
            # Draw column headers
            screen.blit(small_font.render("Item", True, (0,0,0)), (col_item, y))
            screen.blit(small_font.render("Cost", True, (0,0,0)), (col_cost, y))
            screen.blit(small_font.render("Effect", True, (0,0,0)), (col_effect, y))
            y += row_height
            for item, data in ERA_COST_TABLE[era_key].items():
                # Only one effect per item
                for stat, val in data["effect"].items():
                    effect_str = f"+{val} {stat.capitalize()}"
                screen.blit(small_font.render(item, True, (0,0,0)), (col_item, y))
                screen.blit(small_font.render(str(data['cost']), True, (0,0,0)), (col_cost, y))
                screen.blit(small_font.render(effect_str, True, (0,0,0)), (col_effect, y))
                y += row_height
            y += 18
        nav_txt = small_font.render("Up/Down or Mouse Wheel to scroll, Esc to return", True, (100,100,100))
        screen.blit(nav_txt, (screen.get_width()//2 - nav_txt.get_width()//2, screen.get_height()-40))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_DOWN:
                    scroll = min(scroll + 30, max(0, y - screen.get_height() + 60))
                if event.key == pygame.K_UP:
                    scroll = max(0, scroll - 30)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if "home" in nav_btns and nav_btns["home"].collidepoint(event.pos):
                    return  # Return to main loop (current era)
                if "start" in nav_btns and nav_btns["start"].collidepoint(event.pos):
                    pygame.quit()
                    os.execl(sys.executable, sys.executable, *sys.argv)  # Restart to start page
                if event.button == 4:  # Scroll up
                    scroll = max(0, scroll - 30)
                if event.button == 5:  # Scroll down
                    scroll = min(scroll + 30, max(0, y - screen.get_height() + 60))

def show_era_lesson(screen, font, era_name):
    WIDTH, HEIGHT = screen.get_size()
    lesson = ERA_LESSONS[era_name]
    popup_width = min(700, WIDTH - 80)
    min_popup_height = 300
    max_popup_height = HEIGHT - 80

    title_font = pygame.font.SysFont("Arial", 32, bold=True)
    text_font = pygame.font.SysFont("Arial", 22)
    button_font = pygame.font.SysFont("Arial", 24, bold=True)

    # Helper to measure multiline text height
    def measure_multiline(text, font, max_width, line_spacing=8):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return len(lines) * (font.get_height() + line_spacing)

    # Calculate needed height
    y = 80  # space for title
    lesson_height = measure_multiline(lesson["lesson_text"], text_font, popup_width - 80)
    y += lesson_height + 16
    y += text_font.get_height() + 4  # "Gameplay Connection:" label
    gameplay_height = measure_multiline(lesson["gameplay_connection"], text_font, popup_width - 80)
    y += gameplay_height
    y += 24 + 50  # space for button

    popup_height = min(max(y, min_popup_height), max_popup_height)
    popup_x = (WIDTH - popup_width) // 2
    popup_y = (HEIGHT - popup_height) // 2

    running = True
    while running:
        # Draw popup background
        pygame.draw.rect(screen, (255, 255, 220), (popup_x, popup_y, popup_width, popup_height), border_radius=18)
        pygame.draw.rect(screen, (180, 180, 100), (popup_x, popup_y, popup_width, popup_height), 4, border_radius=18)

        # Draw title
        title_surf = title_font.render(lesson["title"], True, (80, 60, 0))
        screen.blit(title_surf, (popup_x + (popup_width - title_surf.get_width()) // 2, popup_y + 24))

        # Draw lesson text (wrap if needed)
        def draw_multiline(text, font, color, x, y, max_width, line_spacing=8):
            words = text.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            for i, line in enumerate(lines):
                surf = font.render(line, True, color)
                screen.blit(surf, (x, y + i * (font.get_height() + line_spacing)))
            return y + len(lines) * (font.get_height() + line_spacing)

        y = popup_y + 80
        y = draw_multiline(lesson["lesson_text"], text_font, (0, 0, 0), popup_x + 40, y, popup_width - 80)
        y += 16
        gameplay_title = text_font.render("Gameplay Connection:", True, (0, 80, 120))
        screen.blit(gameplay_title, (popup_x + 40, y))
        y += gameplay_title.get_height() + 4
        y = draw_multiline(lesson["gameplay_connection"], text_font, (0, 0, 0), popup_x + 40, y, popup_width - 80)

        # Draw Continue button BELOW all text
        btn_width, btn_height = 180, 50
        btn_x = popup_x + popup_width//2 - btn_width//2
        btn_y = popup_y + popup_height - btn_height - 24
        btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        pygame.draw.rect(screen, (255, 221, 51), btn_rect, border_radius=14)
        pygame.draw.rect(screen, (180, 180, 100), btn_rect, 3, border_radius=14)
        btn_text = button_font.render("Continue", True, (0,0,0))
        screen.blit(btn_text, (btn_x + btn_width//2 - btn_text.get_width()//2, btn_y + btn_height//2 - btn_text.get_height()//2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    play_confirm_sound()
                    running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    play_confirm_sound()
                    running = False

def draw_main_ui(screen, font, pet, player, eras, current_era, diary):
    WIDTH, HEIGHT = screen.get_size()
    padding = 24
    section_gap = 32
    box_color = (230, 230, 240)
    border_color = (180, 180, 200)
    header_font = pygame.font.SysFont("Arial", 28, bold=True)
    section_font = pygame.font.SysFont("Arial", 22, bold=True)
    normal_font = pygame.font.SysFont("Arial", 18)

    # --- Section: Pet Actions ---
    pet_actions_rect = pygame.Rect(padding, padding, WIDTH//3 - padding*2, HEIGHT//3)
    pygame.draw.rect(screen, box_color, pet_actions_rect, border_radius=12)
    pygame.draw.rect(screen, border_color, pet_actions_rect, 2, border_radius=12)
    header = section_font.render("Pet Actions", True, (60, 60, 90))
    screen.blit(header, (pet_actions_rect.x + 12, pet_actions_rect.y + 12))

    # Arrange pet action buttons vertically with spacing
    btn_y = pet_actions_rect.y + 48
    btn_gap = 16
    for btn_name in ["feed", "play", "rest", "clean", "health"]:
        btn = buttons[btn_name]
        btn_rect = pygame.Rect(pet_actions_rect.x + 24, btn_y, 120, 40)
        pygame.draw.rect(screen, (200, 220, 200), btn_rect, border_radius=8)
        btn_label = normal_font.render(btn_name.capitalize(), True, (40, 40, 40))
        screen.blit(btn_label, (btn_rect.x + 16, btn_rect.y + 8))
        btn_y += 40 + btn_gap

    # --- Section: Economy ---
    economy_rect = pygame.Rect(WIDTH//3 + padding, padding, WIDTH//3 - padding*2, HEIGHT//3)
    pygame.draw.rect(screen, box_color, economy_rect, border_radius=12)
    pygame.draw.rect(screen, border_color, economy_rect, 2, border_radius=12)
    header = section_font.render("Economy", True, (60, 60, 90))
    screen.blit(header, (economy_rect.x + 12, economy_rect.y + 12))

    # Display player stats with spacing
    stat_y = economy_rect.y + 48
    stats = [
        f"ChronoCoins: {player.chronocoins}",
        f"Weekly Budget: {player.weekly_budget}",
        f"Budget Remaining: {player.budget_remaining}",
        f"Savings: {player.savings}",
        f"Savings Goal: {player.savings_goal_name} ({player.savings_goal_target})"
    ]
    for stat in stats:
        stat_label = normal_font.render(stat, True, (40, 40, 40))
        screen.blit(stat_label, (economy_rect.x + 24, stat_y))
        stat_y += 32

    # --- Section: Reports ---
    reports_rect = pygame.Rect(2*WIDTH//3 + padding, padding, WIDTH//3 - padding*2, HEIGHT//3)
    pygame.draw.rect(screen, box_color, reports_rect, border_radius=12)
    pygame.draw.rect(screen, border_color, reports_rect, 2, border_radius=12)
    header = section_font.render("Reports", True, (60, 60, 90))
    screen.blit(header, (reports_rect.x + 12, reports_rect.y + 12))

    # Arrange report buttons vertically
    report_y = reports_rect.y + 48
    for btn_name in ["diary", "custom_report"]:
        btn = buttons[btn_name]
        btn_rect = pygame.Rect(reports_rect.x + 24, report_y, 140, 40)
        pygame.draw.rect(screen, (220, 200, 200), btn_rect, border_radius=8)
        btn_label = normal_font.render(btn_name.replace("_", " ").capitalize(), True, (40, 40, 40))
        screen.blit(btn_label, (btn_rect.x + 16, btn_rect.y + 8))
        report_y += 40 + btn_gap

    # --- Section: Era Info ---
    era_rect = pygame.Rect(padding, HEIGHT//3 + section_gap, WIDTH - padding*2, HEIGHT//3)
    pygame.draw.rect(screen, box_color, era_rect, border_radius=12)
    pygame.draw.rect(screen, border_color, era_rect, 2, border_radius=12)
    header = section_font.render("Era Info", True, (60, 60, 90))
    screen.blit(header, (era_rect.x + 12, era_rect.y + 12))

    # Display current era and facts
    era_label = header_font.render(f"Current Era: {eras[current_era].capitalize()}", True, (80, 80, 120))
    screen.blit(era_label, (era_rect.x + 24, era_rect.y + 48))
    fact_y = era_rect.y + 90
    for fact in era_facts[eras[current_era]]:
        fact_label = normal_font.render(f"- {fact}", True, (40, 40, 40))
        screen.blit(fact_label, (era_rect.x + 24, fact_y))
        fact_y += 28

    # --- Section: Navigation ---
    nav_rect = pygame.Rect(padding, HEIGHT - 80, WIDTH - padding*2, 60)
    pygame.draw.rect(screen, (220, 220, 230), nav_rect, border_radius=10)
    pygame.draw.rect(screen, border_color, nav_rect, 2, border_radius=10)
    nav_btns = draw_nav_buttons(screen, show_home=True, show_start=True)
    nav_label = normal_font.render("Navigation", True, (60, 60, 90))
    screen.blit(nav_label, (nav_rect.x + 12, nav_rect.y + 12))

    # (Keep all button logic and event handling unchanged)

# ============================================================
# Saving Goal System
# ============================================================
def set_saving_goal(player, era):
    goal = ERA_GOALS[era]
    # Normalize goal fields so all UI / logic read the same values
    player.current_goal_name = goal["name"]
    player.savings_goal_name = goal["name"]
    player.savings_goal_target = 100            # canonical target used in UI
    player.goal_target_amount = 100             # legacy field kept in sync
    # progress should reflect actual saved amount (in case player already had savings)
    player.goal_progress = getattr(player, "savings", 0)
    # completion flags
    player.goal_completed = player.savings >= player.savings_goal_target
    player.goal_reward_applied = False

def show_goal_popup(player):
    # Use your popup style
    WIDTH, HEIGHT = screen.get_size()
    popup_width = 500
    popup_height = 320
    popup_x = (WIDTH - popup_width) // 2
    popup_y = (HEIGHT - popup_height) // 2
    font = pygame.font.SysFont("Arial", 24)
    running = True
    while running:
        pygame.draw.rect(screen, (255, 255, 220), (popup_x, popup_y, popup_width, popup_height), border_radius=18)
        pygame.draw.rect(screen, (180, 180, 100), (popup_x, popup_y, popup_width, popup_height), 4, border_radius=18)
        y = popup_y + 30
        title = font.render(f"Savings Goal: {player.current_goal_name}", True, (80, 60, 0))
        screen.blit(title, (popup_x + (popup_width - title.get_width()) // 2, y))
        y += 50
        if player.goal_target_amount > 0:
            progress = min(player.goal_progress, player.goal_target_amount)
            progress_txt = font.render(f"Progress: {progress} / {player.goal_target_amount}", True, (0,0,0))
            screen.blit(progress_txt, (popup_x + 40, y))
            y += 40
            # Progress bar
            bar_w = 400
            bar_h = 28
            bar_x = popup_x + 50
            bar_y = y
            pygame.draw.rect(screen, (200,200,200), (bar_x, bar_y, bar_w, bar_h), border_radius=10)
            fill_w = int(bar_w * progress / player.goal_target_amount)
            pygame.draw.rect(screen, (80,200,80), (bar_x, bar_y, fill_w, bar_h), border_radius=10)
            pygame.draw.rect(screen, (100,100,100), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)
            y += bar_h + 30
        else:
            no_goal_txt = font.render("No saving goal set for this era.", True, (200, 60, 60))
            screen.blit(no_goal_txt, (popup_x + 40, y))
            y += 60
        reward = None
        for era, goal in ERA_GOALS.items():
            if goal["name"] == player.current_goal_name:
                reward = goal["reward"]
        if reward:
            reward_lines = reward.split(", ")
            for line in reward_lines:
                line_txt = font.render(line, True, (0,0,0))
                screen.blit(line_txt, (popup_x + 60, y))
                y += 28
        else:
            no_reward_txt = font.render("No reward info available", True, (200, 60, 60))
            screen.blit(no_reward_txt, (popup_x + 40, y))
            y += 28
        if player.goal_completed and not player.goal_reward_applied:
            congrats = font.render("Congratulations! You reached your saving goal!", True, (200,120,0))
            screen.blit(congrats, (popup_x + 40, popup_y + popup_height - 60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_ESCAPE]):
                play_confirm_sound()
                running = False
    # Apply reward if not already done
    if player.goal_completed and not player.goal_reward_applied:
        for era, goal in ERA_GOALS.items():
            if goal["name"] == player.current_goal_name:
                goal["apply_reward"](pet, player)
                player.goal_reward_applied = True

def show_savings_goal_popup(screen, font, player):
    WIDTH, HEIGHT = screen.get_size()
    # Ensure canonical savings fields are present and up-to-date
    player.savings = getattr(player, "savings", 0)
    player.savings_goal_target = getattr(player, "savings_goal_target", getattr(player, "goal_target_amount", 100))
    player.goal_progress = getattr(player, "savings", getattr(player, "goal_progress", 0))
    player.savings_goal_completed = getattr(player, "savings_goal_completed", player.savings >= player.savings_goal_target)
    scroll = 0
    title_font = pygame.font.SysFont("Arial", 28, bold=True)
    section_font = pygame.font.SysFont("Arial", 22, bold=True)
    text_font = pygame.font.SysFont("Arial", 20)
    input_font = pygame.font.SysFont("Arial", 24)
    button_font = pygame.font.SysFont("Arial", 24, bold=True)

    deposit_amount = ""
    deposit_message = ""
    row_height = 36

    # Prepare lines for scrolling
    lines = [
        (title_font, "Savings Goal", (80, 60, 0)),
        (section_font, f"Goal Name: {player.savings_goal_name}", (180, 140, 0)),
        (text_font, f"Target: {player.savings_goal_target} ChronoCoins", (0,0,0)),
        (text_font, f"Progress: {player.savings} / {player.savings_goal_target}", (0,0,0)),
        (text_font, f"Current ChronoCoins: {player.chronocoins}", (0,0,0)),
        (text_font, f"Weekly Budget Remaining: {player.weekly_budget - player.budget_spent}", (0,0,0)),
        (text_font, "", (0,0,0)),
        (section_font, "Deposit to Savings", (120, 60, 0)),
        (text_font, "Enter an amount below and click Deposit.", (0,0,0)),
        (text_font, "", (0,0,0)),
    ]

    running = True
    while running:
        screen.fill((245,245,220))
        nav_btns = draw_nav_buttons(screen, show_home=True, show_start=True)
        y = 30 - scroll

        # Render lines
        for entry in lines:
            fnt, text, color = entry
            surf = fnt.render(text, True, color)
            screen.blit(surf, (60, y))
            y += row_height if fnt != title_font else 38

        # Instruction box (right side) - baby blue
        info_box_w = min(360, WIDTH // 3)
        info_box_h = 420
        info_box_x = WIDTH - info_box_w - 40
        info_box_y = 60
        pygame.draw.rect(screen, (173, 216, 230), (info_box_x, info_box_y, info_box_w, info_box_h), border_radius=14)
        pygame.draw.rect(screen, (100, 140, 180), (info_box_x, info_box_y, info_box_w, info_box_h), 2, border_radius=14)

        instr_lines = [
            "How Savings Goals work:",
            "Each era has a savings goal which rewards your pet when reached.",
            "Target for this era: 100 ChronoCoins.",
            "To contribute, enter an amount in the box and click Deposit.",
            "Your progress and a progress bar update immediately.",
            "When you reach the target the goal completes and the reward is applied.",
            "Reward/Effect: Pet stats decrease 1.5X slower.",
            "You can track your current ChronoCoins and weekly budget on this screen."
        ]
        tx = info_box_x + 14
        ty = info_box_y + 12
        heading_font = pygame.font.SysFont("Arial", 18, bold=True)
        body_font = pygame.font.SysFont("Arial", 16)
        # Draw heading
        screen.blit(heading_font.render(instr_lines[0], True, (0,0,0)), (tx, ty))
        ty += heading_font.get_height() + 8
        # Draw body lines
        for line in instr_lines[1:]:
            # simple wrap: if line too wide, split at nearest space
            surf = body_font.render(line, True, (0,0,0))
            if surf.get_width() <= info_box_w - 28:
                screen.blit(surf, (tx, ty))
                ty += body_font.get_height() + 6
            else:
                # naive wrap
                words = line.split()
                cur = ""
                for w in words:
                    test = (cur + " " + w).strip()
                    test_surf = body_font.render(test, True, (0,0,0))
                    if test_surf.get_width() <= info_box_w - 28:
                        cur = test
                    else:
                        screen.blit(body_font.render(cur, True, (0,0,0)), (tx, ty))
                        ty += body_font.get_height() + 6
                        cur = w
                if cur:
                    screen.blit(body_font.render(cur, True, (0,0,0)), (tx, ty))
                    ty += body_font.get_height() + 6

        # Deposit input and button
        deposit_label = input_font.render("Deposit Amount:", True, (0,0,0))
        screen.blit(deposit_label, (60, y))
        input_box = pygame.Rect(260, y, 100, 36)
        pygame.draw.rect(screen, (255,255,255), input_box, border_radius=8)
        pygame.draw.rect(screen, (180,180,100), input_box, 2, border_radius=8)
        deposit_input = input_font.render(deposit_amount, True, (0,0,0))
        screen.blit(deposit_input, (input_box.x + 8, input_box.y + 4))

        btn_width, btn_height = 140, 44
        btn_x = input_box.right + 20
        btn_y = y
        btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        pygame.draw.rect(screen, (255, 221, 51), btn_rect, border_radius=12)
        pygame.draw.rect(screen, (180, 180, 100), btn_rect, 3, border_radius=12)
        btn_text = button_font.render("Deposit", True, (0,0,0))
        screen.blit(btn_text, (btn_x + btn_width//2 - btn_text.get_width()//2, btn_y + btn_height//2 - btn_text.get_height()//2))

        y += btn_height + 16

        # Deposit message
        if deposit_message:
            msg_txt = text_font.render(deposit_message, True, (200,60,60) if "fail" in deposit_message.lower() else (0,120,0))
            screen.blit(msg_txt, (60, y))
            y += row_height

        # Completion message
        if player.savings_goal_completed:
            complete_txt = text_font.render("Goal Complete! Reward Unlocked!", True, (200,120,0))
            screen.blit(complete_txt, (60, y))
            y += row_height

        # Navigation
        nav_txt = text_font.render("Up/Down or Mouse Wheel to scroll, Esc to exit", True, (100,100,100))
        screen.blit(nav_txt, (screen.get_width()//2 - nav_txt.get_width()//2, screen.get_height()-40))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_DOWN:
                    scroll = min(scroll + row_height, max(0, y - screen.get_height()))
                if event.key == pygame.K_UP:
                    scroll = max(0, scroll - row_height)
                elif event.key == pygame.K_BACKSPACE:
                    deposit_amount = deposit_amount[:-1]
                elif event.unicode.isdigit() and len(deposit_amount) < 6:
                    deposit_amount += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if "home" in nav_btns and nav_btns["home"].collidepoint(event.pos):
                    return
                if "start" in nav_btns and nav_btns["start"].collidepoint(event.pos):
                    pygame.quit()
                    os.execl(sys.executable, sys.executable, *sys.argv)
                if btn_rect.collidepoint(event.pos):
                    try:
                        amt = int(deposit_amount)
                        if amt <= 0:
                            deposit_message = "Enter a positive amount."
                            play_error_sound()
                        elif amt > getattr(player, "chronocoins", 0):
                            # Trying to deposit more than the player currently has
                            deposit_message = "You don't have that many ChronoCoins."
                            play_error_sound()
                        else:
                            success, msg = player.deposit_to_savings(amt)
                            deposit_message = msg
                            if success:
                                deposit_amount = ""
                                # Keep canonical progress fields in sync with player's savings
                                player.goal_progress = getattr(player, "savings", 0)
                                # Use canonical target field
                                target = getattr(player, "savings_goal_target", getattr(player, "goal_target_amount", 100))
                                # mark completion if reached
                                if player.savings >= target:
                                    player.savings_goal_completed = True
                                    player.goal_completed = True
                                    # Apply the requested achievement effect: stats decay at 1.5 instead of 1
                                    global HUNGER_DECAY, ENERGY_DECAY
                                    HUNGER_DECAY = 1.5
                                    ENERGY_DECAY = 1.5
                                    deposit_message = "Savings goal reached! Pet stats now decay at 1.5x."
                                else:
                                    deposit_message = f"Deposited {amt}. Progress: {player.savings}/{target}"
                    except ValueError:
                        deposit_message = "Enter a valid number."
                        play_error_sound()
                if event.button == 4:  # Scroll up
                    scroll = max(0, scroll - row_height)
                if event.button == 5:  # Scroll down
                    scroll = min(scroll + row_height, max(0, y - screen.get_height()))

# ============================================================
# Action System
# ============================================================

def home_page(screen, font):
    """
    Displays the starter screen with a custom background image and a centered Start Game button.
    """
    running = True
    WIDTH, HEIGHT = screen.get_size()
    # Load your custom background image for the starter screen
    bg = load_placeholder("assets/backgrounds/home.png", (WIDTH, HEIGHT))
    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    subtitle_font = pygame.font.SysFont("Arial", 28)
    button_font = pygame.font.SysFont("Arial", 28, bold=True)

    while running:
        screen.blit(bg, (0, 0))

        # Draw a semi-transparent overlay for better text readability
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 60))
        screen.blit(overlay, (0, 0))

        # Start Button
        btn_width, btn_height = 240, 70
        btn_rect = pygame.Rect(WIDTH // 2 - btn_width // 2, HEIGHT // 2 + 80, btn_width, btn_height)
        pygame.draw.rect(screen, (0, 120, 255), btn_rect, border_radius=20)
        pygame.draw.rect(screen, (255, 221, 51), btn_rect, 4, border_radius=20)
        btn_text = button_font.render("Start Game", True, (255, 255, 255))
        screen.blit(btn_text, (btn_rect.x + btn_width // 2 - btn_text.get_width() // 2, btn_rect.y + btn_height // 2 - btn_text.get_height() // 2))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                WIDTH, HEIGHT = screen.get_size()
                bg = load_placeholder("assets/backgrounds/home.png", (WIDTH, HEIGHT))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    play_confirm_sound()
                    return

def perform_care_action(player, pet, action, current_era):
    global ml_tip_text, show_ml_tip, effect_img, effect_timer  # <-- Add effect_img, effect_timer here

    # Map action to item name for each era
    era_item_map = {
        "feed": {
            "egypt": "Fish",
            "greece": "Olives",
            "medieval": "Bread & Cheese",
            "industrial": "Vegetable Stew",
            "modern": "Pet Kibble"
        },
        "play": {
            "egypt": "Papyrus Toy",
            "greece": "Courtyard Mat",
            "medieval": "Jousting Game",
            "industrial": "Park Run",
            "modern": "Drone Fetch"
        },
        "clean": {
            "egypt": "Nile Bath",
            "greece": "Well Water",
            "medieval": "Sponge Bath",
            "industrial": "Tin Tub Wash",
            "modern": "Auto Shower"
        },
        "health": {
            "egypt": "Honey Remedy",
            "greece": "Herbal Ointment",
            "medieval": "Healer Visit",
            "industrial": "Doctor Visit",
            "modern": "Vet Checkup"
        }
    }

    era_title = current_era.title()
    item_name = era_item_map[action][current_era]
    item_data = ERA_COST_TABLE[era_title][item_name]
    cost = item_data["cost"]
    effect = item_data["effect"]

    success, message = player.deduct_chronocoins(cost, action, era_title)
    if not success:
        ml_tip_text = message
        show_ml_tip = True
        return False

    # --- Track stats before ---
    before = {
        "hunger": int(pet.hunger),
        "happiness": int(pet.happiness),
        "energy": int(pet.energy),
        "health": int(pet.health),
        "coins": int(player.chronocoins)
    }

    # Apply stat changes from effect dict
    for stat, value in effect.items():
        setattr(pet, stat.lower(), getattr(pet, stat.lower()) + value)
    pet.clamp_stats()

    # --- Track stats after ---
    after = {
        "hunger": int(pet.hunger),
        "happiness": int(pet.happiness),
        "energy": int(pet.energy),
        "health": int(pet.health),
        "coins": int(player.chronocoins)
    }

    # --- Build concise diary log with custom verbs ---
    action_verbs = {
        "feed": "fed",
        "play": "played with",
        "clean": "cleaned",
        "health": "healed",
        "rest": "rested"
    }

    changes = []
    for stat in ["hunger", "happiness", "energy", "health"]:
        if before[stat] != after[stat]:
            changes.append(f"{stat.capitalize()}: {after[stat]}")
    if before["coins"] != after["coins"]:
        changes.append(f"Coins: {after['coins']}")

    verb = action_verbs.get(action, f"{action}ed")
    diary.log(
        f"{pet.name} was {verb}. " + ", ".join(changes)
    )

    # Reward ChronoCoins for good care
    if all(getattr(pet, stat) > 70 for stat in ["hunger", "happiness", "energy", "health"]):
        player.earn_coins(10, source="good care")
    
    era_key = current_era.lower()
    if action in ERA_ACTION_ITEMS.get(era_key, {}):
        img_path = ERA_ACTION_ITEMS[era_key][action]
        effect_img = load_placeholder(img_path, (80, 80))
        effect_timer = pygame.time.get_ticks() + 3000

    return True

# ============================================================
# Report System
# ============================================================
def diary_screen(screen, font, diary, player):
    #============================================================
    #Displays the read-only Diary & Spending Tracker screen.

    #Purpose:
    # - Shows real gameplay activity log (diary entries).
    # - Displays financial summary pulled from Player object.
    # - Allows scrolling through entries.
    # - Does NOT allow editing of gameplay data.

    # This function reflects actual recorded gameplay.
    # ============================================================

    scroll = 0
    entries = diary.get_entries()
    summary_data = player.get_financial_summary()
    WIDTH, HEIGHT = screen.get_size()
    title_font = pygame.font.SysFont("Arial", 28, bold=True)
    section_font = pygame.font.SysFont("Arial", 22, bold=True)
    text_font = pygame.font.SysFont("Arial", 18)
    small_font = pygame.font.SysFont("Arial", 16)
    entry_box_height = 38
    entry_box_margin = 12
    max_entries_shown = 8

    # Prepare summary lines
    summary_lines = [
        ("ChronoCoins:", str(summary_data['chronocoins'])),
        ("Weekly Budget:", f"{summary_data['budget_remaining']}/{player.weekly_budget}"),
        ("Total Earned:", str(summary_data['total_earned'])),
        ("Total Spent:", str(summary_data['total_spent'])),
    ]
    # Category summary
    cat_lines = [(cat.capitalize(), str(amt)) for cat, amt in summary_data['by_category'].items()]
    era_lines = [(era.capitalize(), str(amt)) for era, amt in summary_data['by_era'].items()]

    while True:
        screen.fill((235, 240, 255))
        nav_btns = draw_nav_buttons(screen, show_home=True, show_start=True)
        # Title
        title = title_font.render("Diary & Spending Tracker", True, (40, 40, 80))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        # Entries section
        entries_x = 60
        entries_y = 90
        entries_w = WIDTH//2 - 80
        entries_h = entry_box_height * max_entries_shown + entry_box_margin * (max_entries_shown-1) + 24

        pygame.draw.rect(screen, (255,255,255), (entries_x-10, entries_y-10, entries_w+20, entries_h+20), border_radius=18)
        pygame.draw.rect(screen, (180,180,220), (entries_x-10, entries_y-10, entries_w+20, entries_h+20), 3, border_radius=18)
        section = section_font.render("Recent Activity", True, (60,60,120))
        screen.blit(section, (entries_x, entries_y-38))

        num_entries_shown = min(max_entries_shown, max(0, len(entries) - scroll))
        for i, entry in enumerate(entries[scroll:scroll+max_entries_shown]):
            y = entries_y + i * (entry_box_height + entry_box_margin)
            pygame.draw.rect(screen, (245,245,255), (entries_x, y, entries_w, entry_box_height), border_radius=10)
            pygame.draw.rect(screen, (200,200,220), (entries_x, y, entries_w, entry_box_height), 1, border_radius=10)
            entry_txt = text_font.render(str(entry), True, (40,40,60))
            screen.blit(entry_txt, (entries_x + 12, y + entry_box_height//2 - entry_txt.get_height()//2))

        # Summary section
        summary_x = WIDTH//2 + 20
        summary_y = 190
        summary_w = WIDTH//2 - 80
        summary_h = 500

        pygame.draw.rect(screen, (255,255,255), (summary_x-10, summary_y-10, summary_w+20, summary_h+20), border_radius=18)
        pygame.draw.rect(screen, (180,180,220), (summary_x-10, summary_y-10, summary_w+20, summary_h+20), 3, border_radius=18)
        section = section_font.render("Summary", True, (60,60,120))
        screen.blit(section, (summary_x, summary_y-38))

        y = summary_y
        for label, value in summary_lines:
            label_txt = text_font.render(label, True, (0,0,0))
            value_txt = text_font.render(value, True, (40,80,0))
            screen.blit(label_txt, (summary_x+10, y))
            screen.blit(value_txt, (summary_x+180, y))
            y += 32

        # Category breakdown
        cat_title = small_font.render("By Category:", True, (80,80,120))
        screen.blit(cat_title, (summary_x+10, y+8))
        for i, (cat, amt) in enumerate(cat_lines):
            cat_txt = small_font.render(f"{cat}: ", True, (0,0,0))
            amt_txt = small_font.render(amt, True, (40,80,0))
            screen.blit(cat_txt, (summary_x+30, y+32+i*22))
            screen.blit(amt_txt, (summary_x+160, y+32+i*22))
        y += 32 + len(cat_lines)*22

        # Era breakdown
        era_title = small_font.render("By Era:", True, (80,80,120))
        screen.blit(era_title, (summary_x+10, y+8))
        for i, (era, amt) in enumerate(era_lines):
            era_txt = small_font.render(f"{era}: ", True, (0,0,0))
            amt_txt = small_font.render(amt, True, (40,80,0))
            screen.blit(era_txt, (summary_x+30, y+32+i*22))
            screen.blit(amt_txt, (summary_x+160, y+32+i*22))

        # Navigation
        nav_txt = text_font.render("Up/Down to scroll, Esc to exit", True, (100,100,100))
        screen.blit(nav_txt, (WIDTH//2 - nav_txt.get_width()//2, HEIGHT-40))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    scroll = min(max(0, len(entries)-max_entries_shown), scroll+1)
                if event.key == pygame.K_UP:
                    scroll = max(0, scroll-1)
                if event.key == pygame.K_ESCAPE: return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if "home" in nav_btns and nav_btns["home"].collidepoint(event.pos):
                    return
                if "start" in nav_btns and nav_btns["start"].collidepoint(event.pos):
                    play_confirm_sound()
                    pygame.quit()
                    os.execl(sys.executable, sys.executable, *sys.argv)
                if event.button == 4:  # Mouse wheel up
                    scroll = max(0, scroll-1)
                if event.button == 5:  # Mouse wheel down
                    scroll = min(max(0, len(entries)-max_entries_shown), scroll+1)
import copy
def custom_report_screen(screen, font, diary, player):
    # ============================================================
    # Displays the Custom Output Report screen.

    #Purpose:
    #- Uses SAME visual format as diary screen.
    #- Allows user to add/remove action lines.
    #- Calculates a simulated summary based on edited list.
    #- Does NOT modify real gameplay data.
    #- Resets changes when user exits screen.

    #This satisfies rubric requirement:
    #Output reports allow user to customize and analyze information.
    
     # ============================================================
    import copy
    editable_action_log = copy.deepcopy(diary.get_entries())
    WIDTH, HEIGHT = screen.get_size()
    scroll = 0
    title_font = pygame.font.SysFont("Arial", 28, bold=True)
    section_font = pygame.font.SysFont("Arial", 22, bold=True)
    text_font = pygame.font.SysFont("Arial", 18)
    small_font = pygame.font.SysFont("Arial", 16)
    entry_box_height = 38
    entry_box_margin = 12
    max_entries_shown = 8

    predefined_actions = [
        "Pet was fed. Hunger: 65, Coins: 90",
        "Pet was played with. Happiness: 70, Coins: 85",
        "Pet was rested. Energy: 80, Coins: 85",
        "Pet was cleaned. Health: 75, Coins: 80",
        "Pet was healed. Health: 90, Coins: 65"
    ]

    summary = None

    running = True
    while running:
        screen.fill((235, 240, 255))
        nav_btns = draw_nav_buttons(screen, show_home=True, show_start=True)
        title = title_font.render("Custom Output Report", True, (40, 40, 80))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        # --- Editable Actions Section (left) ---
        entries_x = 60
        entries_y = 90
        entries_w = WIDTH//2 - 80
        entries_h = entry_box_height * max_entries_shown + entry_box_margin * (max_entries_shown-1) + 24

        pygame.draw.rect(screen, (255,255,255), (entries_x-10, entries_y-10, entries_w+20, entries_h+20), border_radius=18)
        pygame.draw.rect(screen, (180,180,220), (entries_x-10, entries_y-10, entries_w+20, entries_h+20), 3, border_radius=18)
        section = section_font.render("Editable Actions", True, (60,60,120))
        screen.blit(section, (entries_x, entries_y-38))

        num_entries_shown = min(max_entries_shown, max(0, len(editable_action_log) - scroll))
        remove_btns = []
        for i, entry in enumerate(editable_action_log[scroll:scroll+max_entries_shown]):
            y = entries_y + i * (entry_box_height + entry_box_margin)
            pygame.draw.rect(screen, (245,245,255), (entries_x, y, entries_w, entry_box_height), border_radius=10)
            pygame.draw.rect(screen, (200,200,220), (entries_x, y, entries_w, entry_box_height), 1, border_radius=10)
            entry_txt = text_font.render(str(entry), True, (40,40,60))
            screen.blit(entry_txt, (entries_x + 12, y + entry_box_height//2 - entry_txt.get_height()//2))
            btn_rect = pygame.Rect(entries_x + entries_w - 40, y + 6, 28, 28)
            pygame.draw.rect(screen, (255,120,120), btn_rect, border_radius=8)
            minus_txt = text_font.render("-", True, (255,255,255))
            screen.blit(minus_txt, (btn_rect.x + 8, btn_rect.y + 2))
            remove_btns.append(btn_rect)

        # Add predefined actions
        add_y = entries_y + entries_h + 24
        add_label = small_font.render("Add Action:", True, (0,0,0))
        screen.blit(add_label, (entries_x, add_y))
        add_btns = []
        for j, act in enumerate(predefined_actions):
            btn_rect = pygame.Rect(entries_x + 90 + j*160, add_y, 150, 28)
            pygame.draw.rect(screen, (200,255,200), btn_rect, border_radius=8)
            act_txt = small_font.render(act.split(".")[0], True, (0,80,0))
            screen.blit(act_txt, (btn_rect.x+8, btn_rect.y+4))
            add_btns.append((btn_rect, act))

        # Results button
        results_btn_rect = pygame.Rect(entries_x, add_y + 40, 120, 36)
        pygame.draw.rect(screen, (255, 221, 51), results_btn_rect, border_radius=10)
        pygame.draw.rect(screen, (180, 180, 100), results_btn_rect, 2, border_radius=10)
        results_txt = text_font.render("Results", True, (0,0,0))
        screen.blit(results_txt, (results_btn_rect.x + 20, results_btn_rect.y + 6))

        # --- Summary Section (right, next to actions) ---
        summary_x = WIDTH//2 + 20
        summary_y = 90
        summary_w = WIDTH//2 - 80
        summary_h = 320

        pygame.draw.rect(screen, (255,255,255), (summary_x-10, summary_y-10, summary_w+20, summary_h+20), border_radius=18)
        pygame.draw.rect(screen, (180,180,220), (summary_x-10, summary_y-10, summary_w+20, summary_h+20), 3, border_radius=18)
        section = section_font.render("Custom Report Summary", True, (60,60,120))
        screen.blit(section, (summary_x, summary_y-38))

        y = summary_y
        if summary:
            for label, value in summary.items():
                label_txt = text_font.render(label, True, (0,0,0))
                value_txt = text_font.render(str(value), True, (40,80,0))
                screen.blit(label_txt, (summary_x+10, y))
                screen.blit(value_txt, (summary_x+260, y))  # Increased spacing here
                y += 32
        else:
            info_txt = text_font.render("Press Results to analyze.", True, (120,120,120))
            screen.blit(info_txt, (summary_x+10, y))

        # Navigation
        nav_txt = text_font.render("Up/Down to scroll, Esc to exit", True, (100,100,100))
        screen.blit(nav_txt, (WIDTH//2 - nav_txt.get_width()//2, HEIGHT-40))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    scroll = min(max(0, len(editable_action_log)-max_entries_shown), scroll+1)
                if event.key == pygame.K_UP:
                    scroll = max(0, scroll-1)
                if event.key == pygame.K_ESCAPE: return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i, btn in enumerate(remove_btns[:num_entries_shown]):
                    if btn.collidepoint(mx, my):
                        idx = scroll + i
                        if 0 <= idx < len(editable_action_log):
                            del editable_action_log[idx]
                        break
                for btn, act in add_btns:
                    if btn.collidepoint(mx, my):
                        editable_action_log.append(act)
                        break
                if results_btn_rect.collidepoint(mx, my):
                    # Calculate summary
                    total_coins_spent = 0
                    total_hunger_change = 0
                    total_happiness_change = 0
                    total_energy_change = 0
                    total_health_change = 0
                    budget_usage = 0
                    savings_impact = 0
                    for entry in editable_action_log:
                        entry_str = str(entry)
                        if "Coins:" in entry_str:
                            try:
                                coins = int(entry_str.split("Coins:")[1].split(",")[0].strip())
                                total_coins_spent += coins
                                if "fed" in entry_str:
                                    total_hunger_change += 15
                                if "played" in entry_str:
                                    total_happiness_change += 15
                                if "rested" in entry_str:
                                    total_energy_change += 15
                                if "cleaned" in entry_str:
                                    total_health_change += 10
                                if "healed" in entry_str:
                                    total_health_change += 20
                            except Exception:
                                pass
                    summary = {
                        "Total Coins Spent": total_coins_spent,
                        "Total Hunger Change": total_hunger_change,
                        "Total Happiness Change": total_happiness_change,
                        "Total Energy Change": total_energy_change,
                        "Total Health Change": total_health_change,
                        "Budget Usage": budget_usage,
                        "Savings Impact": savings_impact
                    }
                if "home" in nav_btns and nav_btns["home"].collidepoint(mx, my):
                    return
                if "start" in nav_btns and nav_btns["start"].collidepoint(mx, my):
                    pygame.quit()
                    os.execl(sys.executable, sys.executable, *sys.argv)

def show_era_summary(screen, font, player, era_name):
    WIDTH, HEIGHT = screen.get_size()
    summary = player.get_financial_summary()
    by_category = summary['by_category']
    if by_category:
        most_spent_cat = max(by_category, key=by_category.get)
    else:
        most_spent_cat = "None"
    
    lesson = ERA_LESSONS[era_name]  # <-- Add this line

    # Save summary to JSON
    summary_data = {
        "era": era_name,
        "total_earned": summary['total_earned'],
        "total_spent": summary['total_spent'],
        "savings": summary['savings'],
        "most_spent_category": most_spent_cat,
        "historical_concept": lesson['title'],
        "timestamp": datetime.datetime.now().isoformat()
    }
    os.makedirs("data", exist_ok=True)
    if os.path.exists("data/era_summaries.json"):
        with open("data/era_summaries.json", "r") as f:
            all_summaries = json.load(f)
    else:
        all_summaries = []
    all_summaries.append(summary_data)
    with open("data/era_summaries.json", "w") as f:
        json.dump(all_summaries, f, indent=2)

    # Display popup
    popup_width = 500
    popup_height = 350
    popup_x = (WIDTH - popup_width) // 2
    popup_y = (HEIGHT - popup_height) // 2
    title_font = pygame.font.SysFont("Arial", 28, bold=True)
    text_font = pygame.font.SysFont("Arial", 22)
    button_font = pygame.font.SysFont("Arial", 24, bold=True)

    running = True
    while running:
        pygame.draw.rect(screen, (255, 255, 220), (popup_x, popup_y, popup_width, popup_height), border_radius=18)
        pygame.draw.rect(screen, (180, 180, 100), (popup_x, popup_y, popup_width, popup_height), 4, border_radius=18)
        y = popup_y + 30
        title = title_font.render(f"{era_name.capitalize()} Era Complete!", True, (80, 60, 0))
        screen.blit(title, (popup_x + (popup_width - title.get_width()) // 2, y))
        y += 50
        lines = [
            f"Total Earned: {summary['total_earned']}",
            f"Total Spent: {summary['total_spent']}",
            f"Savings: {summary['savings']}",
            f"Most Spent Category: {most_spent_cat.capitalize()}",
            f"Historical Concept Learned:",
            f"{lesson['title']}"
        ]
        for line in lines:
            txt = text_font.render(line, True, (0,0,0))
            screen.blit(txt, (popup_x + 40, y))
            y += 36

        # Continue button
        btn_width, btn_height = 180, 50
        btn_x = popup_x + popup_width//2 - btn_width//2
        btn_y = popup_y + popup_height - btn_height - 24
        btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        pygame.draw.rect(screen, (255, 221, 51), btn_rect, border_radius=14)
        pygame.draw.rect(screen, (180, 180, 100), btn_rect, 3, border_radius=14)
        btn_text = button_font.render("Continue", True, (0,0,0))
        screen.blit(btn_text, (btn_x + btn_width//2 - btn_text.get_width()//2, btn_y + btn_height//2 - btn_text.get_height()//2))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    play_confirm_sound()
                    running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    running = False

def show_name_warning(screen, font, message="You must enter a name to continue!"):
    # ============================================================
    # Displays temporary warning popup if user tries to continue
    # without entering a pet name.
    #
    # Purpose:
    # - User validation
    # - Improves UX clarity
    # - Prevents invalid game state
    # ============================================================
    play_error_sound()
    WIDTH, HEIGHT = screen.get_size()
    popup_width = 500
    popup_height = 80
    popup_x = (WIDTH - popup_width) // 2
    popup_y = HEIGHT // 2 - popup_height // 2
    warning_font = pygame.font.SysFont("Arial", 24, bold=True)
    timer = pygame.time.get_ticks()
    while pygame.time.get_ticks() - timer < 2000:  # Show for 2 seconds
        pygame.draw.rect(screen, (255, 221, 51), (popup_x, popup_y, popup_width, popup_height), border_radius=18)
        pygame.draw.rect(screen, (180, 180, 100), (popup_x, popup_y, popup_width, popup_height), 3, border_radius=18)
        txt = warning_font.render(message, True, (120, 0, 0))
        screen.blit(txt, (popup_x + popup_width//2 - txt.get_width()//2, popup_y + popup_height//2 - txt.get_height()//2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.time.Clock().tick(30)

def mission_screen(screen, font, era, pet, player):
    # ============================================================
    #Displays interactive mission screen for selected era.

    #Purpose:
    #- Loads era-specific missions.
   #- Displays interactive objects.
    #- Tracks mission progress.
   #- Rewards coins upon completion.
   #- Unlocks next era when main mission is complete.

    #Demonstrates:
    #- Conditional branching by era
    #- Dynamic asset loading
   # - State tracking
    #- Player reward system
    # ============================================================
   missions = MISSIONS[era]
   current_mission = next((m for m in missions if not m["complete"]), None)
   running = True
   
   # --- implements interactive help menu ---
   help_state = "menu"   
   
   # --- Interactive objects for each mission ---
   object_positions = []
   object_clicked = []
   object_img = None
   discus_pos = [0, 0]
   discus_thrown = False
   # Shaking state will be initialized AFTER we set object_positions below
   shake_duration = 1500  # milliseconds (1.5s)
   object_shaking = []



   # Setup objects based on era and mission name
   if era == "egypt":
       if current_mission and current_mission["name"] == "Collect Stones":
           object_positions = [(220, 320), (420, 320), (620, 320)]
           object_clicked = [False, False, False]
           object_img = load_placeholder("assets/items/rock.png", (60, 60))
       elif current_mission and current_mission["name"] == "Build Ramp":
           object_positions = [(320, 340), (520, 340)]
           object_clicked = [False, False]
           object_img = load_placeholder("assets/items/wood.png", (80, 40))
       elif current_mission and current_mission["name"] == "Build Pyramid":
           object_positions = [(250, 370), (350, 370), (450, 370), (550, 370), (650, 370)]
           object_clicked = [False]*5
           object_img = load_placeholder("assets/items/brick.png", (50, 50))


   elif era == "greece":
       if current_mission and current_mission["name"] == "Train Running":
           object_positions = [(250, 320), (450, 320), (650, 320)]
           object_clicked = [False, False, False]
           object_img = load_placeholder("assets/items/shoes.png", (60, 60))
       elif current_mission and current_mission["name"] == "Throw Discus":
           discus_pos = [300, 350]
           discus_thrown = False
           object_img = load_placeholder("assets/items/discus.png", (60, 60))
       elif current_mission and current_mission["name"] == "Win Olympics":
           object_positions = [(250, 370), (350, 370), (450, 370), (550, 370), (650, 370)]
           object_clicked = [False]*5
           object_img = load_placeholder("assets/items/medal.png", (50, 50))


   elif era == "medieval":
       if current_mission and current_mission["name"] == "Gather Herbs":
           object_positions = [(220, 320), (420, 320), (620, 320)]
           object_clicked = [False, False, False]
           object_img = load_placeholder("assets/items/herbs.png", (60, 60))
       elif current_mission and current_mission["name"] == "Mix Potions":
           object_positions = [(350, 340), (550, 340)]
           object_clicked = [False, False]
           object_img = load_placeholder("assets/items/potion.png", (60, 80))
       elif current_mission and current_mission["name"] == "Craft Festival Potion":
           object_positions = [(250, 370), (350, 370), (450, 370), (550, 370), (650, 370)]
           object_clicked = [False]*5
           object_img = load_placeholder("assets/items/wand.png", (50, 70))


   elif era == "industrial":
       if current_mission and current_mission["name"] == "Collect Coal":
           object_positions = [(220, 320), (420, 320), (620, 320)]
           object_clicked = [False, False, False]
           object_img = load_placeholder("assets/items/coal.png", (60, 60))
       elif current_mission and current_mission["name"] == "Repair Gear":
           object_positions = [(350, 340), (550, 340)]
           object_clicked = [False, False]
           object_img = load_placeholder("assets/items/gear.png", (60, 60))
       elif current_mission and current_mission["name"] == "Fix Steam Engine":
           object_positions = [(250, 370), (350, 370), (450, 370), (550, 370), (650, 370)]
           object_clicked = [False]*5
           object_img = load_placeholder("assets/items/engine.png", (50, 50))


   elif era == "modern":
       if current_mission and current_mission["name"] == "Collect Data":
           object_positions = [(220, 320), (420, 320), (620, 320)]
           object_clicked = [False, False, False]
           object_img = load_placeholder("assets/items/graph.png", (60, 60))
       elif current_mission and current_mission["name"] == "Prepare Slides":
           object_positions = [(350, 340), (550, 340)]
           object_clicked = [False, False]
           object_img = load_placeholder("assets/items/projector.png", (80, 60))
       elif current_mission and current_mission["name"] == "Present Timeline":
           object_positions = [(250, 370), (350, 370), (450, 370), (550, 370), (650, 370)]
           object_clicked = [False]*5
           object_img = load_placeholder("assets/items/graph.png", (60, 60))

   # Ensure shaking array matches number of interactive objects (must be after object_positions is set)
   object_shaking = [0] * len(object_positions)

   # --- MaiN MISSION LOOP ---
   while running and current_mission:
       # Draw era background
       background_img = pygame.image.load("assets/backgrounds/mission_bg.png")
       background = pygame.transform.scale(background_img, (screen.get_width(), screen.get_height()))
       screen.blit(background, (0, 0))
       # --- Draw avatar and happy pet in the middle right ---
       avatar_img = load_placeholder(f"assets/player/{player.avatar}", (120,180))
       pet_happy_path = f"assets/pets/{pet.species}/{pet.species}_happy.png"
       if os.path.exists(pet_happy_path):
           pet_img = pygame.image.load(pet_happy_path).convert_alpha()
       else:
           pet_img = pet.sprite  # fallback to current sprite
       pet_img = pygame.transform.smoothscale(pet_img, pet.PET_DISPLAY_SIZE)

       # Position: middle right, side by side
       center_y = screen.get_height() // 2
       right_x = screen.get_width() * 3 // 4  # 3/4 across the screen

       avatar_rect = avatar_img.get_rect(center=(right_x - 80, center_y))
       pet_rect = pet_img.get_rect(center=(right_x + 60, center_y))

       screen.blit(avatar_img, avatar_rect)
       screen.blit(pet_img, pet_rect)

       nav_btns = draw_nav_buttons(screen, show_home=True, show_start=True)
       y = 60
       
       # --- Mission Name Box ---
       txt = font.render(f"{current_mission['name']} ({current_mission['type'].capitalize()}): {current_mission['goal']}", True, (0,0,0))
       box_rect = pygame.Rect(50, y-10, txt.get_width()+40, txt.get_height()+20)
       pygame.draw.rect(screen, (173,216,230), box_rect, border_radius=16)
       pygame.draw.rect(screen, (100,140,180), box_rect, 2, border_radius=16)
       screen.blit(txt, (box_rect.x+20, box_rect.y+10))
       y += box_rect.height + 10

       # --- Progress Box ---
       status = "✅" if current_mission["complete"] else f"{current_mission['progress']}/{current_mission['target']}"
       status_txt = font.render(f"Progress: {status}", True, (0,0,0))
       prog_rect = pygame.Rect(50, y-10, status_txt.get_width()+40, status_txt.get_height()+20)
       pygame.draw.rect(screen, (173,216,230), prog_rect, border_radius=16)
       pygame.draw.rect(screen, (100,140,180), prog_rect, 2, border_radius=16)
       screen.blit(status_txt, (prog_rect.x+20, prog_rect.y+10))

       # Draw interactive objects
       if era == "greece" and current_mission and current_mission["name"] == "Throw Discus":
           if not discus_thrown:
               screen.blit(object_img, discus_pos)
           else:
               discus_pos[0] += 20
               if discus_pos[0] < screen.get_width():
                   screen.blit(object_img, discus_pos)
               else:
                   discus_thrown = False
                   discus_pos = [300, 350]
                   current_mission["progress"] += 1
                   if current_mission["progress"] >= current_mission["target"]:
                       current_mission["complete"] = True
                       if current_mission["type"] == "main":
                           player.earn_coins(100, source="main mission")
                           return "main"
                       else:
                           player.earn_coins(50, source="small mission")
                           return "small"

           # --- Navigation Text Box for discus ---
           nav_txt = font.render("Click the discus to throw! Esc to exit", True, (0,0,0))
           nav_rect = pygame.Rect(50, screen.get_height() - 70, nav_txt.get_width() + 40, nav_txt.get_height() + 20)
           pygame.draw.rect(screen, (173,216,230), nav_rect, border_radius=16)
           pygame.draw.rect(screen, (100,140,180), nav_rect, 2, border_radius=16)
           screen.blit(nav_txt, (nav_rect.x + 20, nav_rect.y + 10))
       else:
           # Draw objects with shake animation if they are shaking
           now = pygame.time.get_ticks()
           for i, pos in enumerate(object_positions):
               # safety: ensure lists have correct length
               if i >= len(object_clicked):
                   continue
               if i < len(object_shaking) and object_shaking[i]:
                   elapsed = now - object_shaking[i]
                   if elapsed < shake_duration:
                       # smooth shake using sine/cosine
                       offset_x = int(math.sin(elapsed * 0.05 + i) * 8)
                       offset_y = int(math.cos(elapsed * 0.04 + i) * 4)
                       screen.blit(object_img, (pos[0] + offset_x, pos[1] + offset_y))
                   else:
                       # Shake finished: mark clicked, increment progress, handle completion
                       object_shaking[i] = 0
                       object_clicked[i] = True
                       current_mission["progress"] += 1
                       if current_mission["progress"] >= current_mission["target"]:
                           current_mission["complete"] = True
                           if current_mission["type"] == "main":
                               player.earn_coins(100, source="main mission")
                               return "main"
                           else:
                               player.earn_coins(50, source="small mission")
                               return "small"
               elif not object_clicked[i]:
                   screen.blit(object_img, pos)

           # Navigation text box for object missions
           nav_txt = font.render("Click objects to progress, Esc to exit", True, (0,0,0))
           nav_rect = pygame.Rect(50, screen.get_height() - 70, nav_txt.get_width() + 40, nav_txt.get_height() + 20)
           pygame.draw.rect(screen, (173,216,230), nav_rect, border_radius=16)
           pygame.draw.rect(screen, (100,140,180), nav_rect, 2, border_radius=16)
           screen.blit(nav_txt, (nav_rect.x + 20, nav_rect.y + 10))

       # Help box placement and rendering
       help_box_x = nav_rect.right + 32  # 32 pixels of space to the right
       help_box_y = nav_rect.y - 200     # Align vertically with nav box
       help_btns = draw_mission_help_box(screen, font, help_state, box_x=help_box_x, box_y=help_box_y)

       pygame.display.flip()


       for event in pygame.event.get():
           if event.type == pygame.QUIT: pygame.quit(); sys.exit()
           if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
               return False
           if event.type == pygame.MOUSEBUTTONDOWN:
               if "home" in nav_btns and nav_btns["home"].collidepoint(event.pos):
                   return  # Return to main loop (current era)
               if "start" in nav_btns and nav_btns["start"].collidepoint(event.pos):
                   play_confirm_sound()
                   pygame.quit()
                   os.execl(sys.executable, sys.executable, *sys.argv)  # Restart to start page
               mx, my = event.pos
               # --- Mission Help Box interaction (ALWAYS check first) ---
               help_clicked = False
               for btn_rect, next_state in help_btns:
                   if btn_rect.collidepoint(event.pos):
                       help_state = next_state
                       help_clicked = True
                       break
               if help_clicked:
                   continue  # Don't process object clicks if help was clicked
               
               if era == "greece" and current_mission and current_mission["name"] == "Throw Discus":
                   if not discus_thrown and pygame.Rect(discus_pos[0], discus_pos[1], object_img.get_width(), object_img.get_height()).collidepoint(mx, my):
                       discus_thrown = True
                       
               else:
                   for i, pos in enumerate(object_positions):
                       obj_rect = pygame.Rect(pos[0], pos[1], object_img.get_width(), object_img.get_height())
                       if not object_clicked[i] and obj_rect.collidepoint(mx, my):
                           # start shaking (do not immediately mark clicked/progress)
                           if object_shaking and i < len(object_shaking) and object_shaking[i] == 0:
                               object_shaking[i] = pygame.time.get_ticks()
                           break
       clock.tick(30)
    
# ============================================================
# Main Game Setup & Loop
# ============================================================

if os.path.exists("data/save.json"):
    os.remove("data/save.json")
# ============================================================
# MaiN GAME INITIALIZATION
    #- Clears previous save file.
    #- Loads home and customization screens.
    #- Initializes Player, Pet, Diary, and ml.
    #- Sets starting era and default stats.
# ============================================================
# --- Home and Customization ---
home_page(screen, font)
pet_avatar, pet_species, pet_name, screen = customization_page(screen, font)
WIDTH, HEIGHT = screen.get_size()
player = Player("Player", pet_avatar)
pet = Pet(pet_name, pet_species)
pet.avatar = pet_avatar
player.avatar = pet_avatar
pet.update_sprite()
set_saving_goal(player, eras[current_era] if 'current_era' in globals() else eras[0])

# Set up game state for Ancient Egypt
current_era = 0
unlocked_eras = [eras[0]]
player_credits = 50
pet_evolution = 0
pet_stats = {"hunger":50,"happiness":50,"energy":50,"health":50}
diary_data = []

# --- Create Classes ---
diary = Diary(diary_data, username=username)
ml = Petml()

# Restore saved game for this user (run once at startup)
existing_save = load_game(username)                      
if existing_save:                                        
        current_era = existing_save.get("current_era", 0)    
        unlocked_eras = existing_save.get("unlocked_eras", [eras[0]])  
        pet.hunger = existing_save.get("hunger", getattr(pet, "hunger", 50))  
        pet.happiness = existing_save.get("happiness", getattr(pet, "happiness", 50))  
        pet.energy = existing_save.get("energy", getattr(pet, "energy", 50))  
        pet.health = existing_save.get("health", getattr(pet, "health", 50))  
        if hasattr(player, "credits"):                         
            player.credits = existing_save.get("credits", getattr(player, "credits", getattr(player, "chronocoins", 0)))  
        else:                                                  
            player.chronocoins = existing_save.get("credits", getattr(player, "chronocoins", 0))  
        player.weekly_budget = existing_save.get("weekly_budget", getattr(player, "weekly_budget", getattr(player, "budget", 0)))  
        player.budget_spent = existing_save.get("budget_spent", getattr(player, "budget_spent", 0))  
        player.savings = existing_save.get("savings", getattr(player, "savings", 0))  
        try:                                                   
            player.update_financial_derived_fields()           
        except Exception:                                     
            pass

# Show the lesson for the starting era
show_era_lesson(screen, font, eras[current_era])

WIDTH, HEIGHT = screen.get_size()
background_img = pygame.image.load(f"assets/backgrounds/{eras[current_era]}.png")
background = pygame.transform.scale(background_img, (min(WIDTH, HEIGHT*16//9), HEIGHT))

show_fact_modal = False
show_ml_tip = False
mission_complete = False
fact_modal_text = ""
ml_tip_text = ""
effect_img = None
effect_timer = 0

# --- Animation State ---
animating = False
anim_start_time = 0
anim_duration = 2000  # milliseconds (2 seconds)
anim_target_x = None
anim_target_y = None
anim_action = None  # "diary", "mission", "customize", "map"

# ============================================================
# MaiN GAME LOOP
    # - Handles rendering.
    # - Updates pet state.
    # - Updates budget timer.
    # - Handles all UI interactions.
    # - Processes missions and era changes.
    # - Manages navigation between screens.
# ============================================================
DECAY_INTERVAL = 3000  # milliseconds (3 second)
HUNGER_DECAY = 1
ENERGY_DECAY = 1
HAPPINESS_DECAY = 0.5
HEALTH_DECAY = 0.2
running = True
last_decay_time = pygame.time.get_ticks()

while running:
    pet_x = WIDTH//2 + 100
    pet_y = HEIGHT//2 - pet.sprite.get_height()//2
    
    # In the main loop, before event handling:
    current_time = pygame.time.get_ticks()
    if current_time - last_decay_time > DECAY_INTERVAL:
        pet.hunger -= HUNGER_DECAY
        pet.energy -= ENERGY_DECAY
        pet.happiness -= HAPPINESS_DECAY
        pet.health -= HEALTH_DECAY
        pet.clamp_stats()
        last_decay_time = current_time
    if current_time - player.last_budget_refill > 60000:  # 1 minute = 1 week
        player.reset_week()
        player.last_budget_refill = current_time

    screen.blit(background, (0,0))
    # --- Animation Logic ---
    # Start positions (centered)
    pet_w, pet_h = pet.sprite.get_width(), pet.sprite.get_height()
    avatar_w = max(16, int(pet_w * 2.5))
    avatar_h = max(16, int(pet_h * 2.5))
    # Place pet at a fixed offset right of center
    pet_start_x = WIDTH//2 + 60
    pet_start_y = HEIGHT//2 - pet.sprite.get_height()//2
    # Reduce gap so the player's avatar sits closer to the pet (left of the pet).
    # Use a small adaptive gap based on pet width so layout scales with size.
    gap_to_pet = max(12, int(pet_w * 0.1))  # ~10% of pet width, minimum 12px
    avatar_start_x = pet_start_x - avatar_w - gap_to_pet
    avatar_start_y = HEIGHT//2 - avatar_h//2

    if not animating:
        avatar_x = avatar_start_x
        avatar_y = avatar_start_y
        pet_x = pet_start_x
        pet_y = pet_start_y
    else:
        elapsed = pygame.time.get_ticks() - anim_start_time
        t = min(elapsed / anim_duration, 1.0)
        # Both move to the same target (button center)
        avatar_x = int(avatar_start_x + (anim_target_x - avatar_start_x) * t)
        avatar_y = int(avatar_start_y + (anim_target_y - avatar_start_y) * t)
        pet_x = int(pet_start_x + (anim_target_x - pet_start_x) * t)
        pet_y = int(pet_start_y + (anim_target_y - pet_start_y) * t)
        if t >= 1.0:
            # Animation done, open the screen
            animating = False
            if anim_action == "diary":
                diary_screen(screen, font, diary, player)
            elif anim_action == "customize":
                pet_avatar, pet_species, pet_name, screen = customization_page(screen, font)
                pet.avatar = pet_avatar
                pet.species = pet_species
                pet.name = pet_name
                player.avatar = pet_avatar
                pet.update_sprite()
            elif anim_action == "map":
                era_idx = era_map_screen(screen, font, unlocked_eras, current_era)
                if era_idx is not None:
                    current_era = era_idx
                    background_img = pygame.image.load(f"assets/backgrounds/{eras[current_era]}.png")
                    background = pygame.transform.scale(background_img, (min(WIDTH, HEIGHT*16//9), HEIGHT))
                    set_saving_goal(player, eras[current_era])
                    show_era_lesson(screen, font, eras[current_era])
            elif anim_action == "mission":
                result = mission_screen(screen, font, eras[current_era], pet, player)
                # If the mission returned the main completion, unlock next era and show summary popup
                if result == "main":
                    # unlock the next era (if any)
                    if current_era + 1 < len(eras):
                        next_era = eras[current_era + 1]
                        if next_era not in unlocked_eras:
                            unlocked_eras.append(next_era)
                    # show era-complete summary for the era just finished
                    try:
                        show_era_summary(screen, font, player, eras[current_era])
                    except Exception as e:
                        print(f"[mission completion] failed to show era summary: {e}")
                # small mission returns don't change era but may still award coins (handled in mission_screen)
                elif result == "small":
                    # optional: small acknowledgement popup (kept minimal)
                    print("[mission] small mission completed")
            anim_action = None
            # Reset positions after returning
            avatar_x = avatar_start_x
            avatar_y = avatar_start_y
            pet_x = pet_start_x
            pet_y = pet_start_y
    # Update mood and sprite before drawing so visuals reflect current mood
    pet.mood = pet.get_mood()
    pet.update_sprite_by_mood()
    # Draw avatar and pet on the main screen.
    # Player avatar is scaled here to be 2.5x the pet size (only on the main screen).
    avatar_img = load_placeholder(f"assets/player/{player.avatar}", (avatar_w, avatar_h))
    screen.blit(avatar_img, (avatar_x, avatar_y))
    
    # Defensive: always ensure pet.sprite is a valid Surface BEFORE using it
    if not pet.sprite or not hasattr(pet.sprite, "get_height"):
        try:
            pet.sprite = pet.load_sprite()
            if not pet.sprite or not hasattr(pet.sprite, "get_height"):
                raise Exception("pet.sprite is still invalid after load_sprite()")
        except Exception as e:
            # Fallback: create a blank surface if loading fails
            pet.sprite = pygame.Surface((120, 120), pygame.SRCALPHA)
            pet.sprite.fill((200, 200, 200, 255))
            pygame.draw.rect(pet.sprite, (100, 100, 100), pet.sprite.get_rect(), 4)
    screen.blit(pet.sprite, (pet_x, pet_y))
   
    
    nav_btns = draw_nav_buttons(screen, show_home=False, show_start=True)  # <--- ADD THIS HERE


    # Draw effect image if timer is active
    if effect_img and pygame.time.get_ticks() < effect_timer:
        effect_x = pet_x + pet.sprite.get_width() + 20
        effect_y = pet_y + pet.sprite.get_height()//2 - 40
        screen.blit(effect_img, (effect_x, effect_y))
    else:
        effect_img = None
            

    # Now it's safe to use pet.sprite.get_width()
    pet.mood = pet.get_mood()
    mood_txt = font.render(f"Mood: {pet.mood}", True, (0,0,0))
    mood_x = pet_x + pet.sprite.get_width()//2 - mood_txt.get_width()//2

# --- ml TIP: Call after stat changes ---
    ml_tip = ml.get_ml_tip(pet, player, eras[current_era])
    ml_tip_text = ml_tip

    # Display pet mood with highlight
    highlight_rect = pygame.Rect(
        mood_x - 10,
        pet_y - mood_txt.get_height() - 18,
        mood_txt.get_width() + 20,
        mood_txt.get_height() + 8
    )
    pygame.draw.rect(screen, (255, 255, 153), highlight_rect, border_radius=12)
    screen.blit(mood_txt, (mood_x, pet_y - mood_txt.get_height() - 14))

    # Player avatar already drawn above on the main screen (scaled to 2.5x pet).
    # Display character's display name above the avatar mapped from avatar image filename
    char_name_map = {
        "boy1.png": "Alex",
        "girl1.png": "Maria",
        "boy2.png": "Carlos",
        "girl2.png": "Grace"
    }
    # player.avatar is the selected character image filename from customization_page
    display_name = char_name_map.get(getattr(player, "avatar", ""), getattr(player, "name", "Player"))
    name_txt = font.render(display_name, True, (0, 0, 0))
    name_x = avatar_x + avatar_w // 2 - name_txt.get_width() // 2
    name_rect = pygame.Rect(
        name_x - 10,
        avatar_y - name_txt.get_height() - 18,
        name_txt.get_width() + 20,
        name_txt.get_height() + 8
    )
    pygame.draw.rect(screen, (255, 255, 153), name_rect, border_radius=12)
    pygame.draw.rect(screen, (180, 180, 100), name_rect, 2, border_radius=12)
    screen.blit(name_txt, (name_x, avatar_y - name_txt.get_height() - 14))
    # --- Character Animation Logic ---
    if 'pet_x' not in locals():
        pet_x = WIDTH//2 + 100
        pet_y = HEIGHT//2 - pet.sprite.get_height()//2



    # --- DYNAMIC BUTTON POSITIONS ---
    button_y = HEIGHT - 60  # 60px from the bottom, adjust as needed
    buttons = {
        "feed": pygame.Rect(10, button_y, 100, 50),
        "play": pygame.Rect(120, button_y, 100, 50),
        "rest": pygame.Rect(230, button_y, 100, 50),
        "clean": pygame.Rect(340, button_y, 100, 50),
        "health": pygame.Rect(450, button_y, 100, 50),
        "diary": pygame.Rect(560, button_y, 100, 50),
        "custom_report": pygame.Rect(WIDTH - 180, 200, 170, 40),  # Below Savings Goal
        "customize": pygame.Rect(670, button_y, 120, 50),
        "map": pygame.Rect(800, button_y, 120, 50),
        "mission": pygame.Rect(10, button_y - 60, 120, 50),  # mission button above the row
        "help": pygame.Rect(WIDTH - 130, button_y, 120, 50),  # Help button at far right
        "cost_guide": pygame.Rect(WIDTH - 180, 50, 170, 40),  # Wider and still at far right
        "pet_guide": pygame.Rect(WIDTH - 180, 100, 170, 40),  # Pet Guide
        "savings_goal": pygame.Rect(WIDTH - 180, 150, 170, 40),  # Savings Goal below Pet Guide
    }
    buttons["help"] = pygame.Rect(buttons["map"].right + 10, button_y, 120, 50)
    buttons["start"] = pygame.Rect(WIDTH - 130, button_y, 120, 50)

    # Draw UI buttons (rounded)
    for name, rect in buttons.items():
        if name == "start":
            pygame.draw.rect(screen, (255,230,200), rect, border_radius=20)  # Same color as other Start buttons
            pygame.draw.rect(screen, (200,120,80), rect, 2, border_radius=20)
            text = font.render("Restart", True, (80,40,0))
        else:
            pygame.draw.rect(screen, (173,216,230), rect, border_radius=20)
            text = font.render(name.capitalize(), True, (0,0,0))
        screen.blit(text, (rect.x+10, rect.y+10))

    pygame.draw.rect(screen, (255, 255, 200), buttons["cost_guide"], border_radius=12)
    cost_guide_txt = font.render("Cost Guide", True, (0,0,0))
    
    pygame.draw.rect(screen, (255, 255, 200), buttons["custom_report"], border_radius=12)
    custom_report_txt = font.render("Custom Report", True, (0,0,0))
    screen.blit(
        custom_report_txt,
        (
            buttons["custom_report"].x + (buttons["custom_report"].width - custom_report_txt.get_width()) // 2,
            buttons["custom_report"].y + (buttons["custom_report"].height - custom_report_txt.get_height()) // 2
        )
    )
    # Center the text in the wider button
    screen.blit(
        cost_guide_txt,
        (
            buttons["cost_guide"].x + (buttons["cost_guide"].width - cost_guide_txt.get_width()) // 2,
            buttons["cost_guide"].y + (buttons["cost_guide"].height - cost_guide_txt.get_height()) // 2
        )
    )
    pygame.draw.rect(screen, (255, 255, 200), buttons["savings_goal"], border_radius=12)
    savings_goal_txt = font.render("Savings Goal", True, (0,0,0))
    screen.blit(
        savings_goal_txt,
        (
            buttons["savings_goal"].x + (buttons["savings_goal"].width - savings_goal_txt.get_width()) // 2,
            buttons["savings_goal"].y + (buttons["savings_goal"].height - savings_goal_txt.get_height()) // 2
        )
    )
    pygame.draw.rect(screen, (255, 255, 200), buttons["pet_guide"], border_radius=12)
    pet_guide_txt = font.render("Pet Guide", True, (0,0,0))
    screen.blit(
        pet_guide_txt,
        (
            buttons["pet_guide"].x + (buttons["pet_guide"].width - pet_guide_txt.get_width()) // 2,
            buttons["pet_guide"].y + (buttons["pet_guide"].height - pet_guide_txt.get_height()) // 2
        )
    )

    pet.mood = pet.get_mood()
    pet.update_sprite_by_mood()
    # --- Pet Stats Box (Left Middle) ---
    draw_stats_box(screen, pet, WIDTH, HEIGHT)


    if ml_tip_text:
        # ml Tip System:
        # Generates context-based suggestions based on:
        # - Pet stats
        # - Player spending
        # - Current era
        tip_font = pygame.font.SysFont("Arial", 20, bold=True)
        tip_surface = tip_font.render(ml_tip_text, True, (80, 60, 0))
        tip_box_height = 50
        tip_box_padding_x = 30  # horizontal padding inside box
        tip_box_padding_y = 10  # vertical padding inside box

        # Calculate box width based on text width + padding
        tip_box_width = tip_surface.get_width() + 2 * tip_box_padding_x
        tip_box_x = buttons["mission"].right + 20
        tip_box_y = buttons["mission"].y

        # Draw background box
        pygame.draw.rect(
            screen,
            (255, 255, 220),
            (tip_box_x, tip_box_y, tip_box_width, tip_box_height),
            border_radius=15
        )
        pygame.draw.rect(
            screen,
            (180, 180, 100),
            (tip_box_x, tip_box_y, tip_box_width, tip_box_height),
            3,
            border_radius=15
        )

        # Render and center the tip text vertically, left-aligned with padding
        screen.blit(
            tip_surface,
            (tip_box_x + tip_box_padding_x,
            tip_box_y + (tip_box_height - tip_surface.get_height()) // 2)
        )
        # Info bar
        pygame.draw.rect(screen, (173,216,230), (0,0,WIDTH,40))  # Baby blue
        era_title = ERA_DISPLAY_NAMES.get(eras[current_era], eras[current_era].capitalize())
        info_text = f"Pet: {pet.name} | ChronoCoins: {player.chronocoins} | Weekly Budget: {player.budget_remaining}/{player.weekly_budget} | Era: {era_title} | Mood: {pet.mood}"
        info_surface = font.render(info_text, True, (0,0,0))  # Black text
        screen.blit(info_surface, (10,10))
            
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Save game on exit (per-user)
            try:
                persist_game_state(username, current_era, unlocked_eras, pet, player)
                diary.save()
            except Exception as e:
                print(f"[save on quit] failed: {e}")
            running = False
            continue
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            WIDTH, HEIGHT = screen.get_size()
            background_img = pygame.image.load(f"assets/backgrounds/{eras[current_era]}.png")
            background = pygame.transform.scale(background_img, (min(WIDTH, HEIGHT*16//9), HEIGHT))
        if event.type == pygame.MOUSEBUTTONDOWN:
            if animating:
               continue
            if "start" in nav_btns and nav_btns["start"].collidepoint(event.pos):
                play_confirm_sound()
                pygame.quit()
                os.execl(sys.executable, sys.executable, *sys.argv)
            pos = event.pos
            if buttons["feed"].collidepoint(pos):
                perform_care_action(player, pet, "feed", eras[current_era])
            elif buttons["play"].collidepoint(pos):
                perform_care_action(player, pet, "play", eras[current_era])
            elif buttons["rest"].collidepoint(pos):
                pet.rest()  # If rest is free and not era-dependent, you can keep this
            elif buttons["clean"].collidepoint(pos):
                perform_care_action(player, pet, "clean", eras[current_era])
            elif buttons["health"].collidepoint(pos):
                perform_care_action(player, pet, "health", eras[current_era])
            if buttons["help"].collidepoint(pos):
                help_screen(screen, font)
            if buttons["start"].collidepoint(pos):
                pygame.quit()
                os.execl(sys.executable, sys.executable, *sys.argv)
            if buttons["savings_goal"].collidepoint(pos):
                show_savings_goal_popup(screen, font, player)
            if not animating:
                if buttons["diary"].collidepoint(pos):
                    animating = True
                    anim_start_time = pygame.time.get_ticks()
                    anim_action = "diary"
                    anim_target_x = buttons["diary"].centerx
                    anim_target_y = buttons["diary"].centery
                elif buttons["customize"].collidepoint(pos):
                    animating = True
                    anim_start_time = pygame.time.get_ticks()
                    anim_action = "customize"
                    anim_target_x = buttons["customize"].centerx
                    anim_target_y = buttons["customize"].centery
                elif buttons["map"].collidepoint(pos):
                    animating = True
                    anim_start_time = pygame.time.get_ticks()
                    anim_action = "map"
                    anim_target_x = buttons["map"].centerx
                    anim_target_y = buttons["map"].centery
                elif buttons["mission"].collidepoint(pos):
                    animating = True
                    anim_start_time = pygame.time.get_ticks()
                    anim_action = "mission"
                    anim_target_x = buttons["mission"].centerx
                    anim_target_y = buttons["mission"].centery
            

            # Fact modal close
            if show_fact_modal:
                show_fact_modal = False
            # Mission complete modal close
            if mission_complete:
                mission_complete = False
            # ml tip close
            if show_ml_tip:
                show_ml_tip = False
            if buttons["custom_report"].collidepoint(pos):
                custom_report_screen(screen, font, diary, player)
            if buttons["help"].collidepoint(pos):
                help_screen(screen, font)
            if buttons["cost_guide"].collidepoint(pos):
                cost_guide_screen(screen, font)
            if buttons["pet_guide"].collidepoint(pos):
                show_pet_care_guide(screen, font, pet, player, eras, current_era)
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()



