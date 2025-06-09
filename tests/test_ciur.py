"""
Testing ciur module
"""
from typing import Iterable

import datetime
import logging
from pathlib import Path
from unittest import mock

import pytest
import retry.api
from _pytest.capture import CaptureFixture
from ciur.exceptions import CiurBaseException

with mock.patch.dict('os.environ', {
    'ADA_GMAIL_USER': 'some-value',
    'ADA_GMAIL_PASSWORD': 'some-value'

}):
    import asta_s_eu.scraping.kleinanzeigen_de
    import asta_s_eu.scraping.kleinanzeigen_de.ciur

from asta_s_eu.scraping.core.prospect_database import Prospect

MY_EBAY_K_ID = 79809801
KIDS_EBAY_K_ID = 88403630
EBAY_K_URL = "https://www.kleinanzeigen.de/s-bestandsliste.html?userId={id}"


def test_parse_page_with_different_dates():
    """
    GIVEN a single page with prospects
    WHEN parse the page
    THEN get three prospects with a today's, yesterday's and other date
    """
    url = mock.Mock()
    web = mock.Mock()
    web.get.return_value = mock.Mock(status_code=200, text='some-text')

    with mock.patch.object(
            asta_s_eu.scraping.kleinanzeigen_de.ciur.ciur.parse, 'html_type'
    ) as html_type:

        html_type.return_value = {
            'body': {
                'prospect_list': [
                    {
                        'date': 'other-date',
                    },
                    {
                        'date': 'Heute, some-time',
                    },
                    {
                        'date': 'Gestern, some-date',
                    }
                ]
            }
        }
        data = asta_s_eu.scraping.kleinanzeigen_de.ciur.parse_page(
            url=url,
            web=web
        )

    assert data == {
        'prospect_list': [
            {'date': 'other-date'},
            {'date': datetime.datetime.now(datetime.UTC).strftime('%d.%m.%Y')},
            {
                'date': (
                    datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)
                ).strftime('%d.%m.%Y')
            }
        ]
    }


@pytest.mark.parametrize('test_exception_name, expect_exception', (
        ('InvalidHtml', pytest.raises(asta_s_eu.scraping.kleinanzeigen_de.ciur.InvalidHtml)),
        ('ciur.parse.html_type', pytest.raises(CiurBaseException))
))
def test_parse_page_with_exceptions(test_exception_name, expect_exception):
    """
    GIVEN a single page with prospects
    WHEN parse the page
    THEN get different expected exceptions
    """
    url = mock.Mock()
    web = mock.Mock()
    if test_exception_name == 'InvalidHtml':
        web_text = asta_s_eu.scraping.kleinanzeigen_de.ciur.InvalidHtml.__doc__
    else:
        web_text = 'some_text'

    web.get.return_value = mock.Mock(status_code=200, text=web_text, content=b'some_content')

    def _do_not_retry(function, *_, **__):
        return function()

    # use your decorated method
    if test_exception_name == 'ciur.parse.html_type':
        html_type_side_effect = CiurBaseException(b'something')
    else:
        html_type_side_effect = None

    with \
            mock.patch.object(
                asta_s_eu.scraping.kleinanzeigen_de.ciur.ciur.parse,
                'html_type',
                side_effect=html_type_side_effect
            ), mock.patch.object(
                retry.api,
                '__retry_internal',
                _do_not_retry
            ):

        with expect_exception:
            asta_s_eu.scraping.kleinanzeigen_de.ciur.parse_page(
                url=url,
                web=web
            )


@pytest.mark.integration
def test_parse_search_page(my_sample_ebay_prospect):
    """
    GIVEN a search term 'kleiner bluetooth lautsprecher' in '13507 Reinickendorf 20km'
    WHEN search and extract the data
    THEN check if extracted data has the title from our test sample
    """
    data = asta_s_eu.scraping.kleinanzeigen_de.ciur.parse_page(
        url="https://www.kleinanzeigen.de/s-13507/kleiner-bluetooth-lautsprecher-klarna/k0l3453r20"
    )

    assert data['has_next_page'] is False

    my_sample_ebay_prospect.location = '13507 Reinickendorf (0.0 km)'
    prospect_titles = {prospect["text"] for prospect in data["prospect_list"]}
    assert my_sample_ebay_prospect.text in prospect_titles


def _test_prospects_for_updates(prospects: Iterable[Prospect], k_id: int):
    """
    GIVEN a concrete user
    WHEN parse prospects of the user
    THEN check if extracted data match 1:1 expected values
    """
    data = asta_s_eu.scraping.kleinanzeigen_de.ciur.parse_page(
        url=EBAY_K_URL.format(id=k_id)
    )
    dump_path = Path(__file__).parent / f'conftest_{k_id}.py'

    data = {
        'prospect_titles': Prospect.print_from_prospect_list(
            [Prospect(i) for i in data["prospect_list"]], dump_path=dump_path
         ),
        'has_next_page': data['has_next_page']
    }
    expect = {
        'prospect_titles': Prospect.print_from_prospect_list(prospects),
        'has_next_page': False
    }

    assert data == expect

    dump_path.unlink()


@pytest.mark.integration
def test_kinder_prospects_for_updates(kinder_prospects: Iterable[Prospect]):
    """
    Check kinder prospects
    """
    _test_prospects_for_updates(kinder_prospects, KIDS_EBAY_K_ID)


@pytest.mark.integration
def test_g_prospects_for_updates(g_prospects: Iterable[Prospect]):
    """
    Check ada prospects
    """
    _test_prospects_for_updates(g_prospects, MY_EBAY_K_ID)

@pytest.mark.skip('temporary disable')
def test_config():
    """
    GIVEN a config which has a dynamic builds parts
    WHEN generate final config
    THEN check if the config expect final parts
    """
    the_config = asta_s_eu.scraping.kleinanzeigen_de.ciur.SEARCH
    expect = {
        ('Schlieperstr 12', 'https://www.kleinanzeigen.de/s-13507/l3453r1'),

        ('13507 one plus 3',
         'https://www.kleinanzeigen.de/s-13507/one-plus-3/k0l3453r5'),
        ('masa pentru bucatarie',
         'https://www.kleinanzeigen.de/s-kueche-esszimmer/13507/preis::150/esstisch/k0c86l3453'),
        ('13507 Zwillinge 5km',
         'https://www.kleinanzeigen.de/s-13507/zwillinge/k0l3453r5'),
        ('13507 Twin 5km', 'https://www.kleinanzeigen.de/s-13507/twin/k0l3453r5'),

        ('tegel',
         'https://www.kleinanzeigen.de/s-wohnung-mieten/13507/anzeige:angebote/preis::2500/c203l3453r5+wohnung_mieten.qm_d:90%2C+wohnung_mieten.zimmer_d:3%2C'),
        ('gradinita',
         'https://www.kleinanzeigen.de/s-wohnung-mieten/13503/anzeige:angebote/preis::2500/c203l26758r5+wohnung_mieten.qm_d:90%2C+wohnung_mieten.zimmer_d:3%2C'),
        ('spital',
         'https://www.kleinanzeigen.de/s-wohnung-mieten/13467/anzeige:angebote/preis::2500/c203l3455+wohnung_mieten.qm_d:90%2C+wohnung_mieten.zimmer_d:3%2C'),

        ('tegel',
         'https://www.kleinanzeigen.de/s-wohnung-mieten/13507/anzeige:angebote/preis::2500/c203l3453r5+wohnung_mieten.qm_d:90%2C+wohnung_mieten.zimmer_d:3%2C'),
        ('gradinita',
         'https://www.kleinanzeigen.de/s-wohnung-mieten/13503/anzeige:angebote/preis::2500/c203l26758r5+wohnung_mieten.qm_d:90%2C+wohnung_mieten.zimmer_d:3%2C'),
        ('spital',
         'https://www.kleinanzeigen.de/s-wohnung-mieten/13467/anzeige:angebote/preis::2500/c203l3455+wohnung_mieten.qm_d:90%2C+wohnung_mieten.zimmer_d:3%2C'),
    }

    diff = expect - set(asta_s_eu.scraping.kleinanzeigen_de.ciur.config_parser(the_config))
    assert not diff


@pytest.mark.parametrize('start_url, next_url', [
    pytest.param(
        'https://www.kleinanzeigen.de/s-13507/l3453r1',
        'https://www.kleinanzeigen.de/s-13507/seite:2/l3453r1',
        id='all-from-zip-code'
    ),
    pytest.param(
        'https://www.kleinanzeigen.de/s-familie-kind-baby/13507/hose-104/k0c17l3453r5',
        'https://www.kleinanzeigen.de/s-familie-kind-baby/13507/seite:2/hose-104/k0c17l3453r5',
        id='all-from-pants-and-zip-code'
    ),
    pytest.param(
        EBAY_K_URL.format(id=MY_EBAY_K_ID),
        'https://www.kleinanzeigen.de/s-bestandsliste.html?userId=79809801&pageNum=2&sortingField=SORTING_DATE',
        id='all-prospects-from-user'
    )
])
def test_find_next_url(start_url: str, next_url: str):
    """
    GIVEN an ebay page with prospects
    WHEN find next url
    THEN assert next url match expected result from test
    """
    assert asta_s_eu.scraping.kleinanzeigen_de.ciur.find_next_url(
        start_url, 1
    ) == next_url


def test_parse_a_search_page_until_n_captured():
    """
    GIVEN an ebay page with prospects
    WHEN find n prospects already captured in our database
    THEN finish the page iteration
    """
    parse = mock.Mock(return_value={
        'prospect_list': [
            '1'
        ],
        'has_next_page': True
    })
    start_url_page = mock.create_autospec(str)
    db = mock.create_autospec(asta_s_eu.scraping.kleinanzeigen_de.ciur.ProspectDatabase)
    with mock.patch.object(asta_s_eu.scraping.kleinanzeigen_de.ciur, 'find_next_url'):
        result = asta_s_eu.scraping.kleinanzeigen_de.ciur.parse_a_search_page_until_n_captured(
            parse=parse,
            start_url_page=start_url_page,
            db=db,
            page_limit=2,
            captured_amount=3
        )
        assert result == {'has_more': True, 'prospects': ['1']}


def test_follow_person(caplog: CaptureFixture):
    """
    GIVEN a person ebay page with prospects
    WHEN extract all the prospects
    THEN finish with a message in log 'DONE'
    """
    with \
            mock.patch.object(
                asta_s_eu.scraping.kleinanzeigen_de.ciur, 'ProspectDatabase'
            ), mock.patch.object(
                asta_s_eu.scraping.kleinanzeigen_de.ciur, 'parse_a_search_page_until_n_captured',
                return_value=asta_s_eu.scraping.kleinanzeigen_de.ciur.ProspectsResults(
                    has_more=True,
                    prospects=[])
            ), caplog.at_level(logging.INFO):

        caplog.clear()
        asta_s_eu.scraping.kleinanzeigen_de.ciur.follow_person()
        assert caplog.messages[-1] == 'DONE'

@pytest.mark.skip('temporary disables')
def test_search_all(caplog: CaptureFixture):
    """
    GIVEN a configuration with search all criteria
    AND no prospect for to be found
    WHEN search all
    THEN get last log as "No new item was added"
    """
    with mock.patch.object(
            asta_s_eu.scraping.kleinanzeigen_de.ciur,
            asta_s_eu.scraping.kleinanzeigen_de.ciur.parse_page.__qualname__,
            return_value={'prospect_list': [], 'has_next_page': False}):
        asta_s_eu.scraping.kleinanzeigen_de.ciur.search_all()

    assert caplog.messages[-1] == 'No new item was added'
