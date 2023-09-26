import random
import pygame

class Axon:
    def __init__(self, synapses):
        self.synapses = synapses

    def step(self, membrane):
        for synapse in self.synapses:
            if membrane.spike:
                synapse.transmit()
            synapse.regenerate()

class Dendrite:
    def __init__(self, weight=10):
        self.weight = weight
        self.max_weight = 50
        self.min_weight = -50
        self.input_mediator = ""
        self.post_synapse = None
        self.last_input_state = None
        self.history_of_inputs = []

    def connect(self, synapse):
        self.post_synapse = synapse

    def set_weight(self, new_weight):
        self.weight = new_weight

    def step(self, mode="default"):
        if self.post_synapse:
            self.input_mediator = self.post_synapse.receive()

        if mode == "cycle-train":
            self.last_input_state = (self.input_mediator, self.weight)
        elif mode == "associative-train":
            self.history_of_inputs.append((self.input_mediator, self.weight))

        if self.input_mediator != "":
            self.input_mediator = ""
            return self.weight
        else:
            return 0

class Synapse:
    def __init__(self, transmitter_type='simple-signal', initial_level=100, regenerate_rate=0.5):
        self.neurotransmitter_level = initial_level 
        self.max_level = initial_level              
        self.regenerate_rate = regenerate_rate      
        self.transmitter_type = transmitter_type    
        self.received_transmitter = ""              
        self.parent_neuron = None 

    def transmit(self):
        if self.neurotransmitter_level >= 1:
            self.neurotransmitter_level -= 1    
            self.received_transmitter = self.transmitter_type   
        else:
            self.received_transmitter = ""      

    def regenerate(self):
        regenerate_amount = max(0.001, round(self.regenerate_rate * (self.max_level - self.neurotransmitter_level), 3))
        self.neurotransmitter_level += regenerate_amount 
        self.neurotransmitter_level = min(self.max_level, self.neurotransmitter_level)

    def receive(self):
        if self.received_transmitter != "":
            nt = self.received_transmitter 
            self.received_transmitter = "" 
            return nt
        else:
            return ""

class Membrane:
    def __init__(self, rest=0.0, threshold=20.0, reset_ratio=0.05, leakage=0.5):
        self.rest = rest
        self.threshold = threshold
        self.reset_ratio = reset_ratio
        self.leakage = leakage
        self.v_m = self.rest
        self.spike = False

    def reset(self):
        return self.rest + (self.reset_ratio * (self.threshold - self.rest))

    def step(self, input_value, refractory):
        if refractory:
            # If in refractory period, reset the membrane potential and set spike to False
            self.v_m = self.reset()
            self.spike = False
        else:
            # If not in refractory period, update the membrane potential
            self.v_m += input_value
            
            if self.v_m >= self.threshold:
                # If membrane potential has reached the threshold, reset the membrane potential and set spike to True
                self.v_m = self.reset()
                self.spike = True
            else:
                # If potential is below threshold, leak the membrane potential and set spike to False
                self.v_m = round(self.v_m - ((self.v_m - self.rest) / 100 * self.leakage), 6)
                self.spike = False

class Core:
    def __init__(self, dendrites, membrane, axon, refractory_period=1.0, mode="default"):
        self.dendrites = dendrites
        self.membrane = membrane
        self.axon = axon
        self.refractory_period = refractory_period
        self.refractory_time_remaining = 0  
        self.mode = mode 

    def step(self):
        # Accumulate all the dendrite signals
        total_input = sum(dendrite.step(mode=self.mode) for dendrite in self.dendrites)   
        
        # Check if the neuron is in refractory period
        refractory = self.refractory_time_remaining > 0                     
        
        # Update the membrane potential
        self.membrane.step(total_input, refractory)                         
        
        if self.membrane.spike:  
            # If the neuron spiked, enter the refractory period
            self.refractory_time_remaining = self.refractory_period         
        else:
            # Decrease the time remaining in the refractory period
            self.refractory_time_remaining = max(0, self.refractory_time_remaining - 1)  
        
        # Provide the membrane potential and spike to the axon
        self.axon.step(self.membrane)

class Neuron:
    def __init__(self, core):
        self.core = core
        self.is_training = False

    def simple_cycle_by_cycle_learning(self, error):
        if error != 0:
            for dendrite in self.core.dendrites:
                if dendrite.last_input_state and dendrite.last_input_state[0] != "":        # if input of dendrite have some transmitter (not empty string)
                    # the error is applied to the dendrite's weight
                    dendrite.weight = round(dendrite.weight + (error if self.core.membrane.spike else -error), 3)
                    # the weight is limited to the range [min_weight, max_weight]
                    dendrite.weight = max(min(dendrite.weight, dendrite.max_weight), dendrite.min_weight)

    def backward_propagate(self, error):
        self.simple_cycle_by_cycle_learning(error)
        for dendrite in self.core.dendrites:
            if dendrite.last_input_state and dendrite.last_input_state[0] != "":                # if input of dendrite have some transmitter (not empty string)
                if dendrite.post_synapse and hasattr(dendrite.post_synapse, 'parent_neuron'):   # if dendrite have post_synapse and post_synapse have parent_neuron
                    if self.core.membrane.spike:
                        dendrite.post_synapse.parent_neuron.backward_propagate(error=error + dendrite.weight)
                    else:
                        # opposite sign of error with random coefficient
                        dendrite.post_synapse.parent_neuron.backward_propagate(error=-(error + dendrite.weight * random.uniform(0.7, 1.3)))

    def cumulative_learning(self):
        pass

    def long_term_associative_learning(self):
        pass

    def step(self):
        self.core.step()

class SensorNeuron:
    def __init__(self):
        self.input_value = 0
        self.sensitivity = 0.5
        self.leak_rate = 0.1
        self.output_value = False 

    def set_input(self, value):
        self.input_value = round(self.input_value + value, 3)
        # the input value is limited to the range [0, 1]
        self.input_value = min(self.input_value, 1)

    def step(self):
        if self.input_value > self.sensitivity:
            self.output_value = True
            self.input_value = 0
        else:
            self.output_value = False
            if self.input_value > 0:
                self.input_value = round(self.input_value - self.leak_rate, 3)
                # the input value is limited to the range [0, 1]
                self.input_value = max(self.input_value, 0)

    def receive(self):
        return "simple-signal-mediator" if self.output_value else ""

class MotorNeuron:
    def __init__(self):
        self.output_value = 0
        self.post_synapses = []

    def connect(self, synapse_objects=[]):
        self.post_synapses = synapse_objects

    def step(self):
        self.output_value = 0
        for synapse in self.post_synapses:
            if synapse.receive() != "": # if synapse have some transmitter (not empty string)
                self.output_value += 1
        self.output_value = self.output_value

class Brine:
    def __init__(self, input_size, hidden_size=[4,], output_size=1):
         # Create sensor neurons
        self.sensors = [SensorNeuron() for _ in range(input_size)]

        # Define network topology
        self.topology = hidden_size

        # Initialize empty list to hold all layers of neurons
        self.layers = []
        # Create each layer
        for i, num_neurons in enumerate(self.topology):
            # Create neurons for the layer
            layer = [
                Neuron(core=Core(
                    dendrites=[Dendrite(weight=random.uniform(-20, 20))], 
                    membrane=Membrane(threshold=20.0, reset_ratio=0.0, leakage=1),
                    axon=Axon([Synapse(transmitter_type='simple-signal-mediator', initial_level=100, regenerate_rate=1)]),
                    refractory_period=0, mode='cycle-train')) for _ in range(num_neurons)
            ]
            # bind Synapse to parent Neuron
            for neuron in layer:
                neuron.core.axon.synapses[0].parent_neuron = neuron
                

            # If this is the first layer, connect the neurons to the sensors
            if i == 0:
                for j in range(num_neurons):
                    layer[j].core.dendrites[0].connect(self.sensors[j % input_size])
            # If this is not the first layer, connect the neurons to the neurons in the previous layer
            else:
                for j in range(num_neurons):
                    layer[j].core.dendrites[0].connect(self.layers[i-1][j % len(self.layers[i-1])].core.axon.synapses[0])
            # Add the layer to the list of layers
            self.layers.append(layer)

        # Create motor neurons, each connected to a neuron in the last layer
        self.motors = [MotorNeuron() for _ in range(output_size)]
        for i in range(output_size):
            self.motors[i].connect([self.layers[-1][i].core.axon.synapses[0]])

        # Training
        # for _ in range(50):
    def input(self, input_data):
        # Set input for the sensors
        for i in range(len(self.sensors)):
            self.sensors[i].set_input(input_data[i])

    def step(self):

        # Step the sensors
        for sensor in self.sensors:
            sensor.step()

        # Process the inputs with the neurons in each layer and train them
        for layer in self.layers:
            for neuron in layer:
                neuron.step()

        # Step the motors
        for motor in self.motors:
            motor.step()
        
        return [motor.output_value for motor in self.motors]

    def train(self, error):                    
        errors = []  # Calculate the appropriate errors here
        for i, neuron in enumerate(self.layers[-1]):
            # neuron.backward_propagate(errors[i])
            if neuron.core.membrane.spike:
                    neuron.backward_propagate(error = error)
            else:
                neuron.backward_propagate(error = -error)

        # more errors stimulations for all layers to fasten the training ( not sure if it is correct )
        for i in range(len(self.layers)-1, -1, -1):
            layer = self.layers[i]
            for j in range(len(layer)):
                neuron = layer[j]
                if neuron.core.membrane.spike:
                    neuron.backward_propagate(error = error)
                else:
                    neuron.backward_propagate(error = -error)

brine = Brine(input_size=(8*8)+4+8+1, hidden_size=[8,], output_size=4)
class ConnectorSnackSnn:    
    def __init__(self, width, height):
        # Set the dimensions of the field
        self.width = width
        self.height = height
        # data to/from the neural network
        self.go_to = "UP" #STOP
        self.game_state = {
            "field": [[0 for _ in range(width)] for _ in range(height)], 
            "direction": None,
            "food_direction": None,
            "food_distance": {"x": None, "y": None}
        }

    # Entity methods

    def ai_step(self):
        """
        Colled by the entity to compute the next move
        """
        data = brine.step()
        # print(data)
        if data == [1,0,0,0]:
            self.go_to = "Up"
        elif data == [0,1,0,0]:
            self.go_to = "Right"
        elif data == [0,0,1,0]:
            self.go_to = "Down"
        elif data == [0,0,0,1]:
            self.go_to = "Left"
        
        elif data == [1,1,0,0]:
            self.go_to = "UpRight"
        elif data == [0,1,1,0]:
            self.go_to = "DownRight"
        elif data == [0,0,1,1]:
            self.go_to = "DownLeft"
        elif data == [1,0,0,1]:
            self.go_to = "UpLeft"
            
        

    def train(self, error):
        """
        Colled by the entity to train the neural network
        """
        brine.train(error=error)

    def get_move_direction(self):
        """
        Colled by the entity to get the direction to move to
        """
        if self.go_to != None:
            go_to = self.go_to
            self.go_to = None
            return go_to
        else:
            return None
    
    def set_game_state(self, field, direction, food_direction, food_distance):
        """
        Colled by the entity to set the game state, which is then used by the neural network
        """
        self.game_state["field"] = field
        self.game_state["direction"] = direction
        self.game_state["food_direction"] = food_direction
        self.game_state["food_distance"] = food_distance
    
        # transfer data to snn
        data = []

        # food direction
        if self.game_state["food_direction"] == "Up":
            data = [1, 0, 0, 0]
        elif self.game_state["food_direction"] == "Right":
            data = [0, 1, 0, 0]
        elif self.game_state["food_direction"] == "Down":
            data = [0, 0, 1, 0]
        elif self.game_state["food_direction"] == "Left":
            data = [0, 0, 0, 1]
            
        elif self.game_state["food_direction"] == "UpRight":
            data = [1, 1, 0, 0]
        elif self.game_state["food_direction"] == "DownRight":
            data = [0, 1, 1, 0]
        elif self.game_state["food_direction"] == "DownLeft":
            data = [0, 0, 1, 1]
        elif self.game_state["food_direction"] == "UpLeft":
            data = [1, 0, 0, 1]
        else:
            data = [0, 0, 0, 0] # STOP
        
        # food distance sum (x+y)
        distance = self.game_state["food_distance"]["x"] + self.game_state["food_distance"]["y"]
        if distance > (self.width + self.height) * 3/4:
            data += [0, 0, 0, 1]
        elif distance > (self.width + self.height) * 1/2:
            data += [0, 0, 1, 0]
        elif distance > (self.width + self.height) * 1/4:
            data += [0, 1, 0, 0]
        else:
            data += [1, 0, 0, 0]


        # direction
        if self.game_state["direction"] == "Up":
            data += [1, 0, 0, 0]
        elif self.game_state["direction"] == "Right":
            data += [0, 1, 0, 0]
        elif self.game_state["direction"] == "Down":
            data += [0, 0, 1, 0]
        elif self.game_state["direction"] == "Left":
            data += [0, 0, 0, 1]
        else:
            data += [0, 0, 0, 0] # STOP
        
        # head in field
        for row in self.game_state["field"]:
            for cell in row:
                if cell == '3':
                    data.append(1)
                else:
                    data.append(0)
        
        # body in field
        for row in self.game_state["field"]:
            for cell in row:
                if cell == '2':
                    data.append(1)
                else:
                    data.append(0)
        
        # if next step collides with boundary
        boundary_is_next = 0
        if self.game_state["direction"] == "Up":
            # check if head ('3') is in top row
            if '3' in self.game_state["field"][0]:
                print("UP collision")
                boundary_is_next = 1
        elif self.game_state["direction"] == "Right":
            # check if head ('3') is in right column
            if '3' in [row[-1] for row in self.game_state["field"]]:
                print("RIGHT collision")
                boundary_is_next = 1
        elif self.game_state["direction"] == "Down":
            # check if head ('3') is in bottom row
            if '3' in self.game_state["field"][-1]:
                print("DOWN collision")
                boundary_is_next = 1
        elif self.game_state["direction"] == "Left":
            # check if head ('3') is in left column
            if '3' in [row[0] for row in self.game_state["field"]]:
                print("LEFT collision")
                boundary_is_next = 1
                
        data.append(boundary_is_next)        
        
        
        brine.input(tuple(data))
        
   
    
    # Neural network methods
    
    def set_move_direction(self, go_to):
        """
        Colled by the neural network to set the direction to move to
        """
        self.go_to = go_to

    def get_game_state(self):
        """
        Colled by the neural network to get the game state, which is then used to compute the next move
        """
        return self.game_state


# Set the dimensions of the game window
width = 160
height = 160

data_width = 700
data_height = 500
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
score_font = pygame.font.SysFont(None, 50)
game_data = pygame.font.SysFont(None, 20)
game_distance = pygame.font.SysFont(None, 20)
game_map = pygame.font.SysFont(None, 10)

# Define functions for displaying the snake and the score:
def our_snake(snake_block_size, snake_list):
    for x in snake_list:
        pygame.draw.rect(window, GREEN, [x[0], x[1], snake_block_size, snake_block_size])

#print meadl score of last 30 games
last_score = 0
score = 0
rekord = 0
game_count = 0

def your_score(points):
    # value = score_font.render("Score: " + str(points), True, WHITE)
    # window.blit(value, [0, 0+height])
    global score
    global last_score
    global game_count
    global rekord
    score += points
    game_count += 1
    if points > rekord:
            rekord = points
    if game_count == 50:
        score = round(score/50)
        last_score = score
        score = 0
        game_count = 0
    value = score_font.render("Medal Score by last 50 games: " + str(last_score), True, WHITE)
    window.blit(value, [0, 0+height])
    # show rekord
    value = score_font.render("Rekord: " + str(rekord), True, WHITE)
    window.blit(value, [0, 30+height])
    # show actual score
    value = score_font.render("Actual: " + str(points), True, WHITE)
    window.blit(value, [0, 60+height])

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
                connector.train(error=-5)
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
            connector.train(error=20)
        



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
