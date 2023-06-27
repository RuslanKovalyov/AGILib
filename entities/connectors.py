import os
import ai

brine = ai.Brine(input_size=4, hidden_size=[36,], output_size=4)

class ConnectorSnackSnn:    
    def __init__(self, width, height):
        # Set the dimensions of the field
        self.width = width
        self.height = height
        # data to/from the neural network
        self.go_to = "STOP"
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
        if self.game_state["food_direction"] == "Up":
            brine.input(tuple([1, 0, 0, 0]))
        elif self.game_state["food_direction"] == "Right":
            brine.input(tuple([0, 1, 0, 0]))
        elif self.game_state["food_direction"] == "Down":
            brine.input(tuple([0, 0, 1, 0]))
        elif self.game_state["food_direction"] == "Left":
            brine.input(tuple([0, 0, 0, 1]))
            
        elif self.game_state["food_direction"] == "UpRight":
            brine.input(tuple([1, 1, 0, 0]))
        elif self.game_state["food_direction"] == "DownRight":
            brine.input(tuple([0, 1, 1, 0]))
        elif self.game_state["food_direction"] == "DownLeft":
            brine.input(tuple([0, 0, 1, 1]))
        elif self.game_state["food_direction"] == "UpLeft":
            brine.input(tuple([1, 0, 0, 1]))
    
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
