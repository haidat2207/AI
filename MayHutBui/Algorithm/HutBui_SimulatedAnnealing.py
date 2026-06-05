from math import exp
import random

class Node:
    def __init__(self, state, x, y, parent=None, action=None, cost=0):
        self.state = state
        self.x = x
        self.y = y
        self.parent = parent
        self.action = action
        self.cost = cost

def copy_node(node):

    return [row[:] for row in node]

def possible_move(x, y, n, m):

    moves = []

    if x > 0:
        moves.append((-1, 0, "UP"))

    if x < n - 1:
        moves.append((1, 0, "DOWN"))

    if y > 0:
        moves.append((0, -1, "LEFT"))

    if y < m - 1:
        moves.append((0, 1, "RIGHT"))

    return moves


def move(node, x, y):

    neighbors = []

    i, j = x, y

    for di, dj, action in possible_move(x, y, len(node), len(node[0])):

        new_i = i + di
        new_j = j + dj

        new_node = copy_node(node)

        if new_node[new_i][new_j] == 1:
            new_node[new_i][new_j] = 0

        neighbors.append((new_node, action, new_i, new_j))

    return neighbors

def calculate_cost(state, x, y):
    min_distance = float('inf')

    for i in range(len(state)):
        for j in range(len(state[0])):
            if state[i][j] == 1:
                distance = abs(x - i) + abs(y - j)
                min_distance = min(min_distance, distance)

    if min_distance == float('inf'):
        return 0

    return min_distance

def SimulatedAnnealing(initial_state, goal_state, x, y, T=100, cooling_rate=0.99, T_min=0.1):
    if initial_state[x][y] == 1:
        initial_state[x][y] = 0

    root = Node(initial_state, x, y, action=None, cost=calculate_cost(initial_state, x, y))

    current_node = root
    
    while T > T_min:

        if current_node.state == goal_state:
            return current_node

        moves = move(current_node.state, current_node.x, current_node.y)

        child = []

        for neighbor, action, new_x, new_y in moves:
            neighbor_cost = calculate_cost(neighbor, new_x, new_y)
            child_node = Node(neighbor, new_x, new_y, parent=current_node, action=action, cost=neighbor_cost)
            child.append(child_node)

        next_node = random.choice(child)
        delta_cost = next_node.cost - current_node.cost
        if delta_cost < 0:
            current_node = next_node
        else:
            p = exp(-delta_cost / T)
            probability = random.random()
            if probability < p:
                current_node = next_node

        T *= cooling_rate

    return current_node
        
def print_room(state):
    for row in state:
        print(row)

def print_result(node):

    path = []

    while node:

        path.append((node.action, node.state,node.x, node.y, node.cost))
        node = node.parent

    path.reverse()

    step = 0

    for action, state, x, y, cost in path:
        print(f"Bước: {step}")
        step += 1
        print(f"Action: {action}")
        print(f"Vị trí máy hút bụi hiện tại: {(x, y)}")
        print("Trạng thái hiện tại của phòng:")
        print_room(state)
        print(f"Chi phí: {cost}")
        print("-" * 30)
        print()

def get_path(node):

    path = []

    while node:

        path.append({
            "action": node.action,
            "state": node.state,
            "x": node.x,
            "y": node.y,
            "cost": node.cost
        })

        node = node.parent

    path.reverse()

    return path


# n = int(input("Nhập số dòng: "))
# m = int(input("Nhập số cột: "))

# goal_state = [[0] * m for _ in range(n)]

# initial_state = []
# for i in range(n):
#     row = list(map(int, input().split()))
#     initial_state.append(row)
# x = random.randint(0, n - 1)
# y = random.randint(0, m - 1)
# T = int(input("Nhập nhiệt độ ban đầu: "))
# cooling_rate = float(input("Nhập hệ số làm mát (0 < cooling_rate < 1): "))
# T_min = float(input("Nhập nhiệt độ tối thiểu: "))
# result = SimulatedAnnealing(initial_state, goal_state, x, y,T,cooling_rate,T_min)

# if result.state == goal_state:
#     print_result(result)
#     print("Đã tìm thấy giải pháp.")
# else:
#     print_result(result)
#     print("Đã đạt giá trị cục bộ.")