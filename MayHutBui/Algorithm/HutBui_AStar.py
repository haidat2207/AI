import random
import heapq

class Node:
    def __init__(self, state, x, y, node_parent=None, action=None, cost=0, g=0):
        self.state = state
        self.x = x
        self.y = y
        self.parent = node_parent
        self.action = action
        self.cost = cost
        self.g = g

    def __lt__(self, other):
        return self.cost < other.cost

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

    random.shuffle(moves)
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

def AStar(initial_state, goal_state, x, y):

    initial_copy = copy_node(initial_state)

    if initial_copy[x][y] == 1:
        initial_copy[x][y] = 0
        
    root = Node(initial_copy, x, y, node_parent=None, action=None, cost=calculate_cost(initial_copy))
    frontier = []
    heapq.heappush(frontier, (root.cost, root))

    reached = {}

    while frontier:

        current_cost, current_node = heapq.heappop(frontier)

        current_key = (
            tuple(map(tuple, current_node.state)),
            current_node.x,
            current_node.y
        )

        reached[current_key] = current_node.cost

        if current_node.state == goal_state:
            return current_node

        moves = move(current_node.state, current_node.x, current_node.y)

        for neighbor, action, new_x, new_y in moves:

            in_frontier = any(
                n.state == neighbor and n.x == new_x and n.y == new_y
                for _, n in frontier
            )

            neighbor_key = (
                tuple(map(tuple, neighbor)),
                new_x,
                new_y,
            )

            if neighbor_key not in reached and not in_frontier:

                child = Node(
                    state=neighbor,
                    x=new_x,
                    y=new_y,
                    node_parent=current_node,
                    action=action,
                    g=current_node.g + calculate_cost(neighbor),
                )

                child.cost = child.g + calculate_cost(neighbor)

                if neighbor_key not in reached or child.cost < reached[neighbor_key]:

                    reached[neighbor_key] = child.cost

                heapq.heappush(frontier, (child.cost, child))

    return None

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
        print(f"Chi phí hiện tại: {cost}")
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

# result = AStar(initial_state, goal_state, x, y)

# if result:
#     print_result(result)
#     print("Đã tìm thấy giải pháp.")
# else:
#     print("Không tìm thấy giải pháp.")