from dataclasses import dataclass
import ctypes
from pathlib import Path
import shutil
import subprocess
import sys
from typing import ClassVar, Iterable, Optional

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
    _resolved_family: ClassVar[Optional[str]] = None

    @staticmethod
    def primary_font_family() -> str:
        """Return the primary family for toolkits that expect a single name."""

        # Ensure bundled fonts are registered.
        Typography.bootstrap_fonts()
        if Typography._resolved_family:
            return Typography._resolved_family
        
        # Default to Geist; it will be used as a key in Tk/CTk font managers.
        return "Geist"

    @staticmethod
    def _resolve_family_from_fontconfig(preferred: str) -> Optional[str]:
        if not sys.platform.startswith("linux"):
            return None
        try:
            result = subprocess.run(
                ["fc-list", ":", "family"],
                check=False,
                capture_output=True,
                text=True,
            )
        except Exception:
            return None
        if result.returncode != 0 or not result.stdout:
            return None
        families: set[str] = set()
        for line in result.stdout.splitlines():
            for item in line.split(","):
                name = item.strip()
                if name:
                    families.add(name)
        if preferred in families:
            return preferred
        alias_priority = (
            "Geist",
            "Geist Regular",
            "Geist Medium",
            "Geist SemiBold",
            "Geist Bold",
        )
        for alias in alias_priority:
            if alias in families:
                return alias
        preferred_lower = preferred.lower()
        for name in sorted(families):
            if name.lower().startswith(preferred_lower):
                return name
        return None

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

    _bootstrapped: ClassVar[bool] = False

    @staticmethod
    def _register_windows_fonts() -> None:
        # Register bundled fonts for the current Windows session.
        if not sys.platform.startswith("win"):
            return
        add_font_resource = ctypes.windll.gdi32.AddFontResourceExW
        fr_private = 0x10
        for path in Typography._font_candidates():
            try:
                add_font_resource(str(path), fr_private, 0)
            except Exception:
                continue

    @staticmethod
    def _register_linux_fonts() -> None:
        # Install user-local copies and refresh fontconfig cache.
        if not sys.platform.startswith("linux"):
            return
        targets = (
            Path.home() / ".local" / "share" / "fonts" / "CSE102ProjectManager",
            Path.home() / ".fonts" / "CSE102ProjectManager",
        )

        for target_dir in targets:
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                continue
            for path in Typography._font_candidates():
                target = target_dir / path.name
                try:
                    if not target.exists() or path.stat().st_mtime > target.stat().st_mtime:
                        shutil.copy2(path, target)
                except Exception:
                    continue

        # Always refresh once; some Linux setups only discover user fonts after cache update.
        try:
            subprocess.run(
                ["fc-cache", "-f"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    @staticmethod
    def bootstrap_fonts() -> None:
        """Best-effort pre-root font registration for bundled assets."""

        if Typography._bootstrapped:
            return
        Typography._ctk_load_fonts_from_disk()
        Typography._register_windows_fonts()
        Typography._register_linux_fonts()
        # Linux font family aliases can vary; resolve once via fontconfig.
        Typography._resolved_family = Typography._resolve_family_from_fontconfig(
            Typography().font_family.split(",")[0].strip()
        ) or Typography._resolved_family
        Typography._bootstrapped = True

    @staticmethod
    def ensure_tk_font(root) -> None:
        """Load Geist into Tk from bundled assets if not already available."""

        Typography.bootstrap_fonts()
        families = set(tkfont.families(root))
        family = Typography.primary_font_family()
        if family in families:
            return
        # Tk may expose bundled faces under a nearby alias (e.g. "Geist Regular").
        for candidate in sorted(families):
            if candidate.lower().startswith("geist"):
                Typography._resolved_family = candidate
                return
        # Windows fallback only; Linux can discover user fonts after cache refresh.
        if sys.platform.startswith("win"):
            # Python 3.14 + CustomTkinter can fail on multi-word family names.
            for candidate in ("Arial", "Calibri", "Tahoma", "Verdana", "Consolas"):
                if candidate in families:
                    Typography._resolved_family = candidate
                    return
            try:
                fallback = tkfont.nametofont("TkDefaultFont").cget("family")
                if fallback:
                    if " " in fallback:
                        for candidate in sorted(families):
                            if candidate and " " not in candidate:
                                Typography._resolved_family = candidate
                                return
                    Typography._resolved_family = fallback
            except Exception:
                pass

    @staticmethod
    def _ctk_load_fonts_from_disk() -> None:
        if ctk is None:
            return
        for path in Typography._font_candidates():
            try:
                ctk.FontManager.load_font(str(path))
            except Exception:
                continue

    _ctk_default: ClassVar[Optional["ctk.CTkFont"]] = None

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
        Typography.bootstrap_fonts()
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
