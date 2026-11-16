"""Create a portable source archive using an explicit allowlist, never personal files."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent
FILES = ["README.md", "USER_GUIDE.md", "METHODOLOGY.md", "SOURCES.md", "AI_PROMPTS.md",
         "CONTRIBUTIONS.md", "DEMO_RUNBOOK.md", "VALIDATION.md", "requirements.txt",
         "vercel.json", ".python-version", ".vercelignore", "LICENSE", "app.py", "engine.py", "generate_data.py", "prepare_submission.py", ".gitignore"]
DIRECTORIES = ["api", "static", "data", "tests", "docs/prompts", "docs/screenshots"]


def main():
    paths = [ROOT / name for name in FILES]
    for directory in DIRECTORIES:
        paths.extend(path for path in (ROOT / directory).rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts and path.name != ".DS_Store")
    for path in paths:
        if not path.is_file():
            raise SystemExit(f"Missing required deliverable: {path.relative_to(ROOT)}")
    destination = ROOT / "submission" / "BLACKSITE.zip"
    destination.parent.mkdir(exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            entry = ZipInfo("BLACKSITE/" + path.relative_to(ROOT).as_posix(), date_time=(2026, 11, 16, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, path.read_bytes())
    print(f"Created {destination.relative_to(ROOT)} with {len(paths)} files ({destination.stat().st_size:,} bytes).")
    print("Dependencies and video are not included. Complete contributions and rebuild before submission.")


if __name__ == "__main__":
    main()
