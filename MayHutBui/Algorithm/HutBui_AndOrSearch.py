
import random


class Node:
    def __init__(self, state, x, y, parent=None, action=None,
                 real_action=None, node_type="NODE", step=0):
        self.state = state
        self.x = x
        self.y = y
        self.parent = parent
        self.action = action       
        self.real_action = real_action   
        self.node_type = node_type
        self.step = step


ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]

DIRECTION = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}

OUTCOME_RULES = {
    "UP": ["UP", "LEFT", "RIGHT"],
    "DOWN": ["DOWN", "LEFT", "RIGHT"],
    "LEFT": ["LEFT", "UP", "DOWN"],
    "RIGHT": ["RIGHT", "UP", "DOWN"],
}

def copy_node(state):
    return [row[:] for row in state]

def state_to_tuple(state):
    return tuple(tuple(row) for row in state)

def make_key(state, x, y):
    return (state_to_tuple(state), x, y)

def calculate_cost(state):
    return sum(row.count(1) for row in state)

def goal_test(state, goal_state):
    return state == goal_state

def valid_position(x, y, n, m):
    return 0 <= x < n and 0 <= y < m

def possible_actions(x, y, n, m):
    """OR: robot chọn một hành động hợp lệ."""
    actions = []
    for action, (dx, dy) in DIRECTION.items():
        nx = x + dx
        ny = y + dy
        if valid_position(nx, ny, n, m):
            actions.append(action)
    return actions

def apply_move(state, x, y, action):
    n = len(state)
    m = len(state[0])

    dx, dy = DIRECTION[action]
    nx = x + dx
    ny = y + dy

    if not valid_position(nx, ny, n, m):
        return None

    new_state = copy_node(state)

    if new_state[nx][ny] == 1:
        new_state[nx][ny] = 0

    return new_state, nx, ny


def results(state, x, y, chosen_action):
    outcomes = []

    for real_action in OUTCOME_RULES[chosen_action]:
        result = apply_move(state, x, y, real_action)

        if result is None:
            continue

        new_state, nx, ny = result
        key = make_key(new_state, nx, ny)

        duplicated = False
        for old in outcomes:
            if old["key"] == key:
                duplicated = True
                break

        if not duplicated:
            outcomes.append({
                "state": new_state,
                "x": nx,
                "y": ny,
                "chosen_action": chosen_action,
                "real_action": real_action,
                "key": key,
            })

    return outcomes


def AND_OR_Search(initial_state, goal_state, x, y, max_depth=None):
    state = copy_node(initial_state)

    # Máy đang đứng ở ô dơ thì hút sạch ô đó trước.
    if state[x][y] == 1:
        state[x][y] = 0

    if max_depth is None:
        max_depth = len(state) * len(state[0]) * 5

    root = Node(
        state=state,
        x=x,
        y=y,
        parent=None,
        action=None,
        real_action=None,
        node_type="START",
        step=0
    )

    logs = []
    path_set = set()

    goal_node = OR_SEARCH(
        node=root,
        goal_state=goal_state,
        path_set=path_set,
        logs=logs,
        depth=max_depth
    )

    return goal_node, logs


def OR_SEARCH(node, goal_state, path_set, logs, depth):
    key = make_key(node.state, node.x, node.y)

    logs.append({
        "type": "OR",
        "message": f"OR tại {(node.x, node.y)} | còn {calculate_cost(node.state)} ô dơ",
        "state": copy_node(node.state),
        "x": node.x,
        "y": node.y,
        "action": node.action,
        "real_action": node.real_action
    })

    if goal_test(node.state, goal_state):
        node.node_type = "GOAL"
        logs.append({
            "type": "GOAL",
            "message": "Tới goal: nhà đã sạch hoàn toàn.",
            "state": copy_node(node.state),
            "x": node.x,
            "y": node.y,
            "action": node.action,
            "real_action": node.real_action
        })
        return node

    if depth <= 0:
        logs.append({
            "type": "FAIL",
            "message": "Fail: vượt quá giới hạn độ sâu.",
            "state": copy_node(node.state),
            "x": node.x,
            "y": node.y
        })
        return None

    if key in path_set:
        logs.append({
            "type": "FAIL",
            "message": "Fail: gặp lại state cũ nên bỏ để tránh lặp.",
            "state": copy_node(node.state),
            "x": node.x,
            "y": node.y
        })
        return None

    path_set.add(key)

    actions = possible_actions(node.x, node.y, len(node.state), len(node.state[0]))

    # Ưu tiên action nào có outcome làm giảm số ô dơ nhiều hơn.
    random.shuffle(actions)
    actions.sort(
        key=lambda action: min(
            calculate_cost(outcome["state"])
            for outcome in results(node.state, node.x, node.y, action)
        )
    )

    for action in actions:
        logs.append({
            "type": "TRY_ACTION",
            "message": f"Thử action {action}.",
            "state": copy_node(node.state),
            "x": node.x,
            "y": node.y,
            "action": action
        })

        result = AND_SEARCH(
            parent_node=node,
            chosen_action=action,
            goal_state=goal_state,
            path_set=path_set,
            logs=logs,
            depth=depth - 1
        )

        if result is not None:
            path_set.remove(key)
            return result

        logs.append({
            "type": "REJECT_ACTION",
            "message": f"Action {action} chưa tới goal, thử action khác.",
            "state": copy_node(node.state),
            "x": node.x,
            "y": node.y,
            "action": action
        })

    path_set.remove(key)
    return None


def AND_SEARCH(parent_node, chosen_action, goal_state, path_set, logs, depth):
    outcomes = results(
        parent_node.state,
        parent_node.x,
        parent_node.y,
        chosen_action
    )

    logs.append({
        "type": "AND",
        "message": f"AND của action {chosen_action}: sinh {len(outcomes)} outcome.",
        "state": copy_node(parent_node.state),
        "x": parent_node.x,
        "y": parent_node.y,
        "action": chosen_action
    })

    for outcome in outcomes:
        child = Node(
            state=outcome["state"],
            x=outcome["x"],
            y=outcome["y"],
            parent=parent_node,
            action=chosen_action,
            real_action=outcome["real_action"],
            node_type="AND_RESULT",
            step=parent_node.step + 1
        )

        logs.append({
            "type": "OUTCOME",
            "message": (
                f"Outcome: chọn {chosen_action}, thực tế đi {outcome['real_action']}, "
                f"tới {(child.x, child.y)} | còn {calculate_cost(child.state)} ô dơ"
            ),
            "state": copy_node(child.state),
            "x": child.x,
            "y": child.y,
            "action": chosen_action,
            "real_action": outcome["real_action"]
        })

        result = OR_SEARCH(
            node=child,
            goal_state=goal_state,
            path_set=path_set,
            logs=logs,
            depth=depth
        )

        if result is not None:
            return result

    return None


def get_path(goal_node):
    path = []

    node = goal_node

    while node:
        path.append({
            "action": node.action,
            "real_action": node.real_action,
            "state": node.state,
            "x": node.x,
            "y": node.y,
            "step": node.step,
            "node_type": node.node_type,
            "cost": calculate_cost(node.state)
        })

        node = node.parent

    path.reverse()
    return path


def get_log_steps(logs):
    result = []

    for i, item in enumerate(logs):
        result.append({
            "step": i,
            "type": item.get("type"),
            "message": item.get("message"),
            "state": item.get("state"),
            "x": item.get("x"),
            "y": item.get("y"),
            "action": item.get("action"),
            "real_action": item.get("real_action"),
        })

    return result


def print_room(state):
    for row in state:
        print(row)


def print_result(goal_node):
    if goal_node is None:
        print("Không tìm thấy đường tới goal.")
        return

    path = get_path(goal_node)

    for item in path:
        print(f"Bước: {item['step']}")
        print(f"OR chọn action: {item['action']}")
        print(f"AND outcome thực tế: {item['real_action']}")
        print(f"Vị trí máy hút bụi: {(item['x'], item['y'])}")
        print(f"Số ô dơ còn lại: {item['cost']}")
        print("Trạng thái phòng:")
        print_room(item["state"])
        print("-" * 30)


# n = int(input("Nhập số dòng: "))
# m = int(input("Nhập số cột: "))

# goal_state = [[0] * m for _ in range(n)]

# initial_state = []
# for i in range(n):
#     row = list(map(int, input().split()))
#     initial_state.append(row)
# start_x = random.randint(0, n - 1)
# start_y = random.randint(0, m - 1)

# result, logs = AND_OR_Search(
#     initial_state=initial_state,
#     goal_state=goal_state,
#     x=start_x,
#     y=start_y,
#     max_depth=30
# )

# print_result(result)
