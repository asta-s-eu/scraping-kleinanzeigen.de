"""
Testing irequests module
"""
from unittest import mock

with mock.patch.dict('os.environ', {
    'ADA_EMAIL_FROM': 'some-value',
    'ADA_EMAIL_PASSWORD': 'some-value'

}):
    from asta_s_eu.scraping.kleinanzeigen_de import irequests


def test_http_get_request() -> None:
    """
    GIVEN library similar to requests
    WHEN call example.org
    THEN get the page
    """

    web = irequests.session()
    response = web.get("https://example.org")

    assert response.status_code == 200
