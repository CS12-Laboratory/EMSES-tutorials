from __future__ import annotations

import argparse
import filecmp
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from . import __version__


DEFAULT_REPO_URL = "https://github.com/CS12-Laboratory/EMSES-tutorials.git"
DEFAULT_REF = "main"
DEFAULT_PYTHON = "/usr/bin/python3.12"
DEFAULT_VENV = ".venv"
DEPLOY_PATHS = [
    ".gitignore",
    ".mypython",
    ".vscode",
    "LICENSE",
    "README.md",
    "README_en.md",
    "docs",
    "dshield0",
    "dshield1",
    "dshield2",
    "imgs",
    "requirements.txt",
]
VSCODE_EXTENSIONS = [
    "ms-python.python",
    "ms-toolsai.jupyter",
    "tamasfe.even-better-toml",
]


class CommandError(RuntimeError):
    pass


def info(message: str) -> None:
    print(f"[INFO] {message}", flush=True)


def warn(message: str) -> None:
    print(f"[WARN] {message}", flush=True)


def fail(message: str, code: int = 1) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(code)


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    prefix = f"(cd {cwd} && " if cwd else ""
    suffix = ")" if cwd else ""
    info(f"$ {prefix}{' '.join(cmd)}{suffix}")
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    result = subprocess.run(cmd, cwd=cwd, env=run_env, text=True, check=False)
    if check and result.returncode != 0:
        raise CommandError(f"command failed with exit code {result.returncode}: {cmd}")
    return result


def find_command(name: str) -> str | None:
    path = shutil.which(name)
    if path:
        return path
    local_path = Path.home() / ".local" / "bin" / name
    if local_path.exists() and os.access(local_path, os.X_OK):
        return str(local_path)
    return None


def require_command(name: str) -> str:
    path = find_command(name)
    if path:
        return path
    raise CommandError(
        f"required command not found: {name} "
        f"(checked PATH and {Path.home() / '.local' / 'bin'})"
    )


def github_archive_url(repo_url: str, ref: str) -> str:
    url = repo_url.removeprefix("git+").removesuffix(".git")
    match = re.search(r"github\.com[:/]([^/]+)/([^/]+)$", url)
    if not match:
        raise CommandError(
            "only GitHub repository URLs are supported for archive setup: "
            f"{repo_url}"
        )
    owner, repo = match.groups()
    return f"https://codeload.github.com/{owner}/{repo}/zip/{ref}"


def download_archive(repo_url: str, ref: str, workdir: Path) -> Path:
    archive_url = github_archive_url(repo_url, ref)
    archive_path = workdir / "source.zip"
    info(f"downloading tutorial archive: {archive_url}")
    try:
        with urllib.request.urlopen(archive_url) as response:
            archive_path.write_bytes(response.read())
    except Exception as exc:  # noqa: BLE001 - present a concise CLI error.
        raise CommandError(f"failed to download {archive_url}: {exc}") from exc

    extract_dir = workdir / "source"
    extract_dir.mkdir()
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(extract_dir)

    roots = [path for path in extract_dir.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise CommandError(f"unexpected archive layout in {archive_path}")
    return roots[0]


def same_file(src: Path, dst: Path) -> bool:
    try:
        return dst.exists() and filecmp.cmp(src, dst, shallow=False)
    except OSError:
        return False


def copy_file(src: Path, dst: Path, *, overwrite: bool) -> str:
    if dst.exists():
        if same_file(src, dst):
            return "unchanged"
        if not overwrite:
            warn(f"keeping existing file: {dst}")
            return "kept"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return "copied"


def copy_tree(src: Path, dst: Path, *, overwrite: bool) -> dict[str, int]:
    counts = {"copied": 0, "unchanged": 0, "kept": 0}
    for current, dirs, files in os.walk(src):
        current_path = Path(current)
        rel_dir = current_path.relative_to(src)
        target_dir = dst / rel_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        for dirname in dirs:
            (target_dir / dirname).mkdir(exist_ok=True)
        for filename in files:
            status = copy_file(
                current_path / filename,
                target_dir / filename,
                overwrite=overwrite,
            )
            counts[status] += 1
    return counts


def deploy_files(source_root: Path, target: Path, *, overwrite: bool) -> None:
    target.mkdir(parents=True, exist_ok=True)
    total = {"copied": 0, "unchanged": 0, "kept": 0}
    for rel in DEPLOY_PATHS:
        src = source_root / rel
        dst = target / rel
        if not src.exists():
            warn(f"source path missing in archive: {rel}")
            continue
        if src.is_dir():
            counts = copy_tree(src, dst, overwrite=overwrite)
            info(f"deployed directory: {rel}")
        else:
            status = copy_file(src, dst, overwrite=overwrite)
            counts = {"copied": 0, "unchanged": 0, "kept": 0}
            counts[status] = 1
            info(f"deployed file: {rel}")
        for key, value in counts.items():
            total[key] += value
    info(
        "deployment summary: "
        f"{total['copied']} copied, "
        f"{total['unchanged']} unchanged, "
        f"{total['kept']} kept"
    )


def resolve_venv_path(target: Path, venv_arg: str) -> Path:
    expanded = Path(os.path.expandvars(venv_arg)).expanduser()
    if expanded.is_absolute():
        return expanded.resolve()
    return (target / expanded).resolve()


def install_environment(target: Path, *, python: str, venv: Path) -> None:
    uv = require_command("uv")
    if not (venv / "bin" / "python").exists():
        run([uv, "venv", "--python", python, str(venv)], cwd=target)
    run(
        [
            uv,
            "pip",
            "install",
            "--python",
            str(venv / "bin" / "python"),
            "--upgrade",
            "pip",
            "setuptools",
            "wheel",
        ],
        cwd=target,
        env={"UV_LINK_MODE": "copy"},
    )
    run(
        [
            uv,
            "pip",
            "install",
            "--python",
            str(venv / "bin" / "python"),
            "-r",
            str(target / "requirements.txt"),
        ],
        cwd=target,
        env={"UV_LINK_MODE": "copy"},
    )


def install_extensions() -> None:
    code = shutil.which("code")
    if not code:
        warn("'code' command not found; skipping VS Code extension install")
        return
    for extension in VSCODE_EXTENSIONS:
        run([code, "--install-extension", extension], check=False)


def open_workspace(target: Path) -> None:
    code = shutil.which("code")
    if not code:
        warn(f"'code' command not found. Open this folder manually: {target}")
        return
    run([code, "--reuse-window", str(target)], check=False)


def cmd_setup(args: argparse.Namespace) -> int:
    target = Path(args.target).expanduser().resolve()
    venv = resolve_venv_path(target, args.venv)
    with tempfile.TemporaryDirectory(prefix="emses-tutorials-setup-") as tmp:
        source_root = download_archive(args.repo_url, args.ref, Path(tmp))
        deploy_files(source_root, target, overwrite=args.overwrite)

    if not args.skip_install:
        install_environment(target, python=args.python, venv=venv)
    if not args.no_extensions:
        install_extensions()
    if args.open:
        open_workspace(target)

    print()
    print("EMSES tutorial setup is ready.")
    print(f"Workspace : {target}")
    print(f"Python env: {venv}")
    print()
    print("Next:")
    print(f"  cd {target}")
    print("  code --reuse-window .")
    print("  # VS Code Python extension will use .venv/bin/python")
    print("  mpiemses3D --version  # after installing MPIEMSES3D in .venv")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="emses-tutorials")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup = subparsers.add_parser("setup", help="expand tutorial files")
    setup.add_argument("target", help="target workspace directory")
    setup.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    setup.add_argument("--ref", default=DEFAULT_REF, help="GitHub branch, tag, or SHA")
    setup.add_argument("--python", default=DEFAULT_PYTHON)
    setup.add_argument("--venv", default=DEFAULT_VENV)
    setup.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing tutorial files in the target directory",
    )
    setup.add_argument("--skip-install", action="store_true")
    setup.add_argument("--no-extensions", action="store_true")
    setup.add_argument("--open", action="store_true", help="open the workspace in VS Code")
    setup.set_defaults(func=cmd_setup)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except CommandError as exc:
        fail(str(exc))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
