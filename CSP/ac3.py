def clone_domains(domains, variables):
    return {v: domains[v][:] for v in variables}


def is_consistent(var, color, assignment, neighbors):
    for nb in neighbors.get(var, []):
        if assignment.get(nb) == color:
            return False, nb
    return True, None


def revise(domains, xi, xj):
    removed = []

    for color_i in domains[xi][:]:
        supported = False

        for color_j in domains[xj]:
            if color_i != color_j:
                supported = True
                break

        if not supported:
            domains[xi].remove(color_i)
            removed.append(color_i)

    return removed


def ac3(domains, variables, neighbors):
    queue = []

    for xi in variables:
        for xj in neighbors.get(xi, []):
            queue.append((xi, xj))

    while queue:
        xi, xj = queue.pop(0)

        removed = revise(domains, xi, xj)

        if removed:
            if len(domains[xi]) == 0:
                return False, xi, removed

            for xk in neighbors.get(xi, []):
                if xk != xj:
                    queue.append((xk, xi))

    return True, None, []


def ac3_after_assign(domains, var, neighbors):
    queue = []

    for nb in neighbors.get(var, []):
        queue.append((nb, var))

    while queue:
        xi, xj = queue.pop(0)

        removed = revise(domains, xi, xj)

        if removed:
            if len(domains[xi]) == 0:
                return False, xi, removed

            for xk in neighbors.get(xi, []):
                if xk != xj:
                    queue.append((xk, xi))

    return True, None, []


def choose_unassigned_variable(variables, assignment, domains, neighbors):
    unassigned = [v for v in variables if v not in assignment]

    return min(
        unassigned,
        key=lambda v: (len(domains[v]), -len(neighbors.get(v, [])))
    )


def solve_map_coloring(variables, colors, neighbors):
    assignment = {}
    domains = {v: list(colors) for v in variables}

    yield {
        "status": "start",
        "message": "Bắt đầu thuật toán AC-3 + Backtracking.",
        "assignment": assignment.copy(),
        "domains": clone_domains(domains, variables),
        "current_var": None,
        "current_color": None,
    }

    def backtrack(local_domains):
        if len(assignment) == len(variables):
            yield {
                "status": "done",
                "message": "Hoàn tất: AC-3 + Backtracking đã tô màu hợp lệ.",
                "assignment": assignment.copy(),
                "domains": clone_domains(local_domains, variables),
                "current_var": None,
                "current_color": None,
            }
            return True

        var = choose_unassigned_variable(
            variables,
            assignment,
            local_domains,
            neighbors
        )

        yield {
            "status": "select",
            "message": f"Chọn {var} theo MRV.",
            "assignment": assignment.copy(),
            "domains": clone_domains(local_domains, variables),
            "current_var": var,
            "current_color": None,
        }

        for color in local_domains[var][:]:
            yield {
                "status": "try",
                "message": f"Thử gán {var} = {color}.",
                "assignment": assignment.copy(),
                "domains": clone_domains(local_domains, variables),
                "current_var": var,
                "current_color": color,
            }

            ok, conflict = is_consistent(var, color, assignment, neighbors)

            if not ok:
                yield {
                    "status": "reject",
                    "message": f"Loại {var} = {color} vì trùng màu với vùng kề {conflict}.",
                    "assignment": assignment.copy(),
                    "domains": clone_domains(local_domains, variables),
                    "current_var": var,
                    "current_color": color,
                }
                continue

            assignment[var] = color

            new_domains = clone_domains(local_domains, variables)
            new_domains[var] = [color]

            yield {
                "status": "assign",
                "message": f"Gán {var} = {color}.",
                "assignment": assignment.copy(),
                "domains": clone_domains(new_domains, variables),
                "current_var": var,
                "current_color": color,
            }

            ac_ok, empty_var, removed = ac3_after_assign(
                new_domains,
                var,
                neighbors
            )

            if ac_ok:
                yield {
                    "status": "prune",
                    "message": f"AC-3 lan truyền ràng buộc sau khi gán {var}.",
                    "assignment": assignment.copy(),
                    "domains": clone_domains(new_domains, variables),
                    "current_var": var,
                    "current_color": color,
                }

                solved = yield from backtrack(new_domains)

                if solved:
                    return True

            else:
                yield {
                    "status": "reject",
                    "message": f"AC-3 loại nhánh vì miền màu của {empty_var} bị rỗng.",
                    "assignment": assignment.copy(),
                    "domains": clone_domains(new_domains, variables),
                    "current_var": empty_var,
                    "current_color": None,
                }

            old_color = assignment.pop(var)

            yield {
                "status": "backtrack",
                "message": f"Quay lui: bỏ màu {old_color} khỏi {var}.",
                "assignment": assignment.copy(),
                "domains": clone_domains(local_domains, variables),
                "current_var": var,
                "current_color": old_color,
            }

        yield {
            "status": "dead_end",
            "message": f"{var} không còn màu hợp lệ, cần quay lui.",
            "assignment": assignment.copy(),
            "domains": clone_domains(local_domains, variables),
            "current_var": var,
            "current_color": None,
        }

        return False

    solved = yield from backtrack(domains)

    if not solved:
        yield {
            "status": "no_solution",
            "message": "Không tìm được lời giải với tập màu hiện tại.",
            "assignment": assignment.copy(),
            "domains": clone_domains(domains, variables),
            "current_var": None,
            "current_color": None,
        }