def is_consistent(var, color, assignment, neighbors):
    for nb in neighbors.get(var, []):
        if assignment.get(nb) == color:
            return False, nb
    return True, None


def choose_unassigned_variable(variables, assignment, neighbors):
    unassigned = [v for v in variables if v not in assignment]
    if not unassigned:
        return None

    return max(
        unassigned,
        key=lambda v: (
            sum(1 for nb in neighbors.get(v, []) if nb in assignment),
            len(neighbors.get(v, [])),
        )
    )


def solve_map_coloring(variables, colors, neighbors):
    assignment = {}

    yield {
        "status": "start",
        "message": "Bắt đầu thuật toán Backtracking.",
        "assignment": assignment.copy(),
        "domains": None,
        "current_var": None,
        "current_color": None,
    }

    def backtrack():
        if len(assignment) == len(variables):
            yield {
                "status": "done",
                "message": "Hoàn tất: tất cả vùng đã được tô màu hợp lệ.",
                "assignment": assignment.copy(),
                "domains": None,
                "current_var": None,
                "current_color": None,
            }
            return True

        var = choose_unassigned_variable(variables, assignment, neighbors)

        yield {
            "status": "select",
            "message": f"Chọn vùng chưa tô: {var}.",
            "assignment": assignment.copy(),
            "domains": None,
            "current_var": var,
            "current_color": None,
        }

        for color in colors:
            yield {
                "status": "try",
                "message": f"Thử tô {var} bằng màu {color}.",
                "assignment": assignment.copy(),
                "domains": None,
                "current_var": var,
                "current_color": color,
            }

            ok, conflict = is_consistent(var, color, assignment, neighbors)

            if ok:
                assignment[var] = color

                yield {
                    "status": "assign",
                    "message": f"Gán {var} = {color}.",
                    "assignment": assignment.copy(),
                    "domains": None,
                    "current_var": var,
                    "current_color": color,
                }

                solved = yield from backtrack()
                if solved:
                    return True

                old_color = assignment.pop(var)
                yield {
                    "status": "backtrack",
                    "message": f"Quay lui: bỏ màu {old_color} khỏi {var}.",
                    "assignment": assignment.copy(),
                    "domains": None,
                    "current_var": var,
                    "current_color": old_color,
                }
            else:
                yield {
                    "status": "reject",
                    "message": f"Loại {var} = {color} vì trùng màu với vùng kề {conflict}.",
                    "assignment": assignment.copy(),
                    "domains": None,
                    "current_var": var,
                    "current_color": color,
                }

        yield {
            "status": "dead_end",
            "message": f"{var} không còn màu hợp lệ, cần quay lui.",
            "assignment": assignment.copy(),
            "domains": None,
            "current_var": var,
            "current_color": None,
        }
        return False

    solved = yield from backtrack()

    if not solved:
        yield {
            "status": "no_solution",
            "message": "Không tìm được lời giải với tập màu hiện tại.",
            "assignment": assignment.copy(),
            "domains": None,
            "current_var": None,
            "current_color": None,
        }
