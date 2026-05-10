from dataclasses import dataclass


@dataclass
class SMTPConfig:
    host: str
    port: int
    username: str
    password: str
    use_tls: bool


@dataclass
class EmailConfig:
    to: list[str]
    cc: list[str]
    bcc: list[str]


@dataclass
class FolderConfig:
    root_path: str
    efactura: str
    mapa: str
    saft: str


@dataclass
class AppConfig:
    desktop: str
    smtp: SMTPConfig
    emails: EmailConfig
    company_name: str
    nif: str
    folders: FolderConfig
    keywords: list[str]
