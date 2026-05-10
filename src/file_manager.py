from pathlib import Path

from .models import AppConfig
from .period import get_period_year

def find_attachments(config: AppConfig, period: str) -> list[Path]:
    folder = Path(config.desktop)

    return sorted(
        (
            file for file in folder.iterdir()
            if (
                file.is_file()
                and file.name.startswith(period)
                and file.suffix.lower() in [".pdf", ".xml"]
                and file.stat().st_size > 0
                and "multidocumento" not in file.name.lower()
            )
        ),
        key=lambda f: f.name.lower()
    )

def validate_attachments(config: AppConfig, attachments: list[Path], period: str) -> None:
    keywords = config.keywords

    expected = {f"{period}.pdf"}

    for keyword in keywords:
        expected.add(f"{period} {keyword.title()}.pdf")
        expected.add(f"{period} {keyword.title()}.xml")

    found = {file.name for file in attachments}

    missing = expected - found
    extra = found - expected

    if missing:
        print("⚠️ Missing files:")
        for file in sorted(missing):
            print(f" - {file}")
        raise RuntimeError("Missing required SAFT files")

    if extra:
        print("ℹ️ Extra files detected:")
        for file in sorted(extra):
            print(f" - {file}")

    if not missing:
        print("✅ All expected files are present")

def get_destination_folder(config: AppConfig, file: Path, period: str) -> Path:
    year = get_period_year(period)
    name = file.name.lower()
    root = Path(config.folders.root_path)

    has_keyword = any(keyword.lower() in name for keyword in config.keywords)

    if file.name.lower() == f"{period}.pdf":
        return root / config.folders.efactura / year

    if file.suffix.lower() == ".pdf" and has_keyword:
        return root / config.folders.mapa / year

    if file.suffix.lower() == ".xml" and has_keyword:
        return root / config.folders.saft / year

    raise RuntimeError(f"No destination rule defined for file: {file.name}")


def move_files_after_send(config: AppConfig, attachments: list[Path], period: str) -> None:
    moves = []
    for file in attachments:
        destination_folder  = get_destination_folder(config, file, period)
        destination_folder .mkdir(parents=True, exist_ok=True)

        destination_file = destination_folder / file.name

        # TODO: Delete this comment after debug
        #if destination_file.exists():
            # raise RuntimeError(f"Destination file already exists: {destination_file}")

        # shutil.move(str(file), str(destination_file))

        moves.append((file.name, str(destination_file)))

    print_table(moves)


def print_table(moves: list[tuple[str, str]]) -> None:
    col1_width = max(len(src) for src, _ in moves)
    col2_width = max(len(dst) for _, dst in moves)

    print("\nFiles moved:")
    print(f"{'FILE'.ljust(col1_width)}   {'DESTINATION'}")
    print(f"{'-' * col1_width}   {'-' * col2_width}")

    for src, dst in moves:
        print(f"{src.ljust(col1_width)}   {dst}")