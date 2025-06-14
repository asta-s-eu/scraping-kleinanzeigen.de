"""
Testing web page parsing edge cases
"""
from pathlib import Path

from ciur import parse
from ciur.rule import Rule


def test_prospect_list() -> None:
    """
    GIVEN Document and parse rule
    WHEN parse
    THEN prospect_list given
    :return:
    """
    path = Path(__file__).parent
    html_document = parse.Document(
        content=(path / 'prospect_list.html').read_bytes()
    )

    rule_definition = (path / 'prospect_list.ciur').read_text()

    rule = Rule.from_dsl(rule_definition)[0]

    result = parse.html_type(html_document, rule)

    assert result['body']['prospect_list']
