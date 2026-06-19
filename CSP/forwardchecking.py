def is_consistent(var, color, assignment, neighbors):
    for nb in neighbors.get(var, []):
        if assignment.get(nb) == color:
            return False, nb
    return True, None


def clone_domains(domains, variables):
    return {v: domains[v][:] for v in variables}


def choose_unassigned_variable(variables, assignment, domains, neighbors):
    unassigned = [v for v in variables if v not in assignment]
    if not unassigned:
        return None

    return min(
        unassigned,
        key=lambda v: (len(domains[v]), -len(neighbors.get(v, [])))
    )


def forward_check(var, color, assignment, domains, neighbors):
    pruned = []

    for nb in neighbors.get(var, []):
        if nb not in assignment and color in domains[nb]:
            domains[nb].remove(color)
            pruned.append((nb, color))

            if len(domains[nb]) == 0:
                return False, pruned, nb

    return True, pruned, None


def solve_map_coloring(variables, colors, neighbors):
    assignment = {}
    domains = {v: list(colors) for v in variables}

    yield {
        "status": "start",
        "message": "Bắt đầu thuật toán Forward Checking.",
        "assignment": assignment.copy(),
        "domains": clone_domains(domains, variables),
        "current_var": None,
        "current_color": None,
    }

    def backtrack(local_domains):
        if len(assignment) == len(variables):
            yield {
                "status": "done",
                "message": "Hoàn tất: tất cả vùng đã được tô màu hợp lệ.",
                "assignment": assignment.copy(),
                "domains": clone_domains(local_domains, variables),
                "current_var": None,
                "current_color": None,
            }
            return True

        var = choose_unassigned_variable(variables, assignment, local_domains, neighbors)

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
                "message": f"Thử tô {var} bằng màu {color}.",
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

            fc_ok, pruned, empty_var = forward_check(
                var, color, assignment, new_domains, neighbors
            )

            if pruned:
                short = pruned[:5]
                pruned_text = ", ".join([f"xóa {c} khỏi {v}" for v, c in short])
                if len(pruned) > 5:
                    pruned_text += f", ... ({len(pruned)} vùng)"
            else:
                pruned_text = "không cần xóa màu nào"

            yield {
                "status": "prune",
                "message": f"Forward checking: {pruned_text}.",
                "assignment": assignment.copy(),
                "domains": clone_domains(new_domains, variables),
                "current_var": var,
                "current_color": color,
            }

            if fc_ok:
                solved = yield from backtrack(new_domains)
                if solved:
                    return True
            else:
                yield {
                    "status": "reject",
                    "message": f"Loại nhánh vì miền màu của {empty_var} bị rỗng.",
                    "assignment": assignment.copy(),
                    "domains": clone_domains(new_domains, variables),
                    "current_var": empty_var,
                    "current_color": None,
                }

            old_color = assignment.pop(var)
            yield {
                "status": "backtrack",
                "message": f"Quay lui: bỏ màu {old_color} khỏi {var} và phục hồi miền màu.",
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
