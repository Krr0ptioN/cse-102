from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from tkinter import font as tkfont

try:
    import customtkinter as ctk
except Exception:  # pragma: no cover - optional dependency
    ctk = None


@dataclass(frozen=True)
class Typography:
    # Primary brand face
    font_family: str = "Geist"
    font_size: str = "16px"
    line_height: str = "1.5"

    @staticmethod
    def primary_font_family() -> str:
        """Return the primary family for toolkits that expect a single name."""

        return Typography().font_family.split(",")[0].strip()

    @staticmethod
    def _font_dir() -> Path:
        return (Path(__file__).resolve().parent.parent / "assets" / "fonts").resolve()

    @staticmethod
    def _font_candidates() -> Iterable[Path]:
        base = Typography._font_dir()
        for name in (
            "Geist-Regular.otf",
            "Geist-Medium.otf",
            "Geist-SemiBold.otf",
            "Geist-Bold.otf",
        ):
            path = base / name
            if path.exists():
                yield path

    @staticmethod
    def ensure_tk_font(root) -> None:
        """Load Geist into Tk from bundled assets if not already available."""

        family = Typography.primary_font_family()
        if family in tkfont.families(root):
            return
        for path in Typography._font_candidates():
            try:
                # Creating a named font binds the family; keep name unique per root.
                root.tk.call(
                    "font",
                    "create",
                    f"{family}-{path.name}",
                    "-family",
                    family,
                    "-size",
                    10,
                    "-file",
                    str(path),
                )
            except Exception:
                continue

    @staticmethod
    def _ctk_load_fonts_from_disk() -> None:
        if ctk is None:
            return
        for path in Typography._font_candidates():
            try:
                ctk.FontManager.load_font(str(path))
            except Exception:
                continue

    _ctk_default: Optional["ctk.CTkFont"] = None

    @staticmethod
    def _ctk_default_font() -> "ctk.CTkFont":
        if ctk is None:
            raise RuntimeError("CustomTkinter is not available")
        if Typography._ctk_default is None:
            Typography._ctk_default = ctk.CTkFont(
                family=Typography.primary_font_family(), size=11, weight="normal"
            )
        return Typography._ctk_default

    @staticmethod
    def ensure_ctk_font(root=None) -> None:
        """Load Geist into CustomTkinter from bundled assets if not available."""

        if ctk is None:
            return
        Typography._ctk_load_fonts_from_disk()

        # Also make sure Tk knows the family for this root (CTk relies on Tk fonts).
        temp_root = None
        if root is None and not getattr(ctk.ThemeManager, "initialized", False):
            try:
                temp_root = ctk.CTk()
            except Exception:
                temp_root = None
        target_root = root or temp_root
        if target_root:
            try:
                Typography.ensure_tk_font(target_root)
            except Exception:
                pass
        if temp_root:
            temp_root.destroy()

        Typography._ctk_default_font()
