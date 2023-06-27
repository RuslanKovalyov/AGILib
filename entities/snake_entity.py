import pygame
import random

# Import the connector (to connect snake to the SNN)
from connectors import ConnectorSnackSnn


# Set the dimensions of the game window
width = 300
height = 300

data_width = 800
data_height = 800
# Define the colors to be used:
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED   = (255, 0, 0)

# connect the snake to the SNN
connector = ConnectorSnackSnn(width, height)

# Initialize Pygame:
pygame.init()

# Create the game window
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# Create the data window
data_window = pygame.display.set_mode((data_width, data_height))
pygame.display.set_caption("Data Window")

# Set up the game variables:
snake_block_size = 10
snake_speed = 15

x_change = 0
y_change = 0

clock = pygame.time.Clock()

font_style = pygame.font.SysFont(None, 30)
score_font = pygame.font.SysFont(None, 30)
game_data = pygame.font.SysFont(None, 20)
game_distance = pygame.font.SysFont(None, 20)
game_map = pygame.font.SysFont(None, 10)

# Define functions for displaying the snake and the score:
def our_snake(snake_block_size, snake_list):
    for x in snake_list:
        pygame.draw.rect(window, GREEN, [x[0], x[1], snake_block_size, snake_block_size])

def your_score(points):
    value = score_font.render("Score: " + str(points), True, WHITE)
    window.blit(value, [0, 0+height])

def render_data(game_state):
    data_window.blit(game_data.render("direction: " + str(game_state["direction"]) + ' | ' +
                                 "food_direction: " + str(game_state["food_direction"]) + ' | ', True, WHITE),
                [30, 30+height])
def render_distance(game_state):
    data_window.blit(game_distance.render("food_distance: " + str(game_state["food_distance"]), True, WHITE),
                [30, 50+height])
def render_map(game_state):
    field = game_state["field"]
    for i, row in enumerate(field):
        row_str = ''.join(str(cell) for cell in row)
        data_window.blit(game_map.render(row_str, True, WHITE), [0, height+70 + 10 * i])


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

    # Initialize snake_head
    snake_head = []

    points = 0
    distance_to_food = abs(foodx - x1) + abs(foody - y1)
    while not game_over:
        while game_end:
            # # Display game over message
            # window.fill(BLACK)
            # message = font_style.render("Game Over! Press Q-Quit or C-Play Again", True, GREEN)
            # window.blit(message, [width / 6, height / 3])
            # your_score(length_of_snake - 1)
            # pygame.display.update()

            # # Check for keypresses after the game ends
            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         game_over = True
            #         game_end = False
            #     if event.type == pygame.KEYDOWN:
            #         if event.key == pygame.K_q:
            #             game_over = True
            #             game_end = False
            #         if event.key == pygame.K_c:
            #             game_loop()

            # Reset game variables
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
            points = 0

            # Generate initial food position
            foodx = round(random.randrange(0, width - snake_block_size) / 10.0) * 10.0
            foody = round(random.randrange(0, height - snake_block_size) / 10.0) * 10.0

            # Initialize snake_head
            snake_head = []

        # Handle connector input events
        connector.ai_step()
        go_to = connector.get_move_direction()
        if go_to:
            if go_to == 'Left':
                x1_change = -snake_block_size
                y1_change = 0
            elif go_to == 'Right':
                x1_change = snake_block_size
                y1_change = 0
            elif go_to == 'Up':
                y1_change = -snake_block_size
                x1_change = 0
            elif go_to == 'Down':
                y1_change = snake_block_size
                x1_change = 0
            
            elif go_to == 'UpRight':
                y1_change = -snake_block_size
                x1_change = snake_block_size
            elif go_to == 'DownRight':
                y1_change = snake_block_size
                x1_change = snake_block_size
            elif go_to == 'DownLeft':
                y1_change = snake_block_size
                x1_change = -snake_block_size
            elif go_to == 'UpLeft':
                y1_change = -snake_block_size
                x1_change = -snake_block_size
                
        else:
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
            connector.train(error=-0.01)
            game_end = True

        # Update the snake's position
        x1 += x1_change
        y1 += y1_change

        window.fill(BLACK)

        # Draw border for game area
        pygame.draw.rect(window, WHITE, pygame.Rect(0, 0, width, height), 2) # 2 is border thickness
        
        pygame.draw.rect(window, RED, [foodx, foody, snake_block_size, snake_block_size])
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
                connector.train(error=-0.01)
                game_end = True

        # Update the snake and food display
        our_snake(snake_block_size, snake_list)
        your_score(points)
        # pygame.display.update()

        # Check if the snake eats the food
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, width - snake_block_size) / 10.0) * 10.0
            foody = round(random.randrange(0, height - snake_block_size) / 10.0) * 10.0
            length_of_snake += 1
            points += 1
            connector.train(error=5)
        



        #check if snake is moving further away from food
        if distance_to_food < abs(foodx - x1) + abs(foody - y1):
            connector.train(error=-0.01)
            # print("snake is moving further away from food")
        elif distance_to_food > abs(foodx - x1) + abs(foody - y1):
            connector.train(error=0.001)
            # print("snake is moving closer to food")
            
        distance_to_food = abs(foodx - x1) + abs(foody - y1)

        
        # Set game state
        field = [[' ' for _ in range(width)] for _ in range(height)]
        field[int(foody / snake_block_size)][int(foodx / snake_block_size)] = 1  # food
        for i, (x, y) in enumerate(snake_list):
            if i == len(snake_list) - 1:  # this is the head of the snake
                field[int(y / snake_block_size)][int(x / snake_block_size)] = '3'  # snake head
            else:
                field[int(y / snake_block_size)][int(x / snake_block_size)] = '2'  # snake body
        direction = {(-snake_block_size, 0): 'Left', (snake_block_size, 0): 'Right', (0, -snake_block_size): 'Up', (0, snake_block_size): 'Down'}.get((x1_change, y1_change), None)
        food_direction = ('Up' if snake_head[1] > foody else 'Down' if snake_head[1] < foody else '') + \
                 ('Left' if snake_head[0] > foodx else 'Right' if snake_head[0] < foodx else '')
        food_distance = {"x": abs(foodx - x1), "y": abs(foody - y1)}


        # # draw the data
        # render_data(connector.get_game_state())
        # render_distance(connector.get_game_state())
        # render_map(connector.get_game_state())

        clock.tick(snake_speed)
        pygame.display.update()
        connector.set_game_state(field, direction, food_direction, food_distance)

    pygame.quit()
    quit()


# Start the game
game_loop()
