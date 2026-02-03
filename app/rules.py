import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Pattern, Sequence, Tuple


# -----------------------------
# 1) Sentence splitting
# -----------------------------

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[\.\!\?])\s+|\n+", re.MULTILINE)

# Matches abbreviations like "U.S." "U.S.A." "E.U." etc.
_ABBREV_RE = re.compile(r"\b(?:[A-Za-z]\.){2,}")

_DOT_PLACEHOLDER = "<DOT>"


def _split_sentences(text: str) -> List[str]:
    """
    Rough sentence splitter with abbreviation protection.

    Why:
    - Simple regex splitting treats 'U.S.' as sentence end.
    - We protect multi-initial abbreviations (U.S., U.S.A., etc.) first.
    """
    text = (text or "").strip()
    if not text:
        return []

    # 1) Protect abbreviations by replacing '.' inside them
    def _protect(m: re.Match) -> str:
        return m.group(0).replace(".", _DOT_PLACEHOLDER)

    protected = _ABBREV_RE.sub(_protect, text)

    # 2) Split sentences
    parts = _SENTENCE_SPLIT_RE.split(protected)

    # 3) Restore dots and clean
    out: List[str] = []
    for p in parts:
        p = (p or "").strip()
        if not p:
            continue
        p = p.replace(_DOT_PLACEHOLDER, ".")
        out.append(p)

    return out


# -----------------------------
# 2) Rule definition (rule table)
# -----------------------------


@dataclass(frozen=True)
class RuleSpec:
    """
    A data-driven rule.

    name:
      The label name you want in hits (e.g. 'clearance', 'citizenship').

    positive:
      Regex patterns indicating a requirement.

    negation_cues:
      Words/phrases indicating negation near the positive match
      (e.g. 'not required', 'no', 'without').

    Notes:
      - We keep negation cues generic; they’re applied with a window (scope).
      - If you want, you can add 'priority' or 'weight' later.
    """

    name: str
    positive: Sequence[Pattern[str]]
    negation_cues: Sequence[Pattern[str]]
    explicit_negatives: Sequence[Pattern[str]] = ()


def _compile_all(patterns: Sequence[str]) -> List[Pattern[str]]:
    """
    Compile patterns once.

    Speed + catch regex bugs early + easier to test.
    """
    return [re.compile(p, flags=re.IGNORECASE) for p in patterns]


# -----------------------------
# 3) Patterns
# -----------------------------

CLEARANCE_POS = _compile_all(
    [
        r"\bsecurity clearance\b",
        r"\bclearance\b",
        r"\b(ts\/sci|ts-sci)\b",
        r"\btop secret\b",
        r"\bsecret clearance\b",
    ]
)

CITIZENSHIP_POS = _compile_all(
    [
        r"\b(u\.s\. citizen|us citizen|united states citizen)\b",
        r"\b(u\.s\. citizenship|us citizenship)\b",
        r"\bcitizenship\b",
        r"\bonly\s+u\.s\.\s+citizens\b",
        r"\bmust be (a )?u\.s\.\s+citizen\b",
    ]
)

# Generic negation cues (mechanism-based)
# You can evolve this list over time; it’s not “enumerating sentences”.
NEGATION_CUES = _compile_all(
    [
        r"\bno\b",
        r"\bnot\b",
        r"\bwithout\b",
        r"\bdoes(?:n'?t)?\b",  # doesn't / does not
        r"\bdo(?:n'?t)?\b",  # don't / do not
        r"\bnot required\b",
        r"\bno longer required\b",
        r"\bnot necessary\b",
        r"\bnot needed\b",
        r"\bnot a requirement\b",
        r"\bpreferred\b.*\bnot required\b",  # common phrasing: preferred but not required
    ]
)

CLEARANCE_NEG_EXPLICIT = _compile_all(
    [
        r"\bno\s+clearance\s+required\b",
        r"\bclearance\s+not\s+required\b",
    ]
)

CITIZENSHIP_NEG_EXPLICIT = _compile_all(
    [
        r"\bno\s+u\.?\s*s\.?\s+citizenship\s+required\b",
        r"\bno\s+u\.?\s*s\.?\s+citizen(?:ship)?\s+required\b",
        r"\bno\s+citizenship\s+required\b",
        r"\bcitizenship\s+not\s+required\b",
    ]
)


RULES = [
    RuleSpec(
        name="clearance",
        positive=CLEARANCE_POS,
        negation_cues=NEGATION_CUES,
        explicit_negatives=CLEARANCE_NEG_EXPLICIT,
    ),
    RuleSpec(
        name="citizenship",
        positive=CITIZENSHIP_POS,
        negation_cues=NEGATION_CUES,
        explicit_negatives=CITIZENSHIP_NEG_EXPLICIT,
    ),
]

# -----------------------------
# 4) Negation window logic
# -----------------------------

_WORD_RE = re.compile(r"[A-Za-z0-9\.\-/]+")


def _tokenize(sentence: str) -> List[str]:
    """
    Tokenize a sentence into rough 'words'.

    Window-based negation (N words around a match) needs token positions.
    """
    return _WORD_RE.findall(sentence.lower())


def _find_first_match_span(
    sentence: str, patterns: Sequence[Pattern[str]]
) -> Optional[Tuple[int, int]]:
    """
    Find the first regex match span (start, end) in the sentence for any pattern.
    Returns None if no match.

    We need a position to anchor the negation window.
    """
    for pat in patterns:
        m = pat.search(sentence)
        if m:
            return (m.start(), m.end())
    return None


def _char_index_to_token_index(sentence: str, char_pos: int) -> int:
    """
    Convert a char index into a token index.

    We find regex match spans in chars, but apply negation in token windows.
    """
    # Count how many tokens start before char_pos
    idx = 0
    for m in _WORD_RE.finditer(sentence):
        if m.start() >= char_pos:
            break
        idx += 1
    return idx


def _is_negated(
    sentence: str,
    match_span: Tuple[int, int],
    negation_cues: Sequence[Pattern[str]],
    window_tokens: int = 6,
) -> bool:
    """
    Determine if a positive match is negated in the same sentence.

    Mechanism:
    - locate match position in tokens
    - look within +/- window_tokens for any negation cue match


    - avoids global cancellation
    - captures many phrasings without enumerating full sentences
    """
    tokens = _tokenize(sentence)
    if not tokens:
        return False

    start_char, _ = match_span
    anchor = _char_index_to_token_index(sentence, start_char)

    left = max(0, anchor - window_tokens)
    right = min(len(tokens), anchor + window_tokens + 1)
    window_text = " ".join(tokens[left:right])

    return any(cue.search(window_text) for cue in negation_cues)


# -----------------------------
# 5) Rule evaluation
# -----------------------------


def _collect_evidence_for_rule(
    sentences: List[str], rule: RuleSpec, max_items: int = 5
) -> Tuple[bool, List[str]]:
    """
    Return (flag, evidence_sentences) for a single rule.

    Evidence policy:
    - sentence is evidence if it matches positive pattern AND is not negated (per window)
    - de-duplicate while preserving order
    """

    evidence: List[str] = []
    for s in sentences:
        if rule.name == "citizenship":
            print("SENTENCE:", repr(s))
            print("EXPL_NEG_MATCH:", any(p.search(s) for p in rule.explicit_negatives))

        span = _find_first_match_span(s, rule.positive)
        if not span:
            continue

        # 1) Explicit negatives first (highest precision)
        if rule.explicit_negatives and any(
            p.search(s) for p in rule.explicit_negatives
        ):
            continue

        # 2) Then window negation (more general)
        if _is_negated(s, span, rule.negation_cues, window_tokens=6):
            continue

        evidence.append(s)
        if len(evidence) >= max_items:
            break

    # De-duplicate preserving order
    seen = set()
    unique: List[str] = []
    for e in evidence:
        if e not in seen:
            seen.add(e)
            unique.append(e)

    return (len(unique) > 0, unique)


def analyze_jd(text: str) -> Dict:
    """
    Core function.

    Output contract stays the same as your current implementation.
    """
    text = (text or "").strip()
    sentences = _split_sentences(text)

    hits: List[str] = []
    evidence_all: List[str] = []

    results: Dict[str, Tuple[bool, List[str]]] = {}

    for rule in RULES:
        flag, evidence = _collect_evidence_for_rule(sentences, rule, max_items=5)
        results[rule.name] = (flag, evidence)

        if flag:
            hits.append(rule.name)
            evidence_all.extend(evidence)

    # Final evidence de-dup + limit
    seen = set()
    evidence_unique: List[str] = []
    for e in evidence_all:
        if e not in seen:
            seen.add(e)
            evidence_unique.append(e)

    return {
        "requires_clearance": results.get("clearance", (False, []))[0],
        "requires_citizenship": results.get("citizenship", (False, []))[0],
        "hits": hits,
        "evidence": evidence_unique[:5],
    }
