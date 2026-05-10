from pathlib import Path

from src.config import load_config
from src.file_manager import find_attachments, validate_attachments, move_files_after_send
from src.outlook_sender import create_email
from src.period import detect_period
from src.utils import ask_yes_no
from src.version import __version__, __build_date__


def main():
    try:
        print(f"SAFT-PT Automation v{__version__} ({__build_date__})")
        config = load_config()

        folder = Path(config.desktop)
        period = detect_period(folder)

        print(f"\nDetected period: {period}")

        attachments = find_attachments(config, period)
        if not attachments:
            print(f"\nNo files found to send for period {period}.")
            return

        validate_attachments(config, attachments, period)

        create_email(config, attachments, period)

        if not ask_yes_no("After sending the email, move the files now?"):
            print("\nFiles were not moved!!!")

        move_files_after_send(config, attachments, period)
        print("\nFiles moved successfully!")

    except Exception as error:
        print(f"\nError: {error}")

    finally:
        input("\nPress ENTER to exit...")


if __name__ == "__main__":
    main()
