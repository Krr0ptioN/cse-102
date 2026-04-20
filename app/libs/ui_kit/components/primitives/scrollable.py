from __future__ import annotations

import tkinter as tk
from ...theme import palette


from ._base import ctk, use_ctk


class ScrollableFrame(tk.Frame):
    """A reusable scrollable container using Canvas and Scrollbar.
    
    The 'scrollable_content' attribute is the frame where you should pack/grid children.
    """

    def __init__(self, master, **kwargs) -> None:
        colors = palette()
        bg = kwargs.get("bg", colors["bg"])
        super().__init__(master, bg=bg)

        self.canvas = tk.Canvas(
            self,
            bg=bg,
            highlightthickness=0,
            bd=0,
        )
        
        if use_ctk(master) and ctk is not None:
            self.scrollbar = ctk.CTkScrollbar(
                self,
                orientation="vertical",
                command=self.canvas.yview,
            )
        else:
            self.scrollbar = tk.Scrollbar(
                self,
                orient="vertical",
                command=self.canvas.yview,
            )
            
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.scrollable_content = tk.Frame(self.canvas, bg=bg)
        self._window_id = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_content,
            anchor="nw",
        )

        self.scrollable_content.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Mouse wheel support
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_frame_configure(self, _event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self.canvas.itemconfigure(self._window_id, width=event.width)

    def _on_mousewheel(self, event) -> None:
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear(self) -> None:
        """Destroy all children of the scrollable_content."""
        for child in self.scrollable_content.winfo_children():
            child.destroy()
