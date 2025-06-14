"""
test configurations
"""

from unittest import mock

from asta_s_eu.scraping import core

mock.patch.object(
        core,
        core.catch_alarms.__qualname__,
        return_value=lambda x: x
).start()
