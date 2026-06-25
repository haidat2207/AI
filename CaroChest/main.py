# main.py
# Chạy file này để chơi Caro 3x3 với người thật.
# Terminal / CMD:
#   python main.py

import tkinter as tk
from tkinter import ttk

from minimax_agent import choose_move as minimax_choose_move
from alphabeta_agent import choose_move as alphabeta_choose_move
from expectimax_agent import choose_move as expectimax_choose_move


# Đây là VAI TRÒ, không phải ký hiệu X/O.
HUMAN_PLAYER = "human"
AI_PLAYER = "ai"

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8), 
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  
    (0, 4, 8), (2, 4, 6)               
]

AGENTS = {
    "Minimax Agent": minimax_choose_move,
    "Alpha-Beta Agent": alphabeta_choose_move,
    "Expectimax Agent": expectimax_choose_move
}


class CaroAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Caro 3x3 - Chọn Agent để chơi")
        self.root.resizable(False, False)

        self.agent_var = tk.StringVar(value="Minimax Agent")
        self.first_var = tk.StringVar(value=HUMAN_PLAYER)

        self.board = [""] * 9
        self.current_player = HUMAN_PLAYER
        self.game_active = False

        # Được gán lại mỗi ván:
        # Bên đi trước luôn cầm X.
        self.human_mark = "X"
        self.ai_mark = "O"

        self.human_score = 0
        self.ai_score = 0
        self.draw_score = 0

        self.status_var = tk.StringVar()
        self.stats_var = tk.StringVar()
        self.score_var = tk.StringVar()
        self.mark_info_var = tk.StringVar()

        self.buttons = []
        self.default_button_bg = None

        self._build_ui()
        self._update_score()
        self.start_new_game()

    def _build_ui(self):
        main = tk.Frame(self.root, padx=16, pady=16)
        main.pack()

        # ================= BÀN CỜ =================
        left = tk.Frame(main)
        left.grid(row=0, column=0, sticky="n")

        tk.Label(left, text="CARO 3 × 3", font=("Arial", 18, "bold")).pack(
            pady=(0, 8)
        )

        board_frame = tk.Frame(left, bd=2, relief="groove")
        board_frame.pack()

        for index in range(9):
            row, col = divmod(index, 3)
            button = tk.Button(
                board_frame,
                text="",
                font=("Arial", 28, "bold"),
                width=4,
                height=2,
                command=lambda i=index: self.human_move(i)
            )
            button.grid(row=row, column=col, padx=2, pady=2)

            if self.default_button_bg is None:
                self.default_button_bg = button.cget("bg")
            self.buttons.append(button)

        tk.Label(
            left,
            textvariable=self.status_var,
            justify="center",
            wraplength=350,
            font=("Arial", 11, "bold")
        ).pack(pady=(12, 4))

        tk.Label(left, textvariable=self.mark_info_var, font=("Arial", 10)).pack()

        # ================= ĐIỀU KHIỂN =================
        right = tk.Frame(main)
        right.grid(row=0, column=1, sticky="n", padx=(20, 0))

        agent_box = tk.LabelFrame(right, text="Chọn Agent để đấu", padx=10, pady=10)
        agent_box.pack(fill="x", pady=(0, 10))

        ttk.Combobox(
            agent_box,
            textvariable=self.agent_var,
            values=list(AGENTS.keys()),
            state="readonly",
            width=25
        ).pack(anchor="w")

        tk.Label(
            agent_box,
            text="Mỗi agent sử dụng một thuật toán khác nhau để chọn nước đi tốt nhất cho AI.",
            justify="left",
            font=("Arial", 9)
        ).pack(anchor="w", pady=(8, 0))

        first_box = tk.LabelFrame(right, text="Ai đi trước?", padx=10, pady=8)
        first_box.pack(fill="x", pady=(0, 10))

        tk.Radiobutton(
            first_box,
            text="Người chơi đi trước",
            variable=self.first_var,
            value=HUMAN_PLAYER
        ).pack(anchor="w")

        tk.Radiobutton(
            first_box,
            text="Agent đi trước",
            variable=self.first_var,
            value=AI_PLAYER
        ).pack(anchor="w")

        controls = tk.Frame(right)
        controls.pack(fill="x", pady=(0, 10))

        tk.Button(
            controls,
            text="Chơi ván mới",
            font=("Arial", 10, "bold"),
            command=self.start_new_game
        ).grid(row=0, column=0, padx=(0, 6))

        tk.Button(controls, text="Xóa log", command=self.clear_log).grid(row=0, column=1)

        tk.Label(
            right,
            textvariable=self.score_var,
            justify="left",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            right,
            textvariable=self.stats_var,
            justify="left",
            wraplength=330,
            font=("Arial", 10)
        ).pack(anchor="w", pady=(0, 8))

        log_box = tk.LabelFrame(right, text="Log trận đấu", padx=4, pady=4)
        log_box.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(log_box)
        scrollbar.pack(side="right", fill="y")

        self.log_text = tk.Text(
            log_box,
            width=46,
            height=20,
            state="disabled",
            wrap="word",
            yscrollcommand=scrollbar.set
        )
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.log_text.yview)

    def _log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def _update_score(self):
        self.score_var.set(
            "Điểm số\n"
            f"Bạn thắng: {self.human_score}   |   "
            f"Agent thắng: {self.ai_score}   |   "
            f"Hòa: {self.draw_score}"
        )

    def _update_mark_info(self):
        self.mark_info_var.set(f"Bạn: {self.human_mark}     |     AI Agent: {self.ai_mark}")

    def _reset_board_visual(self):
        for button in self.buttons:
            button.config(
                text="",
                state="normal",
                bg=self.default_button_bg,
                disabledforeground="black"
            )

    def _disable_board(self):
        for button in self.buttons:
            button.config(state="disabled")

    def _enable_empty_cells(self):
        for index, button in enumerate(self.buttons):
            if self.board[index] == "":
                button.config(state="normal")
            else:
                button.config(state="disabled")

    def start_new_game(self):
        self.board = [""] * 9
        self.game_active = True
        self._reset_board_visual()
        self.stats_var.set("Số node đã xét: 0 | Nhánh cắt: 0")

        selected_agent = self.agent_var.get()

        # Bên nào đi trước đều là X.
        if self.first_var.get() == HUMAN_PLAYER:
            self.human_mark = "X"
            self.ai_mark = "O"
            self.current_player = HUMAN_PLAYER
        else:
            self.ai_mark = "X"
            self.human_mark = "O"
            self.current_player = AI_PLAYER

        self._update_mark_info()
        self._log(f"\n--- Ván mới | Đối thủ: {selected_agent} ---")

        if self.current_player == HUMAN_PLAYER:
            self.status_var.set("Lượt của bạn (X). Hãy bấm một ô.")
            self._log("Bạn đi trước, nên bạn là X.")
        else:
            self.status_var.set(f"{selected_agent} đi trước (X), đang suy nghĩ...")
            self._log(f"{selected_agent} đi trước, nên Agent là X. Bạn là O.")
            self._disable_board()
            self.root.after(250, self.ai_move)

    def human_move(self, index):
        if not self.game_active:
            return

        if self.current_player != HUMAN_PLAYER or self.board[index] != "":
            return

        self._place_mark(index, self.human_mark)
        self._log(f"Bạn đi {self.human_mark} tại ô {index + 1}.")

        if self._finish_if_needed():
            return

        self.current_player = AI_PLAYER
        self.status_var.set(f"{self.agent_var.get()} ({self.ai_mark}) đang suy nghĩ...")
        self._disable_board()
        self.root.after(250, self.ai_move)

    def ai_move(self):
        if not self.game_active:
            return

        selected_agent = self.agent_var.get()
        agent_function = AGENTS[selected_agent]

        # Agent nhận ký hiệu động: có thể là X hoặc O.
        move, score, stats = agent_function(
            list(self.board),
            self.ai_mark,
            self.human_mark
        )

        if move is None:
            self._finish_if_needed()
            return

        self._place_mark(move, self.ai_mark)

        shown_score = f"{score:.2f}" if selected_agent == "Expectimax Agent" else str(int(score))

        self.stats_var.set(
            f"Số node đã xét: {stats['nodes']} | "
            f"Nhánh cắt: {stats['pruned']}"
        )

        self._log(
            f"{selected_agent} đi {self.ai_mark} tại ô {move + 1}. "
            f"Điểm: {shown_score}. "
            f"Node: {stats['nodes']} | Cắt: {stats['pruned']}."
        )

        if self._finish_if_needed():
            return

        self.current_player = HUMAN_PLAYER
        self._enable_empty_cells()
        self.status_var.set(f"Lượt của bạn ({self.human_mark}). Hãy bấm một ô.")

    def _place_mark(self, index, mark):
        self.board[index] = mark
        self.buttons[index].config(text=mark, state="disabled")

    def _get_winner(self):
        for a, b, c in WIN_LINES:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a], (a, b, c)
        return None, None

    def _finish_if_needed(self):
        winner, win_line = self._get_winner()

        if winner is None and "" in self.board:
            return False

        self.game_active = False
        self._disable_board()

        if winner == self.human_mark:
            self.human_score += 1
            result = "Bạn thắng! 🎉"
            color = "#B6F2B6"
            self._log("Kết quả: Bạn thắng.")
        elif winner == self.ai_mark:
            self.ai_score += 1
            result = f"{self.agent_var.get()} thắng!"
            color = "#FFCCCC"
            self._log(f"Kết quả: {self.agent_var.get()} thắng.")
        else:
            self.draw_score += 1
            result = "Hòa!"
            color = "#FFF2B2"
            self._log("Kết quả: Hòa.")

        self.status_var.set(result)
        self._update_score()

        if win_line:
            for index in win_line:
                self.buttons[index].config(bg=color)

        return True


if __name__ == "__main__":
    root = tk.Tk()
    CaroAIApp(root)
    root.mainloop()
