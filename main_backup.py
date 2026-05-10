from pathlib import Path
from datetime import datetime
import re
import sys
import win32com.client as win32

# Configuration
# Todo: implement this using config file
DESKTOP = Path(r"C:\Users\cunha\Desktop")
ROOT_PATH = Path(r"C:\Users\cunha\Medicalis\Documents\Facturacao")

TO = "riemcontabilidade@gmail.com"
CC = "jmacl33@hotmail.com"
BCC = "cunha.barbosa@hotmail.com"
COMPANY_NAME = "Clínica de Medicina e Dentária Dr. Campos Lopes"


# Helper functions to validate config.json
def require(config: dict, key: str, expected_type, parent="root"):
    if key not in config:
        raise ValueError(f"Missing key '{key}' in '{parent}'")

    value = config[key]

    if not isinstance(value, expected_type):
        raise TypeError(
            f"Invalid type for '{parent}.{key}': expected {expected_type.__name__}, got {type(value).__name__}"
        )

    if isinstance(value, str) and not value.strip():
        raise ValueError(f"Empty value for '{parent}.{key}'")

    return value


def require_list(config: dict, key: str, parent="root"):
    value = require(config, key, list, parent)

    for i, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"Invalid email at {parent}.{key}[{i}]")

    return value


# Validate config.json
def validate_config(config: dict) -> dict:
    # Desktop
    desktop = require(config, "desktop", str)

    # SMTP
    smtp = require(config, "smtp", dict)
    smtp_host = require(smtp, "host", str, "smtp")
    smtp_port = require(smtp, "port", int, "smtp")
    smtp_user = require(smtp, "username", str, "smtp")
    smtp_pass = require(smtp, "password", str, "smtp")
    smtp_tls = require(smtp, "use_tls", bool, "smtp")

    # Emails
    emails = require(config, "emails", dict)
    to = require_list(emails, "to", "emails")
    cc = emails.get("cc", [])
    bcc = emails.get("bcc", [])

    # Validate optional lists if present
    if cc:
        if not isinstance(cc, list):
            raise TypeError("emails.cc must be a list")
    if bcc:
        if not isinstance(bcc, list):
            raise TypeError("emails.bcc must be a list")

    # Company
    company_name = require(config, "company_name", str)
    nif = require(config, "nif", str)

    # Folders
    folders = require(config, "folders", dict)
    root_path = require(folders, "root_path", str, "folders")
    efactura = require(folders, "efactura", str, "folders")
    mapa = require(folders, "mapa", str, "folders")
    saft = require(folders, "saft", str, "folders")

    return {
        "desktop": desktop,
        "smtp": {
            "host": smtp_host,
            "port": smtp_port,
            "username": smtp_user,
            "password": smtp_pass,
            "use_tls": smtp_tls,
        },
        "emails": {
            "to": to,
            "cc": cc,
            "bcc": bcc,
        },
        "company_name": company_name,
        "nif": nif,
        "folders": {
            "root_path": root_path,
            "efactura": efactura,
            "mapa": mapa,
            "saft": saft,
        },
    }


# DONE
def detect_period(folder: Path) -> str:
    """
    Automatically detects the period from filenames.
    Example: 2026-04 Porto.pdf -> 2026-04
    """
    periods = []

    for file in folder.iterdir():
        match = re.match(r"(\d{4}-\d{2})", file.name)
        if match:
            periods.append(match.group(1))

    if not periods:
        raise RuntimeError("No files found with format YYYY-MM")

    return sorted(periods)[-1]


def get_attachments(folder: Path, period: str) -> list[Path]:
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

# DONE
def validate_attachments(attachments: list[Path], period: str) -> None:
    expected = {
        f"{period} Porto.pdf",
        f"{period} Porto.xml",
        f"{period} S J Madeira.pdf",
        f"{period} S J Madeira.xml",
        f"{period}.pdf",
    }

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


# DONE
def get_greeting() -> str:
    hour = datetime.now().hour

    if hour < 12:
        return "Bom dia"

    return "Boa tarde"

# DONE
def create_email(period: str, attachments: list[Path]) -> None:
    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)

    greeting = get_greeting()

    mail.To = TO
    mail.CC = CC
    mail.BCC = BCC
    mail.Subject = f"SAFT-PT {period} da {COMPANY_NAME}"

    mail.Body = f"""{greeting},

Segue em anexo o SAFT-PT referente a {period} da {COMPANY_NAME}.

Cumprimentos,
António Barbosa
"""

    for file in attachments:
        mail.Attachments.Add(str(file))

    mail.Display()   # Opens email for review
    # mail.Send()    # Sends immediately

# DONE
def ask_yes_no(question: str) -> bool:
    answer = input(f"{question} (y/n): ").strip().lower()
    return answer in ["y", "yes"]

# DONE
def get_period_year(period: str) -> str:
    # period example: 2026-04
    return period.split("-")[0]

# DONE
def get_destination_folder(file: Path, period: str, root_path: Path) -> Path:
    year = get_period_year(period)
    name = file.name.lower()

    if file.name == f"{period}.pdf":
        return root_path / "e-factura comprovativos" / year

    if file.suffix.lower() == ".pdf" and ("porto" in name or "s j madeira" in name):
        return root_path / "Mapa recapitulativo (mensal)" / year

    if file.suffix.lower() == ".xml" and ("porto" in name or "s j madeira" in name):
        return root_path / "SAFT-PT" / year

    raise RuntimeError(f"No destination rule defined for file: {file.name}")

# DONE
def move_files_after_send(attachments: list[Path], period: str, root_path: Path) -> None:
    for file in attachments:
        destination_folder = get_destination_folder(file, period, root_path)
        destination_folder.mkdir(parents=True, exist_ok=True)

        destination_file = destination_folder / file.name

        if destination_file.exists():
            raise RuntimeError(f"Destination file already exists: {destination_file}")

        # shutil.move(str(file), str(destination_file))

        print(f"Saved: {file.name}")
        print(f"   -> {destination_file}")


def main() -> None:
    try:
        period = detect_period(DESKTOP)
        attachments = get_attachments(DESKTOP, period)

        if not attachments:
            raise RuntimeError(f"No attachments found for {period}")

        validate_attachments(attachments, period)

        create_email(period, attachments)

        if ask_yes_no("After sending the email, move the files now?"):
            move_files_after_send(
                attachments=attachments,
                period=period,
                root_path=ROOT_PATH
            )
            print("\nFiles moved successfully.")
        else:
            print("\nFiles were not moved.")

        input("\nPress ENTER to exit...")

    except RuntimeError as e:
        print(f"❌ Error: {e}")
        input("\nPress ENTER to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()