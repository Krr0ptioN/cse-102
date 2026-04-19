from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from libs.logger import get_logger


logger = get_logger("app.scripts.build_release")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a standalone desktop binary with PyInstaller"
    )
    parser.add_argument(
        "--name",
        default="CSE102-App",
        help="Output binary name (default: CSE102-App)",
    )
    parser.add_argument(
        "--mode",
        choices=("onefile", "onedir"),
        default="onefile",
        help="Bundle mode (default: onefile)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean PyInstaller cache and previous build output",
    )
    return parser.parse_args()


def _data_separator() -> str:
    return ";" if platform.system() == "Windows" else ":"


def _artifact_path(app_root: Path, name: str, mode: str) -> Path:
    dist_dir = app_root / "dist"
    if mode == "onedir":
        return dist_dir / name
    if platform.system() == "Windows":
        return dist_dir / f"{name}.exe"
    return dist_dir / name


def build(args: argparse.Namespace) -> Path:
    app_root = APP_ROOT
    project_root = PROJECT_ROOT
    entrypoint = app_root / "main.py"
    assets_dir = app_root / "assets"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--name",
        args.name,
        "--paths",
        str(project_root),
        "--hidden-import",
        "matplotlib.backends.backend_tkagg",
        "--collect-all",
        "customtkinter",
        "--add-data",
        f"{assets_dir}{_data_separator()}app/assets",
    ]

    if args.clean:
        cmd.append("--clean")

    if args.mode == "onefile":
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    cmd.append(str(entrypoint))

    logger.banner("Build Release")
    logger.info("Mode=%s Name=%s", args.mode, args.name)
    logger.info("Running PyInstaller command")
    subprocess.run(cmd, cwd=app_root, check=True)
    return _artifact_path(app_root, args.name, args.mode)


def main() -> None:
    args = parse_args()
    artifact = build(args)
    logger.success("Build complete: %s", artifact)


if __name__ == "__main__":
    main()
