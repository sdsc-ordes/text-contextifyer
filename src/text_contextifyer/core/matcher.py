import logging
import string
from rapidfuzz import process
from typing import Dict, Optional
from rdflib import URIRef

logger = logging.getLogger("matcher")

class Matcher:
    def __init__(self, label_map: Dict[str, URIRef], log_matches: bool = False):
        # lowercase for case-insensitive matching
        self.label_map = {label.lower(): iri for label, iri in label_map.items()}
        self.labels = list(self.label_map.keys())
        self.log_matches = log_matches

    def _strip_punctuation(self, word: str) -> str:
        # only strip leading/trailing punctuation for matching
        return word.strip(string.punctuation).lower()

    def match(self, word: str, score_cutoff: int = 95) -> Optional[URIRef]:
        clean_word = self._strip_punctuation(word)
        result = process.extractOne(clean_word, self.labels, score_cutoff=score_cutoff)
        if result:
            label, score, _ = result
            iri = self.label_map[label]
            if self.log_matches:
                logger.info(f"[MATCH] '{word}' -> '{label}' ({score}%) -> {iri}")
            return iri
        else:
            if self.log_matches:
                logger.info(f"[NO MATCH] '{word}'")
        return None
