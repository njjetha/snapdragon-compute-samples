import pygame
import sys
import random
from typing import Tuple

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_RADIUS = 10

BACKGROUND_COLOR = (255, 255, 255)
BALL_COLOR = (231, 19, 36)
PADDLE_COLOR = (53, 0, 172)

TEXT_COLOR = (0, 0, 0)
TEXT_BACKGROUND = (245, 246, 247)
SNAPDRAGON_RED = (231, 19, 36)

PADDLE_SPEED = 7
BALL_INITIAL_SPEED = 5
BALL_ACCELERATION_FACTOR = 0.1

MAX_SCORE = 5
last_scored_player = 1

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Two-Player Pong")


def render_wrapped_text(
    surface: pygame.surface.Surface,
    text: str,
    font: pygame.font.Font,
    color: pygame.color.Color,
    background_color: pygame.color.Color,
    center_x: int,
    start_y: int,
    max_width: int,
    line_spacing: int = 5
) -> None:

    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip())

    y_offset = start_y
    for line in lines:
        line_render = font.render(line, True, color, background_color)
        line_rect = line_render.get_rect(center=(center_x, y_offset))
        surface.blit(line_render, line_rect)
        y_offset += font.get_height() + line_spacing


class Paddle(pygame.Rect):
    def __init__(self, x, y, width, height, speed, color):
        super().__init__(x, y, width, height)
        self.speed = speed
        self.color = color

    def move(self, direction):
        if direction == "up":
            self.y -= self.speed
        elif direction == "down":
            self.y += self.speed

        # Keep paddle within screen bounds
        if self.top < 0:
            self.top = 0
        if self.bottom > SCREEN_HEIGHT:
            self.bottom = SCREEN_HEIGHT

    def draw(self):
        pygame.draw.rect(screen, self.color, self)


class Ball(pygame.Rect):
    def __init__(self, x, y, radius, speed, color):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2)
        self.radius = radius
        self.color = color
        self.initial_speed = speed
        self.current_speed = speed
        self.dx = random.choice([-1, 1]) * self.current_speed
        self.dy = random.choice([-1, 1]) * self.current_speed

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def bounce_x(self):
        self.dx *= -1
        self.current_speed += BALL_ACCELERATION_FACTOR

        # Reapply speed
        self.dx = (1 if self.dx > 0 else -1) * self.current_speed
        self.dy = (1 if self.dy > 0 else -1) * self.current_speed

    def bounce_y(self):
        self.dy *= -1

    def reset(self, last_scored_player):
        self.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.current_speed = self.initial_speed

        if last_scored_player == 1:
            self.dx = 1 * self.current_speed  # Ball goes to player 2
        else:
            self.dx = -1 * self.current_speed  # Ball goes to player 1

        self.dy = random.choice([-1, 1]) * self.current_speed

    def draw(self):
        pygame.draw.circle(screen, self.color, self.center, self.radius)


def init_game_state():
    global player1_score, player2_score, game_active, input_active
    global input_string

    player1_score = 0
    player2_score = 0
    game_active = True
    input_active = False

    input_string = ""

    player1_paddle = Paddle(
        PADDLE_WIDTH,
        SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, PADDLE_COLOR
    )
    player2_paddle = Paddle(
        SCREEN_WIDTH - PADDLE_WIDTH * 2,
        SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, PADDLE_COLOR
    )

    ball = Ball(
        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_RADIUS, BALL_INITIAL_SPEED, BALL_COLOR
    )
    ball.reset(last_scored_player)

    return player1_paddle, player2_paddle, ball


player1_paddle, player2_paddle, ball = init_game_state()

# Fonts
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 12)
input_font = pygame.font.Font(None, 24)

clock = pygame.time.Clock()
FPS = 60

# Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if input_active:
            if event.type == pygame.KEYDOWN:
                # User is done with input
                if event.key == pygame.K_RETURN:
                    if input_active:
                        # Do something with input_string

                        input_active = False

                    # Clear input for next time
                    input_string = ""

                # User deletes last character
                elif event.key == pygame.K_BACKSPACE:
                    input_string = input_string[:-1]

                # Collect user input
                else:
                    if event.unicode.isalnum() or event.unicode == " ":
                        input_string += event.unicode

        # Game is over
        if not game_active and not input_active:
            if event.type == pygame.KEYDOWN:
                # "R" to restart the game
                if event.key == pygame.K_r:
                    player1_paddle, player2_paddle, ball = init_game_state()

                # "Q" to quit the game
                if event.key == pygame.K_q:
                    running = False

    # Player controls
    keys = pygame.key.get_pressed()
    if game_active and not input_active:
        # Player 1 controls (W, S)
        if keys[pygame.K_w]:
            player1_paddle.move("up")
        if keys[pygame.K_s]:
            player1_paddle.move("down")

        # Player 2 controls (Up Arrow, Down Arrow)
        if keys[pygame.K_UP]:
            player2_paddle.move("up")
        if keys[pygame.K_DOWN]:
            player2_paddle.move("down")

        ball.move()

        # Ball collision with top/bottom walls
        if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
            ball.bounce_y()

        # Ball collision with paddles
        if ball.colliderect(player1_paddle) or ball.colliderect(player2_paddle):
            # Check if hit on paddle's side (prevents sticking if hit from top/bottom)
            if (ball.left < player1_paddle.right and ball.right > player1_paddle.left) or \
               (ball.right > player2_paddle.left and ball.left < player2_paddle.right):
                ball.bounce_x()

            # Prevent ball getting stuck in paddle
            if ball.left < player1_paddle.right and ball.dx < 0:
                ball.left = player1_paddle.right
            elif ball.right > player2_paddle.left and ball.dx > 0:
                ball.right = player2_paddle.left

        # Scoring (ball out of bounds)
        scored = False
        if ball.left <= 0:
            player2_score += 1
            last_scored_player = 2  # Player 2 scored
            scored = True
        elif ball.right >= SCREEN_WIDTH:
            player1_score += 1
            last_scored_player = 1  # Player 1 scored
            scored = True

        if scored:
            # Check for game over first
            if player1_score >= MAX_SCORE or player2_score >= MAX_SCORE:
                game_active = False
            else:
                # Activate input after score, game still active
                input_active = True

            ball.reset(last_scored_player)

    # Clear screen
    screen.fill(BACKGROUND_COLOR)

    player1_paddle.draw()
    player2_paddle.draw()
    ball.draw()

    score_text1 = font.render(
        f"Player 1: {player1_score}", True, TEXT_COLOR)
    score_text2 = font.render(
        f"Player 2: {player2_score}", True, TEXT_COLOR)

    screen.blit(score_text1, (SCREEN_WIDTH // 4 -
                score_text1.get_width() // 2, 20))
    screen.blit(score_text2, (SCREEN_WIDTH * 3 //
                4 - score_text2.get_width() // 2, 20))

    # Input Prompt (after score or game over)
    if input_active:
        prompt_text = f"Player {last_scored_player} scored! Enter a prompt to change the game! (Press ENTER):"

        prompt_render = input_font.render(prompt_text, True, TEXT_COLOR)
        prompt_rect = prompt_render.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

        screen.blit(prompt_render, prompt_rect)

        input_display_text = input_string + "_"  # Add cursor

        render_wrapped_text(screen, input_display_text, input_font, TEXT_COLOR, TEXT_BACKGROUND,
                            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, SCREEN_WIDTH // 2)

    # Final game over message
    if not game_active and not input_active:
        if player1_score >= MAX_SCORE:
            game_over_text = font.render(
                "Player 1 Wins!", True, TEXT_COLOR)
        else:
            game_over_text = font.render(
                "Player 2 Wins!", True, TEXT_COLOR)

        restart_text = small_font.render(
            "Press 'R' to Restart or 'Q' to Quit", True, TEXT_COLOR)

        game_over_rect = game_over_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        restart_rect = restart_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))

        screen.blit(game_over_text, game_over_rect)
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
