# tests/test_matcher.py
import pytest
from rdflib import Graph, URIRef, Literal, RDFS
from text_contextifyer.core.matcher import Matcher

@pytest.fixture
def matcher():
    g = Graph()
    ex = URIRef("http://example.org/Computer")
    g.add((ex, RDFS.label, Literal("Computer")))  # must be a Literal
    label_map = {"computer": ex}
    return Matcher(label_map)


def test_exact_match(matcher):
    iri = matcher.match("Computer")
    assert str(iri) == "http://example.org/Computer"


def test_no_match(matcher):
    iri = matcher.match("Banana")
    assert iri is None
