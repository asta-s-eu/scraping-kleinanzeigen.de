"""
Initiate constants
"""
import os
from pathlib import Path

from asta_s_eu.scraping.core.log import get_loggers

_, ALARM_LOG = get_loggers(Path(__file__), Path(__file__).parent / 'logging.yaml')

EMAIL_FROM = os.getenv("ADA_EMAIL_FROM")
assert EMAIL_FROM

EMAIL_PASSWORD = os.getenv("ADA_EMAIL_PASSWORD")
assert EMAIL_PASSWORD

EMAIL_TO = os.getenv("ADA_EMAIL_TO") or ''
WEB_SITE = "kleinanzeigen.de"
