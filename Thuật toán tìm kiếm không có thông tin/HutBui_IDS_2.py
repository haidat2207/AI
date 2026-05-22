import random

class Node:
    def __init__(self, state, x, y, node_parent=None, action=None, depth=0):
        self.state = state
        self.x = x
        self.y = y
        self.parent = node_parent
        self.action = action
        self.depth = depth

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


def IDS(initial_state, goal_state, x, y, depth_limit):
    depth = 0
    while depth <= depth_limit:
        result = DLS(initial_state, goal_state, x, y, depth)
        if result is not False:
            return result
        depth += 1
    return None


def DLS(initial_state, goal_state, x, y, depth_limit):

    initial_copy = copy_node(initial_state)

    if initial_copy[x][y] == 1:
        initial_copy[x][y] = 0
    root = Node(initial_copy, x, y, node_parent=None, action=None, depth=0)

    frontier = [root]

    reached = set()

    while frontier:

        current_node = frontier.pop()

        reached.add((tuple(map(tuple, current_node.state)), current_node.x, current_node.y))

        if current_node.state == goal_state:
            return current_node
        
        if current_node.depth>= depth_limit:
            continue

        
        moves = move(current_node.state, current_node.x, current_node.y)

        for neighbor, action, new_x, new_y in moves:

            in_frontier = any(
                node.state == neighbor and node.x == new_x and node.y == new_y for node in frontier
            )

            neighbor_key = (
                tuple(map(tuple, neighbor)),
                new_x,
                new_y
            )

            if neighbor_key not in reached and not in_frontier:

                child = Node(
                    state=neighbor,
                    x=new_x,
                    y=new_y,
                    node_parent=current_node,
                    action=action,
                    depth=current_node.depth + 1
                )

                if child.state == goal_state:
                    return child

                frontier.append(child)

    return False

def print_room(state):
    for row in state:
        print(row)

def print_result(node):

    path = []

    while node:

        path.append((node.action, node.state,node.x, node.y, node.depth))
        node = node.parent

    path.reverse()

    for action, state, x, y, depth in path:
        print(f"Bước: {depth}")
        print(f"Action: {action}")
        print(f"Vị trí máy hút bụi hiện tại: {(x, y)}")
        print("Trạng thái hiện tại của phòng:")
        print_room(state)
        print()

def get_path(node):

    path = []

    while node:

        path.append({
            "action": node.action,
            "state": node.state,
            "x": node.x,
            "y": node.y,
            "depth": node.depth
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

# depth_limit = int(input("Nhập giới hạn độ sâu: "))
# result = IDS(initial_state, goal_state, x, y, depth_limit)

# if result:
#     print_result(result)
#     print("Đã tìm thấy giải pháp.")
# else:
#     print("Không tìm thấy giải pháp.")