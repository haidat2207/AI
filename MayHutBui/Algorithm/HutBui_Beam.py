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

def calculate_cost(state):
    return sum(row.count(1) for row in state)

def state_to_tuple(state):
    return tuple(tuple(row) for row in state)

def Beam(initial_state, goal_state, x, y, beam_width):
    state = copy_node(initial_state)

    if state[x][y] == 1:
        state[x][y] = 0

    root = Node(state, x, y, action=None, cost=calculate_cost(state))

    frontier = [root]

    while frontier:

        next_frontier = []  

        for current_node in frontier:
            if current_node.state == goal_state:
                return current_node

            children = move(
                current_node.state,
                current_node.x,
                current_node.y
            )

            for neighbor, action, new_x, new_y in children:
                neighbor_cost = calculate_cost(neighbor)
                child_node = Node(neighbor, new_x, new_y, parent=current_node, action=action, cost=neighbor_cost)
                next_frontier.append(child_node)

        
        next_frontier.sort(key=lambda node: node.cost)

        if not next_frontier:
            break

        frontier = next_frontier[:beam_width]

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
# beam_width = int(input("Nhập số phần tử tối đa: "))
# result = Beam(initial_state, goal_state, x, y, beam_width)

# if result.state == goal_state:
#     print("Đã tìm thấy giải pháp.")
#     print_result(result)
# else:
#     print("Đã đạt giá trị cục bộ.")
#     print_result(result)