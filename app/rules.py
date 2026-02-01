import re
from typing import Dict, List, Tuple

# --- Keyword patterns (you can expand later) ---

CLEARANCE_PATTERNS = [
    r"\bsecurity clearance\b",
    r"\bclearance\b",
    r"\b(ts\/sci|ts-sci)\b",
    r"\btop secret\b",
    r"\bsecret clearance\b",
]

CITIZENSHIP_PATTERNS = [
    r"\b(u\.s\. citizen|us citizen|united states citizen)\b",
    r"\b(u\.s\. citizenship|us citizenship)\b",
    r"\bcitizenship\b",
    r"\bonly\s+u\.s\.\s+citizens\b",
    r"\bmust be (a )?u\.s\.\s+citizen\b",
]

# Very simple negation phrases (baseline only)
NEGATION_PATTERNS = [
    r"\bno clearance required\b",
    r"\bclearance not required\b",
    r"\bno u\.s\. citizenship required\b",
    r"\bcitizenship not required\b",
]

# --- Helpers ---


def _split_sentences(text: str) -> List[str]:
    """
    Split text into rough sentences.
    Good enough for Day 4; we’ll improve later if needed.
    """
    text = (text or "").strip()
    if not text:
        return []
    parts = re.split(r"(?<=[\.\!\?])\s+|\n+", text)
    return [p.strip() for p in parts if p and p.strip()]


def _find_evidence(
    sentences: List[str], patterns: List[str], max_items: int = 5
) -> Tuple[bool, List[str]]:
    """
    Return (flag, evidence_sentences).
    Evidence sentences are the original sentence strings that match at least one pattern.
    """
    evidence: List[str] = []
    for s in sentences:
        for pat in patterns:
            if re.search(pat, s, flags=re.IGNORECASE):
                evidence.append(s)
                break
        if len(evidence) >= max_items:
            break

    # De-duplicate while preserving order
    seen = set()
    unique: List[str] = []
    for e in evidence:
        if e not in seen:
            seen.add(e)
            unique.append(e)

    return (len(unique) > 0, unique)


def analyze_jd(text: str) -> Dict:
    """
    Day-4 core function.
    Input: JD text
    Output: dict with requires_clearance/requires_citizenship/hits/evidence
    """
    text = (text or "").strip()
    sentences = _split_sentences(text)

    # quick negation check (very simple)
    negated = any(re.search(p, text, flags=re.IGNORECASE) for p in NEGATION_PATTERNS)

    clearance_flag, clearance_evi = _find_evidence(sentences, CLEARANCE_PATTERNS)
    citizenship_flag, citizenship_evi = _find_evidence(sentences, CITIZENSHIP_PATTERNS)

    # Conservative rule: if we see explicit "not required" phrases, prefer False
    if negated:
        # This is simplistic; later we can make it more precise per-sentence.
        # For Day 4, it helps avoid obvious false positives.
        clearance_flag = False if clearance_flag else clearance_flag
        citizenship_flag = False if citizenship_flag else citizenship_flag

    hits: List[str] = []
    evidence: List[str] = []

    if clearance_flag:
        hits.append("clearance")
        evidence.extend(clearance_evi)

    if citizenship_flag:
        hits.append("citizenship")
        evidence.extend(citizenship_evi)

    # Final evidence de-dup + limit
    seen = set()
    evidence_unique: List[str] = []
    for e in evidence:
        if e not in seen:
            seen.add(e)
            evidence_unique.append(e)

    return {
        "requires_clearance": clearance_flag,
        "requires_citizenship": citizenship_flag,
        "hits": hits,
        "evidence": evidence_unique[:5],
    }
