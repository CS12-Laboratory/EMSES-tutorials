from __future__ import annotations

import argparse
import filecmp
import fnmatch
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

from . import __version__


DEFAULT_REPO_URL = "https://github.com/CS12-Laboratory/EMSES-tutorials.git"
DEFAULT_REF = "main"
DEFAULT_PYTHON = "/usr/bin/python3.12"
DEFAULT_VENV = ".venv"

# Participant-facing setup is intentionally allowlisted. Maintainer-only files
# such as .github/, site/, src/, pyproject.toml, and AGENTS.md are not expanded.
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
MAINTAINER_ONLY_PATHS = [
    ".github",
    "AGENTS.md",
    "pyproject.toml",
    "site",
    "src",
]
SAFE_REPAIR_PATTERNS = [
    ".gitignore",
    ".mypython/*.py",
    ".vscode/*.json",
    "LICENSE",
    "README.md",
    "README_en.md",
    "docs/*.md",
    "imgs/*",
    "requirements.txt",
    "dshield*/.logs",
    "dshield*/job.sh",
    "dshield*/tutorial_*.xlsx",
]
PARAMETER_REPAIR_PATTERNS = [
    "dshield*/plasma.toml",
    "dshield*/.old/*.inp",
    "dshield*/.old/*.preinp",
]
NOTEBOOK_REPAIR_PATTERNS = [
    "dshield*/plot_example.ipynb",
]
REQUIRED_WORKSPACE_PATHS = [
    ".vscode/settings.json",
    ".mypython/plot.py",
    "requirements.txt",
    "docs/QuickStart.md",
    "dshield0/job.sh",
    "dshield0/plasma.toml",
    "dshield1/job.sh",
    "dshield1/plasma.toml",
    "dshield2/job.sh",
    "dshield2/plasma.toml",
]
REQUIRED_PYTHON_MODULES = ["numpy", "emout"]
SETUP_COMMANDS = ["mysbatch", "latestjob"]
MPIEMSES_COMMANDS = ["emu", "mpiemses3D"]
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
    capture: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    if not capture:
        prefix = f"(cd {cwd} && " if cwd else ""
        suffix = ")" if cwd else ""
        info(f"$ {prefix}{' '.join(cmd)}{suffix}")

    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=run_env,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=False,
    )
    if check and result.returncode != 0:
        if capture:
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
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


def resolve_workspace(path: str | Path | None) -> Path:
    return Path(path or ".").expanduser().resolve()


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


def uvx_source(repo_url: str, ref: str) -> str:
    source = repo_url if repo_url.startswith("git+") else f"git+{repo_url}"
    if "@" not in source.rsplit("/", 1)[-1]:
        source = f"{source}@{ref}"
    return source


def emses_uvx_command(repo_url: str, ref: str) -> str:
    uvx = find_command("uvx") or "uvx"
    return f'{uvx} --no-cache --from "{uvx_source(repo_url, ref)}" emses-tutorials'


def source_files(source_root: Path) -> list[str]:
    files: list[str] = []
    for current, _, filenames in os.walk(source_root):
        current_path = Path(current)
        for filename in filenames:
            rel = (current_path / filename).relative_to(source_root).as_posix()
            files.append(rel)
    return sorted(files)


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def managed_repair_files(
    source_root: Path,
    *,
    include_parameters: bool,
    include_notebooks: bool,
) -> list[str]:
    patterns = list(SAFE_REPAIR_PATTERNS)
    if include_parameters:
        patterns += PARAMETER_REPAIR_PATTERNS
    if include_notebooks:
        patterns += NOTEBOOK_REPAIR_PATTERNS
    return [
        path
        for path in source_files(source_root)
        if matches_any(path, patterns)
        and not any(path == item or path.startswith(f"{item}/") for item in MAINTAINER_ONLY_PATHS)
    ]


def backup_changed_files(source_root: Path, target: Path, paths: list[str]) -> Path | None:
    changed = [
        rel
        for rel in paths
        if (target / rel).exists() and not same_file(source_root / rel, target / rel)
    ]
    if not changed:
        return None

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = target / ".emses-tutorials" / "backups" / f"repair-{stamp}"
    for rel in changed:
        src = target / rel
        dst = backup_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    info(f"backed up {len(changed)} changed files to {backup_dir}")
    return backup_dir


def repair_workspace(
    source_root: Path,
    target: Path,
    *,
    include_parameters: bool,
    include_notebooks: bool,
    dry_run: bool,
) -> None:
    paths = managed_repair_files(
        source_root,
        include_parameters=include_parameters,
        include_notebooks=include_notebooks,
    )
    if not paths:
        raise CommandError("no managed files found in the source archive")

    info(f"managed files selected for repair: {len(paths)}")
    if dry_run:
        for path in paths:
            print(path)
        return

    backup_changed_files(source_root, target, paths)
    counts = {"copied": 0, "unchanged": 0, "kept": 0}
    for rel in paths:
        status = copy_file(source_root / rel, target / rel, overwrite=True)
        counts[status] += 1
    info(
        "repair summary: "
        f"{counts['copied']} copied, "
        f"{counts['unchanged']} unchanged"
    )


def check_python_import(venv_python: Path, module: str) -> bool:
    result = run(
        [
            str(venv_python),
            "-c",
            (
                "import importlib.util, sys; "
                f"sys.exit(0 if importlib.util.find_spec({module!r}) else 1)"
            ),
        ],
        check=False,
        capture=True,
    )
    if result.returncode == 0:
        info(f"python import ok: {module}")
        return True
    warn(f"python import failed: {module}")
    return False


def check_executable(path: Path, *, optional: bool) -> bool:
    if path.exists() and os.access(path, os.X_OK):
        info(f"command ok: {path}")
        return True
    message = f"command not found in venv: {path}"
    if optional:
        warn(f"{message} (install MPIEMSES3D if you have not yet done so)")
        return False
    warn(message)
    return False


def doctor_workspace(target: Path, *, venv: Path, strict: bool) -> int:
    failures = 0
    warnings = 0

    def issue(message: str) -> None:
        nonlocal failures
        warn(message)
        failures += 1

    def soft_warn(message: str) -> None:
        nonlocal warnings
        warn(message)
        warnings += 1

    info(f"workspace: {target}")
    if not target.exists():
        issue(f"workspace does not exist: {target}")
        return 1

    for rel in REQUIRED_WORKSPACE_PATHS:
        if (target / rel).exists():
            info(f"found: {rel}")
        else:
            issue(f"missing: {rel}")

    for rel in MAINTAINER_ONLY_PATHS:
        if (target / rel).exists():
            soft_warn(f"maintainer-only path is present in this workspace: {rel}")

    settings = target / ".vscode" / "settings.json"
    if settings.exists():
        text = settings.read_text(encoding="utf-8", errors="replace")
        if "${workspaceFolder}/.venv/bin/python" in text:
            info("VS Code interpreter points to ${workspaceFolder}/.venv/bin/python")
        else:
            soft_warn("VS Code interpreter setting does not point to .venv/bin/python")

    for command in ["git", "uv"]:
        path = find_command(command)
        if path:
            info(f"{command}: {path}")
        else:
            issue(f"required command not found: {command}")

    venv_python = venv / "bin" / "python"
    if not venv_python.exists():
        issue(f"missing venv python: {venv_python}")
    else:
        result = run([str(venv_python), "-V"], capture=True, check=False)
        info(result.stdout.strip() or result.stderr.strip())
        for module in REQUIRED_PYTHON_MODULES:
            if not check_python_import(venv_python, module):
                failures += 1
        for command in SETUP_COMMANDS:
            if not check_executable(venv / "bin" / command, optional=False):
                failures += 1
        for command in MPIEMSES_COMMANDS:
            if not check_executable(venv / "bin" / command, optional=True):
                warnings += 1

    if failures:
        warn(f"doctor found {failures} setup issue(s)")
    if warnings:
        warn(f"doctor found {warnings} warning(s)")

    if failures or (strict and warnings):
        return 1
    return 0


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
    print(f"  {emses_uvx_command(args.repo_url, args.ref)} doctor .")
    print("  mpiemses3D --version  # after installing MPIEMSES3D in .venv")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    target = resolve_workspace(args.target)
    venv = resolve_venv_path(target, args.venv)
    return doctor_workspace(target, venv=venv, strict=args.strict)


def cmd_repair(args: argparse.Namespace) -> int:
    target = resolve_workspace(args.target)
    venv = resolve_venv_path(target, args.venv)
    with tempfile.TemporaryDirectory(prefix="emses-tutorials-repair-") as tmp:
        source_root = download_archive(args.repo_url, args.ref, Path(tmp))
        repair_workspace(
            source_root,
            target,
            include_parameters=args.include_parameters,
            include_notebooks=args.include_notebooks,
            dry_run=args.dry_run,
        )

    if args.dry_run:
        return 0
    if not args.skip_install:
        install_environment(target, python=args.python, venv=venv)
    return doctor_workspace(target, venv=venv, strict=args.strict)


def add_workspace_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="tutorial workspace directory (default: current directory)",
    )


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

    doctor = subparsers.add_parser("doctor", help="diagnose an existing workspace")
    add_workspace_argument(doctor)
    doctor.add_argument("--venv", default=DEFAULT_VENV)
    doctor.add_argument("--strict", action="store_true", help="fail on warnings")
    doctor.set_defaults(func=cmd_doctor)

    repair = subparsers.add_parser("repair", help="restore managed tutorial files")
    add_workspace_argument(repair)
    repair.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    repair.add_argument("--ref", default=DEFAULT_REF, help="GitHub branch, tag, or SHA")
    repair.add_argument("--python", default=DEFAULT_PYTHON)
    repair.add_argument("--venv", default=DEFAULT_VENV)
    repair.add_argument(
        "--include-parameters",
        action="store_true",
        help="also repair plasma.toml and archived legacy input files",
    )
    repair.add_argument(
        "--include-notebooks",
        action="store_true",
        help="also repair plot_example.ipynb files",
    )
    repair.add_argument("--skip-install", action="store_true")
    repair.add_argument("--dry-run", action="store_true")
    repair.add_argument("--strict", action="store_true", help="fail on doctor warnings")
    repair.set_defaults(func=cmd_repair)
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
