import os
import ai

brine = ai.Brine(input_size=(8*8)+4+8+1, hidden_size=[80,], output_size=4)
print(len(brine.sensors))
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
