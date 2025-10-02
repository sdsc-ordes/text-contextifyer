import logging
from rapidfuzz import process
from typing import Dict, Optional
from rdflib import URIRef

logger = logging.getLogger("matcher")  # create a named logger

class Matcher:
    def __init__(self, label_map: Dict[str, URIRef], log_matches: bool = False):
        self.label_map = label_map
        self.labels = list(label_map.keys())
        self.log_matches = log_matches

    def match(self, word: str, score_cutoff: int = 92) -> Optional[URIRef]:
        result = process.extractOne(word.lower(), self.labels, score_cutoff=score_cutoff)
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
