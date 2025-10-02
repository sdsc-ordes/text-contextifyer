import re
from text_contextifyer.core.matcher import Matcher


class MarkdownTransformer:
    def __init__(self, matcher: Matcher):
        self.matcher = matcher

    def transform(self, text: str) -> str:
        """
        Scan markdown text and hyperlink ontology matches.
        """

        def replace_word(match):
            word = match.group(0)
            iri = self.matcher.match(word)
            if iri:
                return f"[{word}]({iri})"
            return word

        return re.sub(r"\b\w+\b", replace_word, text)
