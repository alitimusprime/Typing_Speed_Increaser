import pygame
import pygame.freetype
import sys
import random
import json

WINDOWED_SIZE = (1280, 960)
FULLSCREEN_SIZE = (1280, 960)
is_fullscreen = False


pygame.init()

screen = pygame.display.set_mode(WINDOWED_SIZE, pygame.RESIZABLE)
pygame.display.set_caption("Wordship")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

GAME_FONT = pygame.freetype.Font(None, 36)
game_over = False
start_time = pygame.time.get_ticks()
words_typed = 0
game_end_time = 0
game_state = "home"  


key_bindings = {
    "move_left": pygame.K_LSHIFT,
    "move_right": pygame.K_RSHIFT
}




# Load and scale the spaceship image
spaceship = pygame.image.load("Spaceship.png")
spaceship = pygame.transform.scale(spaceship, (50, 50))
spaceship_rect = spaceship.get_rect(midbottom=(400, 930))

# Game variables
current_word = ""
falling_words = []
words_to_type = ["python", "pygame", "coding", "game", "typing", "speed"]
projectiles = []
score = 0
lives = 3
word_delay = 10 # Delay in milliseconds between creating new words


# Load high score and controls from file
def save_data(high_score, controls):
    data = {
        'high_score': high_score,
        'controls': controls
    }
    with open('game_data.json', 'w') as f:
        json.dump(data, f)

def load_data():
    try:
        with open('game_data.json', 'r') as f:
            data = json.load(f)
        return data['high_score'], data['controls']
    except FileNotFoundError:
        return 0, {'move_left': pygame.K_LSHIFT, 'move_right': pygame.K_RSHIFT}
    
high_score, key_bindings = load_data()

def create_falling_word():
    word = random.choice(words_to_type)
    text_surface = font.render(word, True, (255, 255, 255))
    rect = text_surface.get_rect(topleft=(random.randint(50, 1230), -50))  # Start above the screen

    if not any(word["rect"].colliderect(rect) for word in falling_words):
        falling_words.append({
            "word": word,
            "rect": rect,
            "surface": text_surface,
            "alpha": 0,  # Start fully transparent
            "fade_in": True  # Flag to indicate fading in
        })

def draw_settings_menu():
    screen.fill((0, 0, 0))
    title_text, title_rect = GAME_FONT.render("Settings", (255, 255, 255))
    title_rect.center = (WINDOWED_SIZE[0] // 2, WINDOWED_SIZE[1] // 4)
    screen.blit(title_text, title_rect)

    left_key_button = draw_button(screen, f"Move Left: {pygame.key.name(key_bindings['move_left'])}", (WINDOWED_SIZE[0] // 2 - 150, WINDOWED_SIZE[1] // 2), (300, 50))
    right_key_button = draw_button(screen, f"Move Right: {pygame.key.name(key_bindings['move_right'])}", (WINDOWED_SIZE[0] // 2 - 150, WINDOWED_SIZE[1] // 2 + 70), (300, 50))
    back_button = draw_button(screen, "Back", (WINDOWED_SIZE[0] // 2 - 100, WINDOWED_SIZE[1] // 2 + 140), (200, 50))

    return left_key_button, right_key_button, back_button


def draw_home_screen():
    screen.fill((0, 0, 0))
    title_text, title_rect = GAME_FONT.render("Wordship", (255, 255, 255))
    title_rect.center = (WINDOWED_SIZE[0] // 2, WINDOWED_SIZE[1] // 4)
    screen.blit(title_text, title_rect)

    high_score_text, high_score_rect = GAME_FONT.render(f"High Score: {high_score}", (255, 255, 255))
    high_score_rect.center = (WINDOWED_SIZE[0] // 2, WINDOWED_SIZE[1] // 4 + 50)
    screen.blit(high_score_text, high_score_rect)

    play_button = draw_button(screen, "PLAY", (WINDOWED_SIZE[0] // 2 - 100, WINDOWED_SIZE[1] // 2), (200, 50))
    controls_button = draw_button(screen, "CONTROLS", (WINDOWED_SIZE[0] // 2 - 100, WINDOWED_SIZE[1] // 2 + 70), (200, 50))
    exit_button = draw_button(screen, "EXIT", (WINDOWED_SIZE[0] // 2 - 100, WINDOWED_SIZE[1] // 2 + 140), (200, 50))
    return play_button, controls_button, exit_button


def show_controls():
    screen.fill((0, 0, 0))
    controls_text = [
        "CONTROLS:",
        f"Move Left: {pygame.key.name(key_bindings['move_left'])}",
        f"Move Right: {pygame.key.name(key_bindings['move_right'])}",
        "Mouse: Move Ship",
        "Type words and press Enter to shoot"
    ]
    for i, text in enumerate(controls_text):
        text_surf, text_rect = GAME_FONT.render(text, (255, 255, 255))
        text_rect.center = (WINDOWED_SIZE[0] // 2, WINDOWED_SIZE[1] // 4 + i * 50)
        screen.blit(text_surf, text_rect)
    
    left_key_button = draw_button(screen, "Change Left Key", (WINDOWED_SIZE[0] // 2 - 150, WINDOWED_SIZE[1] // 2 + 100), (300, 50))
    right_key_button = draw_button(screen, "Change Right Key", (WINDOWED_SIZE[0] // 2 - 150, WINDOWED_SIZE[1] // 2 + 170), (300, 50))
    back_button = draw_button(screen, "BACK", (WINDOWED_SIZE[0] // 2 - 100, WINDOWED_SIZE[1] - 100), (200, 50))
    
    return left_key_button, right_key_button, back_button



def wait_for_key_press():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return event.key
        pygame.display.flip()
        clock.tick(60)


def shoot_projectile(word):
    projectiles.append({
        "x": spaceship_rect.centerx,
        "y": spaceship_rect.top,
        "word": word,
        "width": 30,
        "height": 15
    })

def draw_text_with_outline(surface, text_surface, rect):
    # Draw red outline
    pygame.draw.rect(surface, (255, 0, 0), rect.inflate(4, 4), 2)  # Inflate to create space for the outline
    # Blit the word inside the outlined rect
    surface.blit(text_surface, rect)

def calculate_wpm():
    end_time = game_end_time if game_over else pygame.time.get_ticks()
    minutes = (end_time - start_time) / 60000  # Convert milliseconds to minutes
    return int(words_typed / minutes) if minutes > 0 else 0


def draw_button(screen, text, position, size):
    button_rect = pygame.Rect(position, size)
    pygame.draw.rect(screen, (100, 100, 100), button_rect)
    pygame.draw.rect(screen, (200, 200, 200), button_rect, 2)
    text_surf, text_rect = GAME_FONT.render(text, (255, 255, 255))
    text_rect.center = button_rect.center
    screen.blit(text_surf, text_rect)
    return button_rect

word_timer = 0
word_delay = 2000  # Delay in milliseconds (e.g., 2000 ms = 2 seconds)
  # Main game loop
while True:
    if game_state == "home":
        play_button, controls_button, exit_button = draw_home_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    game_state = "playing"
                    start_time = pygame.time.get_ticks()
                elif controls_button.collidepoint(event.pos):
                    game_state = "controls"
                elif exit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

    # ... rest of the game loop ...    
    elif game_state == "controls":
        left_key_button, right_key_button, back_button = show_controls()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if left_key_button.collidepoint(event.pos):
                    key_bindings['move_left'] = wait_for_key_press()
                    save_data(high_score, key_bindings)
                elif right_key_button.collidepoint(event.pos):
                    key_bindings['move_right'] = wait_for_key_press()
                    save_data(high_score, key_bindings)
                elif back_button.collidepoint(event.pos):
                    game_state = "home"

    
        pygame.display.flip()

    elif game_state == "settings":
        left_key_button, right_key_button, back_button = draw_settings_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if left_key_button.collidepoint(event.pos):
                    key_bindings['move_left'] = wait_for_key_press()
                elif right_key_button.collidepoint(event.pos):
                    key_bindings['move_right'] = wait_for_key_press()
                elif back_button.collidepoint(event.pos):
                    game_state = "home"
    
    elif game_state == "playing":
          screen.fill((0, 0, 0))  # Black background

          # Event handling
          for event in pygame.event.get():
              if event.type == pygame.QUIT:
                  pygame.quit()
                  sys.exit()
              elif event.type == pygame.KEYDOWN:
                  if event.key == pygame.K_f:  # Press 'F' to toggle fullscreen
                      is_fullscreen = not is_fullscreen
                      if is_fullscreen:
                          screen = pygame.display.set_mode(FULLSCREEN_SIZE, pygame.FULLSCREEN)
                      else:
                          screen = pygame.display.set_mode(WINDOWED_SIZE)
                      spaceship_rect.midbottom = (screen.get_width() // 2, screen.get_height() - 20)
                  elif event.unicode.isalpha():
                      current_word += event.unicode
                  elif event.key == pygame.K_BACKSPACE:
                      current_word = current_word[:-1]
                  elif event.key == pygame.K_RETURN:
                      shoot_projectile(current_word)
                      current_word = ""

          # Move spaceship
          keys = pygame.key.get_pressed()
          mouse_moved = pygame.mouse.get_rel()[0] != 0

          # Movement using shift keys and mouse
          if keys[key_bindings['move_left']]:
              spaceship_rect.x = max(0, spaceship_rect.x - 5)
          if keys[key_bindings['move_right']]:
              spaceship_rect.x = min(WINDOWED_SIZE[0] - spaceship_rect.width, spaceship_rect.x + 5)
          if mouse_moved:
              target_x = pygame.mouse.get_pos()[0] - spaceship_rect.width / 2
              spaceship_rect.x += (target_x - spaceship_rect.x) * 0.1

          # Constrain spaceship to the screen bounds
          spaceship_rect.x = max(0, min(spaceship_rect.x, WINDOWED_SIZE[0] - spaceship_rect.width))

          # Create new falling words
          # Check if enough time has passed to create a new word
          if pygame.time.get_ticks() - word_timer > word_delay:
              create_falling_word()
              word_timer = pygame.time.get_ticks()  # Reset the timer after creating a word

          # Update and render falling words
          for word in falling_words[:]:
              word["rect"].y += 1
              if word["fade_in"]:
                  word["alpha"] += 5
                  if word["alpha"] >= 255:
                      word["alpha"] = 255
                      word["fade_in"] = False
              
              word_surface = word["surface"].copy()
              word_surface.set_alpha(word["alpha"])
              draw_text_with_outline(screen, word_surface, word["rect"])

              # Check if word hits the spaceship
              if word["rect"].colliderect(spaceship_rect):
                  falling_words.remove(word)
                  lives -= 1
                  if lives <= 0:
                      game_state = "game_over"
                      game_end_time = pygame.time.get_ticks()

              # Check if word reaches the bottom
              if word["rect"].bottom > WINDOWED_SIZE[1]:
                  falling_words.remove(word)
                  lives -= 1
                  if lives <= 0:
                      game_state = "game_over"
                      game_end_time = pygame.time.get_ticks()
          # Update and render projectiles
          for projectile in projectiles[:]:
              projectile["y"] -= 5
              pygame.draw.rect(screen, (255, 0, 0), (projectile["x"], projectile["y"], projectile["width"], projectile["height"]))

              # Check projectile collisions with words
              for word in falling_words[:]:
                  if word["rect"].colliderect(pygame.Rect(projectile["x"], projectile["y"], projectile["width"], projectile["height"])):
                      if projectile["word"].lower() == word["word"].lower():
                          falling_words.remove(word)
                          projectiles.remove(projectile)
                          score += 10
                          words_typed += 1
                          break

              # Remove projectiles that go off-screen
              if projectile["y"] < 0:
                  projectiles.remove(projectile)

                    
          # Render current word
          text_surface = font.render(current_word, True, (255, 255, 255))
          screen.blit(text_surface, (100, 910))

          # Render score and lives
          score_surface = font.render(f"Score: {score}", True, (200, 200, 200))
          screen.blit(score_surface, (10, 10))
          lives_surface = font.render(f"Lives: {lives}", True, (200, 200, 200))
          screen.blit(lives_surface, (10, 50))

          # Render spaceship
          screen.blit(spaceship, spaceship_rect)    
    elif game_state == "game_over":
        if score > high_score:
            high_score = score
            save_data(high_score, key_bindings)
    
        
        if 'final_wpm' not in locals():
            final_wpm = calculate_wpm()
    
        game_over_text, game_over_rect = GAME_FONT.render("Game Over!", (255, 0, 0))
        score_text, score_rect = GAME_FONT.render(f"Final Score: {score}", (255, 255, 255))
        wpm_text, wpm_rect = GAME_FONT.render(f"Words per Minute: {final_wpm}", (255, 255, 255))

        game_over_rect.center = (WINDOWED_SIZE[0] // 2, WINDOWED_SIZE[1] // 2 - 100)
        score_rect.center = (WINDOWED_SIZE[0] // 2, WINDOWED_SIZE[1] // 2)
        wpm_rect.center = (WINDOWED_SIZE[0] // 2, WINDOWED_SIZE[1] // 2 + 50)

        screen.blit(game_over_text, game_over_rect)
        screen.blit(score_text, score_rect)
        screen.blit(wpm_text, wpm_rect)

        restart_button = draw_button(screen, "Restart", (WINDOWED_SIZE[0] // 2 - 100, WINDOWED_SIZE[1] // 2 + 100), (200, 50))
        exit_button = draw_button(screen, "Exit", (WINDOWED_SIZE[0] // 2 - 100, WINDOWED_SIZE[1] // 2 + 170), (200, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    # Reset game variables
                    score = 0
                    lives = 3
                    falling_words.clear()
                    projectiles.clear()
                    current_word = ""
                    game_state = "playing"
                    start_time = pygame.time.get_ticks()
                    words_typed = 0
                elif exit_button.collidepoint(event.pos):
                    game_state = "home"
    pygame.display.flip()
    clock.tick(60)
