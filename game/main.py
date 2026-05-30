import math
import random
import sys
from array import array

import pygame

pygame.init()

try:
    pygame.mixer.init()
    SOUND_ENABLED = True
except pygame.error:
    SOUND_ENABLED = False

WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Shooter - Python")

FONT_LARGE = pygame.font.Font(None, 48)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_SMALL = pygame.font.Font(None, 24)

WHITE = (245, 245, 245)
LIGHT_GRAY = (180, 180, 180)
DARK_GRAY = (20, 20, 25)
GREEN = (94, 214, 101)
RED = (255, 75, 75)
BLUE = (93, 164, 255)
YELLOW = (255, 220, 90)
ZOMBIE_GREEN = (112, 194, 60)

clock = pygame.time.Clock()


def make_tone(frequency, duration, volume=0.08, wave="sine", sample_rate=44100, attack=0.0, decay=0.0):
    if not SOUND_ENABLED:
        return None

    frames = int(sample_rate * duration)
    samples = array("h")

    for index in range(frames):
        t = index / sample_rate
        envelope = 1.0

        if attack and t < attack:
            envelope = t / attack
        elif decay and t > duration - decay:
            envelope = (duration - t) / decay

        if wave == "square":
            raw = 1.0 if math.sin(2 * math.pi * frequency * t) >= 0 else -1.0
        elif wave == "saw":
            raw = 2 * (frequency * t - math.floor(frequency * t + 0.5))
        else:
            raw = math.sin(2 * math.pi * frequency * t)

        sample = int(max(-1.0, min(1.0, raw * envelope)) * 32767 * volume)
        samples.append(sample)

    return pygame.mixer.Sound(buffer=samples.tobytes())


def play_effect(frequency, duration, volume=0.08, wave="sine", attack=0.0, decay=0.0):
    if not SOUND_ENABLED:
        return

    sound = make_tone(frequency, duration, volume=volume, wave=wave, attack=attack, decay=decay)
    if sound is not None:
        sound.play()


def play_start_sound():
    play_effect(660, 0.12, volume=0.1, wave="sine", attack=0.01)


def play_shoot_sound():
    play_effect(880, 0.07, volume=0.08, wave="square")


def play_hit_sound():
    play_effect(320, 0.08, volume=0.08, wave="sine")


def play_life_loss_sound():
    play_effect(180, 0.14, volume=0.09, wave="sine", attack=0.01, decay=0.02)


def play_game_over_sound():
    play_effect(220, 0.3, volume=0.08, wave="saw", decay=0.05)
    pygame.time.delay(120)
    play_effect(140, 0.4, volume=0.08, wave="saw", decay=0.05)


class Player:
    def __init__(self):
        self.width = 48
        self.height = 48
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 6
        self.color = BLUE

    def move(self, dx):
        self.x += dx * self.speed
        self.x = max(0, min(WIDTH - self.width, self.x))

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), border_radius=12)
        pygame.draw.rect(surface, WHITE, (self.x + 10, self.y + 10, self.width - 20, self.height - 20), 2, border_radius=8)


class Bullet:
    def __init__(self, x, y):
        self.width = 8
        self.height = 18
        self.x = x
        self.y = y
        self.speed = 9
        self.color = YELLOW

    def update(self):
        self.y -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), border_radius=4)

    def off_screen(self):
        return self.y + self.height < 0


class Zombie:
    def __init__(self):
        self.width = 42
        self.height = 42
        self.x = random.randint(10, WIDTH - self.width - 10)
        self.y = -self.height
        self.speed = random.uniform(1.4, 2.8)
        self.color = ZOMBIE_GREEN

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), border_radius=10)
        pygame.draw.circle(surface, DARK_GRAY, (self.x + 10, int(self.y + 14)), 6)
        pygame.draw.circle(surface, DARK_GRAY, (self.x + self.width - 10, int(self.y + 14)), 6)
        pygame.draw.line(surface, DARK_GRAY, (self.x + 8, self.y + 30), (self.x + self.width - 8, self.y + 30), 3)

    def off_screen(self):
        return self.y > HEIGHT


def draw_background(surface):
    surface.fill(DARK_GRAY)
    for i in range(0, HEIGHT, 20):
        alpha = max(0, 80 - i // 6)
        line = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
        line.fill((40, 40, 50, alpha))
        surface.blit(line, (0, i))
    pygame.draw.rect(surface, (30, 30, 36), (0, HEIGHT - 100, WIDTH, 100))


def draw_ui(surface, score, lives):
    score_text = FONT_MEDIUM.render(f"Score: {score}", True, WHITE)
    lives_text = FONT_MEDIUM.render(f"Lives: {lives}", True, WHITE)
    surface.blit(score_text, (20, 20))
    surface.blit(lives_text, (WIDTH - lives_text.get_width() - 20, 20))
    pygame.draw.rect(surface, GREEN, (20, 60, 220, 22), border_radius=12)
    pygame.draw.rect(surface, RED, (250, 60, 220, 22), border_radius=12)
    intro = FONT_SMALL.render("Use the left/right arrows or A/D to move and Space to shoot", True, LIGHT_GRAY)
    surface.blit(intro, (WIDTH // 2 - intro.get_width() // 2, 22))
    pause_tip = FONT_SMALL.render("Press P to pause/resume", True, LIGHT_GRAY)
    surface.blit(pause_tip, (WIDTH // 2 - pause_tip.get_width() // 2, 52))


def get_start_button_rect():
    return pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 60)


def draw_start_menu(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))

    title = FONT_LARGE.render("Deadzone", True, GREEN)
    subtitle = FONT_SMALL.render("Defend your base from the incoming zombies.", True, WHITE)
    button_rect = get_start_button_rect()
    mouse_pos = pygame.mouse.get_pos()
    button_color = GREEN if button_rect.collidepoint(mouse_pos) else (88, 198, 98)

    pygame.draw.rect(surface, button_color, button_rect, border_radius=18)
    button_text = FONT_MEDIUM.render("Start", True, DARK_GRAY)
    surface.blit(
        button_text,
        (
            button_rect.centerx - button_text.get_width() // 2,
            button_rect.centery - button_text.get_height() // 2,
        ),
    )
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 90))
    surface.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 - 30))


def draw_game_over(surface, score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    game_over_text = FONT_LARGE.render("Game over", True, RED)
    score_text = FONT_MEDIUM.render(f"Final score: {score}", True, WHITE)
    restart_text = FONT_SMALL.render("Press R to restart or Esc to quit", True, LIGHT_GRAY)
    surface.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 80))
    surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 20))
    surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 28))


def draw_pause_overlay(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    paused_text = FONT_LARGE.render("Paused", True, WHITE)
    resume_text = FONT_SMALL.render("Press P to resume", True, LIGHT_GRAY)
    surface.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2 - 80))
    surface.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 - 20))


def reset_game():
    player = Player()
    bullets = []
    zombies = []
    score = 0
    lives = 3
    game_over = False
    spawn_cooldown = 0
    game_started = False
    game_paused = False
    return player, bullets, zombies, score, lives, game_over, spawn_cooldown, game_started, game_paused


def main():
    player, bullets, zombies, score, lives, game_over, spawn_cooldown, game_started, game_paused = reset_game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and game_over:
                    player, bullets, zombies, score, lives, game_over, spawn_cooldown, game_started, game_paused = reset_game()
                    continue
                if game_started and not game_over and event.key == pygame.K_p:
                    game_paused = not game_paused
                if game_started and event.key == pygame.K_SPACE and not game_over and not game_paused:
                    bullets.append(Bullet(player.x + player.width // 2 - 4, player.y - 18))
                    play_shoot_sound()
                if not game_started and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game_started = True
                    play_start_sound()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_started:
                if get_start_button_rect().collidepoint(event.pos):
                    game_started = True
                    play_start_sound()

        keys = pygame.key.get_pressed()
        if game_started and not game_over and not game_paused:
            dx = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += 1
            player.move(dx)

            for bullet in bullets[:]:
                bullet.update()
                if bullet.off_screen():
                    bullets.remove(bullet)

            for zombie in zombies[:]:
                zombie.update()
                if zombie.off_screen():
                    zombies.remove(zombie)
                    lives -= 1
                    play_life_loss_sound()
                    if lives <= 0:
                        game_over = True
                        play_game_over_sound()

            for zombie in zombies[:]:
                for bullet in bullets[:]:
                    bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
                    zombie_rect = pygame.Rect(zombie.x, zombie.y, zombie.width, zombie.height)
                    if bullet_rect.colliderect(zombie_rect):
                        bullets.remove(bullet)
                        zombies.remove(zombie)
                        score += 10
                        play_hit_sound()
                        break

            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
            for zombie in zombies[:]:
                zombie_rect = pygame.Rect(zombie.x, zombie.y, zombie.width, zombie.height)
                if player_rect.colliderect(zombie_rect):
                    zombies.remove(zombie)
                    lives -= 1
                    play_life_loss_sound()
                    if lives <= 0:
                        game_over = True
                        play_game_over_sound()

            if spawn_cooldown <= 0:
                zombies.append(Zombie())
                spawn_cooldown = max(16, 45 - score // 30)
            else:
                spawn_cooldown -= 1

        draw_background(WINDOW)
        player.draw(WINDOW)
        for bullet in bullets:
            bullet.draw(WINDOW)
        for zombie in zombies:
            zombie.draw(WINDOW)

        draw_ui(WINDOW, score, lives)

        if game_paused and game_started and not game_over:
            draw_pause_overlay(WINDOW)

        if not game_started:
            draw_start_menu(WINDOW)

        if game_over:
            draw_game_over(WINDOW, score)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
