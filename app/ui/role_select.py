import tkinter as tk


class RoleSelectFrame(tk.Frame):
    def __init__(self, master, on_select):
        super().__init__(master)
        self.on_select = on_select
        self._build()

    def _build(self) -> None:
        title = tk.Label(self, text="Select a role", font=("Helvetica", 16, "bold"))
        title.pack(pady=20)

        teacher_btn = tk.Button(
            self,
            text="Teacher",
            width=20,
            command=lambda: self.on_select("teacher"),
        )
        teacher_btn.pack(pady=10)

        student_btn = tk.Button(
            self,
            text="Student",
            width=20,
            command=lambda: self.on_select("student"),
        )
        student_btn.pack(pady=10)
