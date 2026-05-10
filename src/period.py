from pathlib import Path
import re


PERIOD_PATTERN = re.compile(r"^(\d{4})-(\d{2})")


def detect_period(folder: Path) -> str:
    """
    Detects the latest valid period from filenames.
    Example: 2026-04 Porto.pdf -> 2026-04
    """

    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")

    if not folder.is_dir():
        raise NotADirectoryError(f"Path is not a folder: {folder}")

    periods: set[str] = set()

    for file in folder.iterdir():
        if not file.is_file():
            continue

        match = PERIOD_PATTERN.match(file.name)

        if not match:
            continue

        year, month = match.groups()
        month_int = int(month)

        if month_int < 1 or month_int > 12:
            continue

        periods.add(f"{year}-{month}")

    if not periods:
        raise RuntimeError(f"No valid files found with format YYYY-MM in folder {folder}")

    if len(periods) > 1:
        print(f"⚠️ Multiple periods detected: {', '.join(sorted(periods))}")
        print(f"Using latest period: {max(periods)}")

    return max(periods)


def get_period_year(period: str) -> str:
    if not PERIOD_PATTERN.match(period):
        raise ValueError(f"Invalid period format: {period}")

    return period[:4]
