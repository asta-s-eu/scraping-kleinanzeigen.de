"""
Initiate constants
"""
import os
from pathlib import Path

from asta_s_eu.scraping.core.log import get_loggers

_, ALARM_LOG = get_loggers(Path(__file__), Path(__file__).parent / 'logging.yaml')

EMAIL_NOTIFICATION_FROM = os.getenv("EMAIL_NOTIFICATION_FROM")
assert EMAIL_NOTIFICATION_FROM

EMAIL_NOTIFICATION_PASSWORD = os.getenv("EMAIL_NOTIFICATION_PASSWORD")
assert EMAIL_NOTIFICATION_PASSWORD

EMAIL_NOTIFICATION_TO = os.getenv("EMAIL_NOTIFICATION_TO") or ''
WEB_SITE = "kleinanzeigen.de"
