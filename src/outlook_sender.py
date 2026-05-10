import win32com.client
from pathlib import Path
from datetime import datetime

from .models import AppConfig


def create_email(config: AppConfig, attachments: list[Path], period: str) -> None:
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)

    mail.To = "; ".join(config.emails.to)
    mail.CC = "; ".join(config.emails.cc)
    mail.BCC = "; ".join(config.emails.bcc)

    mail.Subject = build_subject(config, period)
    mail.Body = build_body(config, period)

    for attachment in attachments:
        mail.Attachments.Add(str(attachment))

    mail.Display()   # Opens email for review
    # mail.Send()    # Sends immediately


def build_subject(config: AppConfig, period: str) -> str:
    return f"SAFT-PT {period} da {config.company_name}"


def get_greeting() -> str:
    hour = datetime.now().hour

    if hour < 12:
        return "Bom dia"

    return "Boa tarde"


def build_body(config: AppConfig, period: str) -> str:
    greeting = get_greeting()
    return f"""{greeting},

Segue em anexo o SAFT-PT referente a {period} da {config.company_name}.

Cumprimentos,
António Barbosa
"""
