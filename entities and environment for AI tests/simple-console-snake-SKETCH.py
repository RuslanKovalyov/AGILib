"""
This is a sketch of a simple snake game.
Please note that this is only a sketch of an entity outside the environment.
There is no interface for connecting the neural network yet (API control with feedback).
"""

import pygame
import random

from pyparsing import White

# Initialize Pygame:
pygame.init()

# Set the dimensions of the game window
width = 640
height = 480

# Create the game window
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# Define the colors to be used:
BLACK = (0, 0, 0)
White = (255, 255, 255)
GREEN = (0, 255, 0)

# Set up the game variables:
snake_block_size = 10
snake_speed = 15

x_change = 0
y_change = 0

clock = pygame.time.Clock()

font_style = pygame.font.SysFont(None, 30)
score_font = pygame.font.SysFont(None, 50)

# Define functions for displaying the snake and the score:
def our_snake(snake_block_size, snake_list):
    for x in snake_list:
        pygame.draw.rect(window, GREEN, [x[0], x[1], snake_block_size, snake_block_size])

def your_score(score):
    value = score_font.render("Your Score: " + str(score), True, White)
    window.blit(value, [0, 0])

# Implement the game loop:
def game_loop():
    game_over = False
    game_end = False

    # Initial position of the snake
    x1 = width / 2
    y1 = height / 2

    # Change in position
    x1_change = 0
    y1_change = 0

    # Snake body
    snake_list = []
    length_of_snake = 1

    # Generate initial food position
    foodx = round(random.randrange(0, width - snake_block_size) / 10.0) * 10.0
    foody = round(random.randrange(0, height - snake_block_size) / 10.0) * 10.0

    while not game_over:
        while game_end:
            # Display game over message
            window.fill(BLACK)
            message = font_style.render("Game Over! Press Q-Quit or C-Play Again", True, GREEN)
            window.blit(message, [width / 6, height / 3])
            your_score(length_of_snake - 1)
            pygame.display.update()

            # Check for keypresses after the game ends
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_end = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_end = False
                    if event.key == pygame.K_c:
                        game_loop()

        # Handle keypresses
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block_size
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block_size
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block_size
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block_size
                    x1_change = 0

        # Check if the snake hits the boundary
        if x1 >= width or x1 < 0 or y1 >= height or y1 < 0:
            game_end = True

        # Update the snake's position
        x1 += x1_change
        y1 += y1_change

        window.fill(BLACK)
        pygame.draw.rect(window, GREEN, [foodx, foody, snake_block_size, snake_block_size])
        snake_head = []
        snake_head.append(x1)
        snake_head.append(y1)
        snake_list.append(snake_head)

        # Remove the extra segments of the snake if it gets longer
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Check if the snake hits itself
        for x in snake_list[:-1]:
            if x == snake_head:
                game_end = True

        # Update the snake and food display
        our_snake(snake_block_size, snake_list)
        your_score(length_of_snake - 1)

        pygame.display.update()

        # Check if the snake eats the food
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, width - snake_block_size) / 10.0) * 10.0
            foody = round(random.randrange(0, height - snake_block_size) / 10.0) * 10.0
            length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()


# Start the game
game_loop()
