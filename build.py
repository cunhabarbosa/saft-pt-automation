from datetime import datetime
from pathlib import Path
import shutil
import subprocess


APP_NAME = "saft-pt-automation"
VERSION = "1.0.0"

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
RELEASE = ROOT / "release"
RELEASE_DIR = RELEASE / f"{APP_NAME}-v{VERSION}-windows"
ZIP_PATH = RELEASE / f"{APP_NAME}-v{VERSION}-windows.zip"


def write_version_file() -> None:
    version_file = ROOT / "src" / "version.py"

    build_date = datetime.now().strftime("%Y-%m-%d")

    version_file.write_text(
        f'__version__ = "{VERSION}"\n'
        f'__build_date__ = "{build_date}"\n',
        encoding="utf-8",
    )


def build_exe() -> None:
    subprocess.run(
        [
            "pyinstaller",
            "--onefile",
            "--name",
            APP_NAME,
            "main.py",
        ],
        check=True,
    )


def prepare_release_folder() -> None:
    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)

    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    exe_file = DIST / f"{APP_NAME}.exe"

    shutil.copy2(exe_file, RELEASE_DIR / exe_file.name)
    shutil.copy2(ROOT / "config.example.json", RELEASE_DIR / "config.example.json")
    shutil.copy2(ROOT / "README.md", RELEASE_DIR / "README.md")


def create_zip() -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    shutil.make_archive(
        base_name=str(ZIP_PATH.with_suffix("")),
        format="zip",
        root_dir=RELEASE,
        base_dir=RELEASE_DIR.name,
    )


def main() -> None:
    write_version_file()
    build_exe()
    prepare_release_folder()
    create_zip()

    print("\nBuild completed successfully.")
    print(f"Release ZIP: {ZIP_PATH}")


if __name__ == "__main__":
    main()