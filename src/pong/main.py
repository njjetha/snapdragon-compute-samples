# -----------------------------------------------------------------------------
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause
#
# -----------------------------------------------------------------------------


import pygame
from game_config import GameConfig
from model_inference import generate_game_config
from time import sleep
from enum import Enum, auto
from typing import Tuple
import sys
import random


game_config: GameConfig = GameConfig({
    "paddle_width": 15,
    "paddle_height": 100,
    "ball_radius": 10,
    "background_color": {
        "red": 255,
        "green": 255,
        "blue": 255,
    },
    "ball_color": {
        "red": 231,
        "green": 19,
        "blue": 36,
    },
    "paddle_color": {
        "red": 53,
        "green": 0,
        "blue": 172,
    },
    "text_color": {
        "red": 0,
        "green": 0,
        "blue": 0,
    },
    "text_background_color": {
        "red": 245,
        "green": 246,
        "blue": 247,
    },
    "paddle_speed": 7.0,
    "ball_initial_speed": 5.0,
    "ball_acceleration_factor": 0.1,
})


SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600

FPS: int = 60

MAX_SCORE: int = 5
last_scored_player: int = 1

MAX_COUNTDOWN: int = 3
current_countdown: int = MAX_COUNTDOWN
countdown_active: bool = True  # The first round starts with a countdown

running: bool = True


pygame.init()

screen: pygame.surface.Surface = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("LLM Pong!")


# Fonts
large_font: pygame.font.Font = pygame.font.Font(None, 74)
small_font: pygame.font.Font = pygame.font.Font(None, 18)
normal_font: pygame.font.Font = pygame.font.Font(None, 24)

clock: pygame.time.Clock = pygame.time.Clock()


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

    words: list[str] = text.split(' ')
    lines: list[str] = []
    current_line: str = ""

    for word in words:
        test_line: str = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip())

    y_offset: int = start_y
    for line in lines:
        line_render: pygame.surface.Surface = font.render(
            line, True, color, background_color)
        line_rect: pygame.Rect = line_render.get_rect(
            center=(center_x, y_offset))
        surface.blit(line_render, line_rect)
        y_offset += font.get_height() + line_spacing


class Direction(Enum):
    Up = auto()
    Down = auto()


class Paddle(pygame.Rect):
    def __init__(self, x: float, y: float, width: float, height: float, speed: float, color: pygame.color.Color) -> None:
        super().__init__(x, y, width, height)

        self.speed = speed
        self.color = color

    def move(self, direction: Direction) -> None:
        if direction == Direction.Up:
            self.y -= self.speed
        elif direction == Direction.Down:
            self.y += self.speed

        # Keep paddle within screen bounds
        if self.top < 0:
            self.top = 0
        if self.bottom > SCREEN_HEIGHT:
            self.bottom = SCREEN_HEIGHT

    def draw(self) -> None:
        pygame.draw.rect(screen, self.color, self)


class Ball(pygame.Rect):
    def __init__(self, x: float, y: float, radius: float, speed: float, color: pygame.color.Color) -> None:
        super().__init__(x - radius, y - radius, radius * 2, radius * 2)

        self.radius = radius
        self.color = color
        self.initial_speed = speed
        self.current_speed = speed
        self.dx = random.choice([-1, 1]) * self.current_speed
        self.dy = random.choice([-1, 1]) * self.current_speed

    def move(self) -> None:
        self.x += self.dx
        self.y += self.dy

    def bounce_x(self) -> None:
        self.dx *= -1
        self.current_speed += game_config.ball_acceleration_factor

        # Reapply speed
        self.dx = (1 if self.dx > 0 else -1) * self.current_speed
        self.dy = (1 if self.dy > 0 else -1) * self.current_speed

    def bounce_y(self) -> None:
        self.dy *= -1

    def reset(self, last_scored_player: int) -> None:
        assert last_scored_player in [
            1, 2], f"last_scored_player has to be either 1 or 2 but was {last_scored_player}"

        self.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.current_speed = self.initial_speed

        if last_scored_player == 1:
            self.dx = 1 * self.current_speed  # Ball goes to player 2
        else:
            self.dx = -1 * self.current_speed  # Ball goes to player 1

        self.dy = random.choice([-1, 1]) * self.current_speed

    def draw(self) -> None:
        pygame.draw.circle(screen, self.color, self.center, self.radius)


def show_start_screen() -> None:
    global running

    waiting_for_start: bool = True
    while waiting_for_start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting_for_start = False

        screen.fill(game_config.background_color)

        # Title
        title_text = large_font.render(
            "Prompt Pong!", True, game_config.text_color)
        title_rect = title_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(title_text, title_rect)

        # Instructions
        start_instruction_text = normal_font.render(
            "Press any key to start", True, game_config.text_color)
        start_instruction_rect = start_instruction_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(start_instruction_text, start_instruction_rect)

        credit_text = small_font.render(
            "Powered by Snapdragon X Elite", True, game_config.text_color)
        credit_rect = credit_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(credit_text, credit_rect)

        pygame.display.flip()
        clock.tick(FPS)


def init_game_state(reset_score: bool = False) -> Tuple[Paddle, Paddle, Ball]:
    global player1_score, player2_score, game_active, input_active, countdown_active, input_string

    if reset_score:
        player1_score = 0
        player2_score = 0

    game_active = True
    input_active = False

    input_string = ""

    player1_paddle = Paddle(
        game_config.paddle_width,
        SCREEN_HEIGHT // 2 - game_config.paddle_height // 2,
        game_config.paddle_width, game_config.paddle_height, game_config.paddle_speed, game_config.paddle_color
    )
    player2_paddle = Paddle(
        SCREEN_WIDTH - game_config.paddle_width * 2,
        SCREEN_HEIGHT // 2 - game_config.paddle_height // 2,
        game_config.paddle_width, game_config.paddle_height, game_config.paddle_speed, game_config.paddle_color
    )

    ball = Ball(
        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, game_config.ball_radius, game_config.ball_initial_speed, game_config.ball_color
    )
    ball.reset(last_scored_player)

    return player1_paddle, player2_paddle, ball


show_start_screen()

# Initial object setup
player1_paddle, player2_paddle, ball = init_game_state(True)

# Main game Loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if input_active:
            if event.type == pygame.KEYDOWN:
                # User is done with input
                if event.key == pygame.K_RETURN:
                    if input_active:
                        model_loading_render = normal_font.render(
                            "The on-device model is generating your game!", True, game_config.text_color)
                        model_loading_rect = model_loading_render.get_rect(
                            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))

                        screen.blit(model_loading_render, model_loading_rect)
                        pygame.display.flip()

                        game_config = generate_game_config(
                            input_string, game_config)

                        player1_paddle, player2_paddle, ball = init_game_state()

                        countdown_active = True
                        input_active = False

                    # Clear input for next time
                    input_string = ""

                # User deletes last character
                elif event.key == pygame.K_BACKSPACE:
                    input_string = input_string[:-1]

                # Collect user input
                else:
                    input_string += event.unicode

        # Game is over
        if not game_active and not input_active:
            if event.type == pygame.KEYDOWN:
                # "R" to restart the game
                if event.key == pygame.K_r:
                    player1_paddle, player2_paddle, ball = init_game_state(
                        True)

                # "Q" to quit the game
                if event.key == pygame.K_q:
                    running = False

    # Player controls
    keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
    if game_active and not input_active and not countdown_active:
        # Player 1 controls (W, S)
        if keys[pygame.K_w]:
            player1_paddle.move(Direction.Up)
        if keys[pygame.K_s]:
            player1_paddle.move(Direction.Down)

        # Player 2 controls (Up Arrow, Down Arrow)
        if keys[pygame.K_UP]:
            player2_paddle.move(Direction.Up)
        if keys[pygame.K_DOWN]:
            player2_paddle.move(Direction.Down)

        ball.move()

        # Ball collision with top/bottom walls
        if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
            ball.bounce_y()

        # Ball collision with paddles
        if ball.colliderect(player1_paddle) or ball.colliderect(player2_paddle):
            # Check if hit on paddle's side (prevents sticking if hit from top/bottom)
            if (ball.left < player1_paddle.right and ball.right > player1_paddle.left) or (ball.right > player2_paddle.left and ball.left < player2_paddle.right):
                ball.bounce_x()

            # Prevent ball getting stuck in paddle
            if ball.left < player1_paddle.right and ball.dx < 0:
                ball.left = player1_paddle.right
            elif ball.right > player2_paddle.left and ball.dx > 0:
                ball.right = player2_paddle.left

        # Scoring (ball out of bounds)
        scored: bool = False
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

    # Clear screen
    screen.fill(game_config.background_color)

    player1_paddle.draw()
    player2_paddle.draw()
    ball.draw()

    score_text1 = large_font.render(
        f"Player 1: {player1_score}", True, game_config.text_color)
    score_text2 = large_font.render(
        f"Player 2: {player2_score}", True, game_config.text_color)

    screen.blit(score_text1, (SCREEN_WIDTH // 4 -
                score_text1.get_width() // 2, 20))
    screen.blit(score_text2, (SCREEN_WIDTH * 3 //
                4 - score_text2.get_width() // 2, 20))

    # Input Prompt (after score or game over)
    if input_active:
        prompt_text: str = f"Player {last_scored_player} scored! Enter a prompt to change the game! (Press ENTER):"

        prompt_render = normal_font.render(
            prompt_text, True, game_config.text_color)
        prompt_rect = prompt_render.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

        screen.blit(prompt_render, prompt_rect)

        input_display_text = input_string + "_"  # Add cursor

        render_wrapped_text(screen, input_display_text, normal_font, game_config.text_color, game_config.text_background_color,
                            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, SCREEN_WIDTH // 2)

    # Countdown screen before a round begins
    if countdown_active:
        countdown_render = normal_font.render(
            f"Round starting in {current_countdown}...", True, game_config.text_color)
        countdown_rect = countdown_render.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))

        ball_direction_render = large_font.render(
            "->" if last_scored_player == 1 else "<-", True, game_config.text_color)
        ball_direction_rect = ball_direction_render.get_rect(
            center=(SCREEN_WIDTH // 2 + (40 if last_scored_player ==
                    1 else -40), SCREEN_HEIGHT // 2 - 2))

        screen.blit(countdown_render, countdown_rect)
        screen.blit(ball_direction_render, ball_direction_rect)

        current_countdown -= 1

    # Final game over message
    if not game_active and not input_active and not countdown_active:
        if player1_score >= MAX_SCORE:
            game_over_text = large_font.render(
                "Player 1 Wins!", True, game_config.text_color)
        else:
            game_over_text = large_font.render(
                "Player 2 Wins!", True, game_config.text_color)

        restart_text = small_font.render(
            "Press 'R' to Restart or 'Q' to Quit", True, game_config.text_color)

        game_over_rect = game_over_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        restart_rect = restart_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))

        screen.blit(game_over_text, game_over_rect)
        screen.blit(restart_text, restart_rect)

    # Re-render the game!
    pygame.display.flip()
    clock.tick(FPS)

    # Add a delay between countdown messages
    if countdown_active:
        sleep(1)

        # Stop countdown
        if current_countdown <= 0:
            current_countdown = MAX_COUNTDOWN
            countdown_active = False

pygame.quit()
sys.exit()
