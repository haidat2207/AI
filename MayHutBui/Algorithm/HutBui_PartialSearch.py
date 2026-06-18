import random
import heapq

class Node:
    def __init__(self, state, node_parent=None, action=None, cost=0, g=0):
        self.state = state
        self.parent = node_parent
        self.action = action
        self.cost = cost
        self.g = g

    def __lt__(self, other):
        return self.cost < other.cost
    
def to_tuple(state):
    return tuple(tuple(row) for row in state)

def to_list(state_tuple):
    return [list(row) for row in state_tuple]


MOVES = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1)
}

def clean_cell(state,x,y):
    room = to_list(state)
    
    if room[x][y] == 1:
        room[x][y] = 0
    
    return to_tuple(room)

def normalize_belief(possibilities):
    return tuple(possibilities)

def make_initial_possibility(room, x, y):
    room = to_tuple(room)
    room = clean_cell(room, x, y)
    return (room, x, y)

def apply_action_to_one_state(room, x, y, action, n, m):
    dx, dy = MOVES[action]

    nx = x + dx
    ny = y + dy

    if not (0 <= nx < n and 0 <= ny < m):
        nx, ny = x, y

    new_room = clean_cell(room, nx, ny)

    return (new_room, nx, ny)

def move_belief_state(belief_state, action, n, m):
    new_possibilities = []

    for room, x, y in belief_state:
        new_possibility = apply_action_to_one_state(room, x, y, action, n, m)
        new_possibilities.append(new_possibility)

    return normalize_belief(new_possibilities)

def calculate_cost(state):
    return sum(row.count(1) for row in state)

def heuristic_belief(belief_state):
    return max(calculate_cost(room) for room, x, y in belief_state)

def is_goal_belief(belief_state, goal_state):
    for room, x, y in belief_state:
        if room != goal_state:
            return False

    return True

def make_random_matrix(n, m):
    matrix = []

    for i in range(n):
        row = []

        for j in range(m):
            row.append(random.randint(0, 1))

        matrix.append(row)

    return matrix


def build_partial_belief(n, m, robot_x, robot_y, estimate_count):
    belief = []

    if estimate_count < 1:
        estimate_count = 1

    # Tạo ma trận thật giả định
    real_matrix = make_random_matrix(n, m)

    for i in range(estimate_count):
        random_matrix = make_random_matrix(n, m)

        # Partial Search: nhìn thấy 1 phần nên cho một vài ô giống ma trận thật
        known_count = max(1, (n * m) // 3)

        all_positions = []

        for r in range(n):
            for c in range(m):
                all_positions.append((r, c))

        known_positions = random.sample(all_positions, known_count)

        for r, c in known_positions:
            random_matrix[r][c] = real_matrix[r][c]

        belief.append(
            make_initial_possibility(
                random_matrix,
                robot_x,
                robot_y
            )
        )

    return belief

def PartialSearch(initial_belief, goal_state, n, m):

    initial_copy = normalize_belief(initial_belief)
    goal_state = to_tuple(goal_state)
        
    root = Node(initial_copy, node_parent=None, action=None, cost=heuristic_belief(initial_copy))
    frontier = []
    counter = 0
    heapq.heappush(frontier, (root.cost, counter, root))

    best_cost = {root.state: root.g}

    while frontier:

        current_cost, _, current_node = heapq.heappop(frontier)

        if current_node.g > best_cost.get(current_node.state, float('inf')):
            continue

        if is_goal_belief(current_node.state, goal_state):
            return current_node

        for action in MOVES:
            new_belief = move_belief_state(
                current_node.state,
                action,
                n,
                m
            )

            new_g = current_node.g + calculate_cost(new_belief[0][0])
            new_h = heuristic_belief(new_belief)
            new_f = new_g + new_h

            if new_g < best_cost.get(new_belief, float('inf')):
                best_cost[new_belief] = new_g

                child = Node(new_belief, node_parent=current_node, action=action, cost=new_f, g=new_g)
                counter += 1
                heapq.heappush(frontier, (child.cost, counter, child))
    return None

def print_room(state):
    for row in state:
        print(row)

def print_result(node):

    path = []

    while node:
        path.append(node)
        node = node.parent

    path.reverse()

    step = 0

    for node in path:
        print(f"Bước: {step}")
        step += 1

        print(f"Action: {node.action}")
        print(f"g = {node.g}")
        print(f"f = {node.cost}")
        print("Belief state hiện tại:")

        for index, (room, x, y) in enumerate(node.state, start=1):
            print(f"Khả năng {index}:")
            print(f"Vị trí máy hút bụi: {(x, y)}")
            print("Trạng thái phòng:")
            print_room(room)
            print()

        print("-" * 30)
        print()

def get_path(node):

    path = []

    while node:

        path.append({
            "action": node.action,
            "state": node.state,
            "cost": node.cost,
            "g": node.g
        })

        node = node.parent

    path.reverse()

    return path


# n = int(input("Nhập số dòng: "))
# m = int(input("Nhập số cột: "))
# k = int(input("Nhập số phần cố định: "))

# goal_state = [[0] * m for _ in range(n)]

# initial_state_1 = []
# initial_state_2 = []
# for i in range(n):
#     row_1 = []
#     row_2 = []
#     for j in range(m):
#         row_1.append(random.randint(0, 1))
#         row_2.append(random.randint(0, 1))
#     initial_state_1.append(row_1)
#     initial_state_2.append(row_2)

# for _ in range(k):
#     x = random.randint(0, n - 1)
#     y = random.randint(0, m - 1)
#     z = random.randint(0, 1)
#     initial_state_1[x][y] = z
#     initial_state_2[x][y] = z
#     print(f"Cố địng tại vị trí: [{x},{y}]")

# x = random.randint(0, n - 1)
# y = random.randint(0, m - 1)

# result = PartialSearch(build_partial_belief(n, m, x, y, 2), goal_state, n, m)

# if result:
#     print_result(result)
#     print("Đã tìm thấy giải pháp.")
# else:
#     print("Không tìm thấy giải pháp.")