import json
import sys
from pathlib import Path

from .models import AppConfig, SMTPConfig, EmailConfig, FolderConfig


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    return Path(__file__).resolve().parent.parent


def load_config() -> AppConfig:
    config_path = app_dir() / "config.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return parse_config(data)

def parse_config(data: dict) -> AppConfig:
    try:
        smtp = data["smtp"]
        emails = data["emails"]
        folders = data["folders"]
        keywords = data["keywords"]

        if not isinstance(keywords, list) or not keywords:
            raise ValueError("keywords must be a non-empty list")

        return AppConfig(
            desktop=_require_str(data, "desktop"),
            company_name=_require_str(data, "company_name"),
            nif=_require_str(data, "nif"),

            smtp=SMTPConfig(
                host=_require_str(smtp, "host", "smtp"),
                port=_require_int(smtp, "port", "smtp"),
                username=_require_str(smtp, "username", "smtp"),
                password=_require_str(smtp, "password", "smtp"),
                use_tls=_require_bool(smtp, "use_tls", "smtp"),
            ),

            emails=EmailConfig(
                to=_require_list(emails, "to", "emails"),
                cc=emails.get("cc", []),
                bcc=emails.get("bcc", []),
            ),

            folders=FolderConfig(
                root_path=_require_str(folders, "root_path", "folders"),
                efactura=_require_str(folders, "efactura", "folders"),
                mapa=_require_str(folders, "mapa", "folders"),
                saft=_require_str(folders, "saft", "folders"),
            ),

            keywords=keywords,
        )

    except KeyError as e:
        raise ValueError(f"Missing config key: {e}")


def _require_str(data: dict, key: str, section="root") -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Invalid or missing '{section}.{key}'")
    return value


def _require_int(data: dict, key: str, section="root") -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"Invalid or missing '{section}.{key}'")
    return value


def _require_bool(data: dict, key: str, section="root") -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"Invalid or missing '{section}.{key}'")
    return value


def _require_list(data: dict, key: str, section="root") -> list[str]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ValueError(f"Invalid or missing '{section}.{key}' (must be list[str])")
    return value