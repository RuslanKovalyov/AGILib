import random
import pygame
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# Initialize pygame
pygame.init()

# Constants
BOARD_SIZE = 6
LR = 0.010
GAMMA = 0.95
EPISODES = 100_000
EPSILON = 1
EPSILON_DECAY = 0.995
EPSILON_MIN = 0.01
BATCH_SIZE = 64
window_delay = 0

# Neural Network Model
class DQN(nn.Module):
    def __init__(self):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(BOARD_SIZE * BOARD_SIZE, 2400)
        self.fc2 = nn.Linear(2400, 2400)
        self.fc3 = nn.Linear(2400, 240)
        self.fc4 = nn.Linear(240, 4)  # 4 actions

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        return self.fc4(x)

# DQNAgent with a target network
class DQNAgent:
    def __init__(self, model_class, lr):
        self.model = model_class().to(device)
        self.target_model = model_class().to(device)
        self.target_model.load_state_dict(self.model.state_dict())
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()

    def update(self, states, actions, rewards, next_states, dones):
        target = rewards + GAMMA * torch.max(self.target_model(next_states), dim=1)[0] * (1 - dones)
        current = self.model(states).gather(1, actions.unsqueeze(-1)).squeeze(-1)
        loss = self.loss_fn(current, target.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def sync(self):
        self.target_model.load_state_dict(self.model.state_dict())

# Snake Game with Visualization
class SnakeGame:
    def __init__(self):
        self.win_width = 400
        self.win_height = self.win_width
        self.block_size = self.win_width/BOARD_SIZE
        self.win = pygame.display.set_mode((self.win_width, self.win_height))
        pygame.display.set_caption("Snake SNN with PyTorch")

    def _get_state(self):
        state = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        for segment in self.snake:
            state[segment[0]][segment[1]] = 1
        state[self.food[0]][self.food[1]] = 2
        return state.flatten()

    def reset(self):
        self.snake = [[5, 5], [5, 4], [5, 3]]
        self.food = [random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)]
        self.score = 0
        self.done = False
        return self._get_state()

    def step(self, action):
        x, y = self.snake[-1].copy()
        if action == 0:   x -= 1
        elif action == 1: x += 1
        elif action == 2: y -= 1
        elif action == 3: y += 1
        if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE:
            self.done = True
            return self._get_state(), -10, self.done
        self.snake.append([x, y])
        if self.snake[-1] == self.food:
            self.score += 1
            reward = 10
            self.food = [random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)]
        else:
            self.snake = self.snake[1:]
            reward = -0.1
        if self.snake[-1] in self.snake[:-1]:
            self.done = True
            reward = -10
        self._render()
        return self._get_state(), reward, self.done

    def _render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
                self.close()
                return
        self.win.fill((255, 255, 255))
        for segment in self.snake:
            pygame.draw.rect(self.win, (0, 255, 0), (segment[1] * self.block_size, segment[0] * self.block_size, self.block_size, self.block_size))
        pygame.draw.rect(self.win, (255, 0, 0), (self.food[1] * self.block_size, self.food[0] * self.block_size, self.block_size, self.block_size))
        pygame.display.flip()
        pygame.time.delay(window_delay)

    def close(self):
        pygame.quit()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
agent = DQNAgent(DQN, LR)
memory = []
env = SnakeGame()

for episode in range(EPISODES):
    state = env.reset()
    state = torch.tensor(state, device=device, dtype=torch.float32)
    done = False

    # Check for key presses to adjust the delay
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                window_delay += 1
                print(f"Delay increased to: {window_delay}")

            elif event.key == pygame.K_DOWN:
                window_delay = max(0, window_delay - 1)
                print(f"Delay decreased to: {window_delay}")

    while not done:
        if random.random() < EPSILON:
            action = random.randint(0, 3)
        else:
            with torch.no_grad():
                action = torch.argmax(agent.model(state)).item()
        next_state, reward, done = env.step(action)
        next_state = torch.tensor(next_state, device=device, dtype=torch.float32)
        memory.append((state, action, reward, next_state, done))
        state = next_state

        if len(memory) > BATCH_SIZE:
            batch = random.sample(memory, BATCH_SIZE)
            states, actions, rewards, next_states, dones = zip(*batch)
            states = torch.stack(states)
            actions = torch.tensor(actions, device=device)
            rewards = torch.tensor(rewards, device=device, dtype=torch.float32)
            next_states = torch.stack(next_states)
            dones = torch.tensor(dones, device=device, dtype=torch.float32)
            agent.update(states, actions, rewards, next_states, dones)

    if EPSILON > EPSILON_MIN:
        EPSILON *= EPSILON_DECAY

    if episode % 10 == 0:
        agent.sync()
    
    print(f"Episode: {episode}, Score: {env.score}, Epsilon: {EPSILON:.2f}, Window_delay: {window_delay}")

