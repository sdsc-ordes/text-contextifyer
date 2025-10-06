import logging
import re
import string
from typing import Dict, Optional, Tuple

from rapidfuzz import process, fuzz
from rdflib import URIRef

logger = logging.getLogger("matcher")

DEFAULT_STOPWORDS = {
    "the", "of", "on", "a", "an", "is", "in", "and", "for", "to", "with", "as",
}


class Matcher:
    """
    Matcher for mapping tokens / n-grams to ontology IRIs using fuzzy matching.

    Behavior highlights:
    - Normalizes tokens by removing internal punctuation and collapsing spaces.
    - Skips tokens that are stopwords, purely numeric, or obviously junk.
    - Exact label matches win immediately.
    - Multi-word tokens are matched only via exact match (no fuzzy multi-word matching).
    - Uses a dynamic fuzzy score cutoff based on token length to reduce false positives.
    """

    def __init__(
        self,
        label_map: Dict[str, URIRef],
        log_matches: bool = False,
        stopwords: Optional[set] = None,
        allow_multiword_fuzzy: bool = False,
    ) -> None:
        """
        :param label_map: mapping from label (human text) -> rdflib.URIRef
        :param log_matches: whether to emit debug logs for match decisions
        :param stopwords: optional set of stopwords to override default
        :param allow_multiword_fuzzy: if True, allow fuzzy matching of multi-word tokens;
                                      defaults to False (safer).
        """
        self.stopwords = stopwords if stopwords is not None else DEFAULT_STOPWORDS
        self.log_matches = log_matches
        self.allow_multiword_fuzzy = allow_multiword_fuzzy

        # Normalize labels consistently and use the normalized label as the key.
        # We intentionally normalize here so comparisons are apples-to-apples.
        self.label_map: Dict[str, URIRef] = {
            self._normalize(label): iri for label, iri in label_map.items()
        }
        self.labels: list[str] = list(self.label_map.keys())

    # --------------------
    # Public API
    # --------------------

    def match(self, text: str, base_score_cutoff: int = 95) -> Optional[URIRef]:
        """
        Try to match `text` to a label. Returns the matched IRI or None.
        """
        token = self._normalize(text)

        # trivial rejects
        if not token:
            self._log_no_match(text, "empty_after_normalize")
            return None
        if self._should_skip(token):
            self._log_no_match(text, "should_skip")
            return None

        # exact match has priority
        iri = self.label_map.get(token)
        if iri:
            self._log_match(text, token, 100, iri, exact=True)
            return iri

        # if token is multi-word, only allow exact match unless allow_multiword_fuzzy
        if " " in token and not self.allow_multiword_fuzzy:
            self._log_no_match(text, "multiword_without_fuzzy")
            return None

        # dynamic cutoff based on token length
        score_cutoff = self._get_score_cutoff(token, base_score_cutoff)

        result = self._find_best_match(token, score_cutoff)
        if result:
            matched_label, score, iri = result
            self._log_match(text, matched_label, score, iri, exact=False)
            return iri

        self._log_no_match(text, "no_fuzzy_match")
        return None

    # --------------------
    # Helpers
    # --------------------

    def _normalize(self, text: str) -> str:
        """
        Normalize text by:
         - lowercasing
         - removing punctuation (including internal commas/periods/etc)
         - collapsing whitespace
        """
        if text is None:
            return ""
        s = str(text).lower()
        # Remove anything that's not word chars, whitespace or hyphen
        s = re.sub(r"[^\w\s-]", "", s)
        # Collapse whitespace
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _should_skip(self, token: str) -> bool:
        """
        Decide whether a normalized token should be skipped:
         - pure numbers or containing any digit
         - single-character tokens
         - stopwords (like 'the', 'of', etc.)
        """
        if not token:
            return True
        if any(ch.isdigit() for ch in token):
            return True
        if len(token) <= 1:
            return True
        # token may be multiple words; if every token is a stopword then skip
        parts = token.split()
        if all(part in self.stopwords for part in parts):
            return True
        return False

    def _get_score_cutoff(self, token: str, base_cutoff: int) -> int:
        """
        Return a numeric score cutoff for fuzzy matching based on token length.
        Short tokens get stricter cutoffs to avoid false positives.
        """
        length = len(token)
        if length < 5:
            return max(base_cutoff, 100)  # require perfect match for tiny tokens
        if length < 8:
            return max(base_cutoff, 97)
        # for longer tokens allow base cutoff (caller can pick 90..95)
        return base_cutoff

    def _find_best_match(self, token: str, score_cutoff: int) -> Optional[Tuple[str, int, URIRef]]:
        """
        Use rapidfuzz to find the best label match above score_cutoff.
        Returns (label, score, iri) or None.
        """
        # Explicitly set scorer and processor for consistent behavior
        result = process.extractOne(
            token,
            self.labels,
            scorer=fuzz.ratio,
            processor=None,
            score_cutoff=score_cutoff,
        )
        if result:
            matched_label, score, _ = result
            iri = self.label_map[matched_label]
            return matched_label, score, iri
        return None

    # --------------------
    # Logging
    # --------------------

    def _log_match(self, original: str, matched_label: str, score: int, iri: URIRef, exact: bool) -> None:
        if not self.log_matches:
            return
        tag = "EXACT" if exact else "FUZZY"
        logger.debug(f"[{tag} MATCH] '{original}' -> '{matched_label}' ({score}%) -> {iri}")

    def _log_no_match(self, original: str, reason: str) -> None:
        if not self.log_matches:
            return
        logger.debug(f"[NO MATCH] '{original}' ({reason})")
