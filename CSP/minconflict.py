import random


def clone_domains(variables, colors):
    return {v: list(colors) for v in variables}


def count_conflicts(var, color, assignment, neighbors):
    count = 0

    for nb in neighbors.get(var, []):
        if assignment.get(nb) == color:
            count += 1

    return count


def total_conflicts(variables, assignment, neighbors):
    total = 0

    for var in variables:
        total += count_conflicts(
            var,
            assignment[var],
            assignment,
            neighbors
        )

    return total // 2


def get_conflicted_variables(variables, assignment, neighbors):
    conflicted = []

    for var in variables:
        if count_conflicts(var, assignment[var], assignment, neighbors) > 0:
            conflicted.append(var)

    return conflicted


def choose_min_conflict_color(var, colors, assignment, neighbors):
    best_colors = []
    best_score = None

    for color in colors:
        score = count_conflicts(var, color, assignment, neighbors)

        if best_score is None or score < best_score:
            best_score = score
            best_colors = [color]
        elif score == best_score:
            best_colors.append(color)

    return random.choice(best_colors), best_score


def solve_map_coloring(variables, colors, neighbors, max_steps=5000):
    domains = clone_domains(variables, colors)

    assignment = {}

    for var in variables:
        assignment[var] = random.choice(colors)

    yield {
        "status": "assign",
        "message": "Khởi tạo ngẫu nhiên toàn bộ bản đồ cho Min-Conflicts.",
        "assignment": assignment.copy(),
        "domains": domains,
        "current_var": None,
        "current_color": None,
    }

    conflict_count = total_conflicts(variables, assignment, neighbors)

    yield {
        "status": "evaluate",
        "message": f"Số xung đột ban đầu: {conflict_count}.",
        "assignment": assignment.copy(),
        "domains": domains,
        "current_var": None,
        "current_color": None,
    }

    for step in range(1, max_steps + 1):
        conflicted = get_conflicted_variables(
            variables,
            assignment,
            neighbors
        )

        if not conflicted:
            yield {
                "status": "done",
                "message": f"Hoàn tất: Min-Conflicts tìm được lời giải sau {step - 1} bước.",
                "assignment": assignment.copy(),
                "domains": domains,
                "current_var": None,
                "current_color": None,
            }
            return

        var = random.choice(conflicted)
        old_color = assignment[var]

        best_color, best_score = choose_min_conflict_color(
            var,
            colors,
            assignment,
            neighbors
        )

        assignment[var] = best_color

        conflict_count = total_conflicts(
            variables,
            assignment,
            neighbors
        )

        yield {
            "status": "assign",
            "message": f"Bước {step}: đổi {var}: {old_color} -> {best_color}. Tổng xung đột còn {conflict_count}.",
            "assignment": assignment.copy(),
            "domains": domains,
            "current_var": var,
            "current_color": best_color,
        }

    yield {
        "status": "no_solution",
        "message": f"Min-Conflicts dừng sau {max_steps} bước nhưng vẫn còn xung đột.",
        "assignment": assignment.copy(),
        "domains": domains,
        "current_var": None,
        "current_color": None,
    }