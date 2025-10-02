from rdflib import URIRef
from text_contextifyer.core.matcher import Matcher
from text_contextifyer.transformers.markdown_transformer import MarkdownTransformer


def test_markdown_transformer_basic():
    matcher = Matcher({"computer": URIRef("http://example.org/Computer")})
    transformer = MarkdownTransformer(matcher)

    text = "I love Computer science."
    output = transformer.transform(text)

    assert "[Computer](http://example.org/Computer)" in output
