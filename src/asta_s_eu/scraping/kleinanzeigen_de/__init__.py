"""
Initiate constants
"""
import os
from pathlib import Path

from asta_s_eu.scraping.core.log import get_loggers

_, ALARM_LOG = get_loggers(Path(__file__), Path(__file__).parent / 'logging.yaml')

GMAIL_USER = os.getenv("ADA_GMAIL_USER")
assert GMAIL_USER

GMAIL_PASSWORD = os.getenv("ADA_GMAIL_PASSWORD")
assert GMAIL_PASSWORD

GMAIL_TO = os.getenv("ADA_GMAIL_TO") or ''
WEB_SITE = "kleinanzeigen.de"
