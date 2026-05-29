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

def SteppestHill(initial_state, goal_state, x, y):
    if initial_state[x][y] == 1:
        initial_state[x][y] = 0

    root = Node(initial_state, x, y, action=None, cost=calculate_cost(initial_state))

    current_node = root
    parent_node = None

    while True:

        if current_node.state == goal_state:
            return current_node

        moves = move(current_node.state, current_node.x, current_node.y)

        parent_node = current_node.state

        child = []

        for neighbor, action, new_x, new_y in moves:
            neighbor_cost = calculate_cost(neighbor)
            if neighbor_cost < current_node.cost:
                child_node = Node(neighbor, new_x, new_y, parent=current_node, action=action, cost=neighbor_cost)
                child.append(child_node)

        if not child:
            break

        best_cost = min(node.cost for node in child)
        best_child = [node for node in child if node.cost == best_cost]
        current_node = random.choice(best_child)

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
# result = SteppestHill(initial_state, goal_state, x, y)

# if result == goal_state:
#     print_result(result)
#     print("Đã tìm thấy giải pháp.")
# else:
#     print_result(result)
#     print("Đã đạt giá trị cục bộ.")