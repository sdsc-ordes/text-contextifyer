import logging
from typing import List
from text_contextifyer.core.matcher import Matcher

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class MarkdownTransformer:
    def __init__(self, matcher: Matcher, max_ngram: int = 5):
        self.matcher = matcher
        self.max_ngram = max_ngram

    def transform(self, text: str) -> str:
        words = text.split()
        i = 0
        result_tokens = []

        while i < len(words):
            matched = False
            # Try longest n-grams first
            for n in range(self.max_ngram, 0, -1):
                if i + n > len(words):
                    continue
                ngram = " ".join(words[i:i + n])
                iri = self.matcher.match(ngram)
                if iri:
                    logger.debug(f"Matched n-gram: '{ngram}' -> {iri}")
                    result_tokens.append(f"[{ngram}]({iri})")
                    i += n
                    matched = True
                    break  # break n-gram loop, go to next i
            if not matched:
                result_tokens.append(words[i])
                i += 1

        return " ".join(result_tokens)

if __name__ == "__main__":
    # Example usage
    from rdflib import URIRef

    # Dummy matcher for testing
    label_map = {
        "Thermal Capacity": URIRef("http://example.org/taxonomy/ThermalCapacity"),
        "Brick": URIRef("http://example.org/taxonomy/Brick"),
        "Straw": URIRef("http://example.org/taxonomy/Straw"),
    }
    matcher = Matcher(label_map)
    transformer = MarkdownTransformer(matcher)
    sample_text = "This is a test of the Thermal Capacity and Brick straw"
    transformed = transformer.transform(sample_text)
    print(transformed)
