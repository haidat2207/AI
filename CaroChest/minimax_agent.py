MOVE_ORDER = [4, 0, 2, 6, 8, 1, 3, 5, 7]
WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]


def _winner(board):
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None


def _terminal_score(board, depth, ai_mark, human_mark):
    winner = _winner(board)

    if winner == ai_mark:
        return 10 - depth
    if winner == human_mark:
        return depth - 10
    if "" not in board:
        return 0
    return None


def _minimax(board, player, depth, ai_mark, human_mark, stats):
    stats["nodes"] += 1

    score = _terminal_score(board, depth, ai_mark, human_mark)
    if score is not None:
        return score

    if player == ai_mark:  
        best_value = float("-inf")
        for move in MOVE_ORDER:
            if board[move] == "":
                board[move] = ai_mark
                value = _minimax(
                    board, human_mark, depth + 1, ai_mark, human_mark, stats
                )
                board[move] = ""
                best_value = max(best_value, value)
        return best_value

    best_value = float("inf")
    for move in MOVE_ORDER:
        if board[move] == "":
            board[move] = human_mark
            value = _minimax(
                board, ai_mark, depth + 1, ai_mark, human_mark, stats
            )
            board[move] = ""
            best_value = min(best_value, value)
    return best_value


def choose_move(board, ai_mark="O", human_mark="X"):
    """
    Trả về:
        move  : chỉ số ô 0..8 mà AI nên đi
        score : điểm Minimax của nước đi đó
        stats : {'nodes': ..., 'pruned': 0}
    """
    stats = {"nodes": 0, "pruned": 0}
    best_move = None
    best_score = float("-inf")

    for move in MOVE_ORDER:
        if board[move] != "":
            continue

        board[move] = ai_mark
        score = _minimax(board, human_mark, 1, ai_mark, human_mark, stats)
        board[move] = ""

        if score > best_score:
            best_score = score
            best_move = move

    return best_move, best_score, stats
