import re
from typing import Dict, List


def _split_sentences(text: str) -> List[str]:
    pattern = r"(?<=[.!?])\s+"
    sentences = [s.strip() for s in re.split(pattern, text) if s.strip()]
    if not sentences and text.strip():
        sentences = [text.strip()]
    return sentences


def _strip_leading_label(text: str) -> str:
    return re.sub(r"^[\W_]*[A-Za-z0-9 /+]*:\s*", "", text).strip()


def _strip_leading_marker(item: str) -> str:
    cleaned = re.sub(r"^[\-\*•]+", "", item).strip()
    cleaned = re.sub(r"^\(?\d+\)?[.)-]?\s*", "", cleaned)
    return cleaned.strip()


def _split_candidates(text: str, extra_patterns: List[str] = None) -> List[str]:
    cleaned = _strip_leading_label(text)
    parts = [cleaned]
    patterns = [r";", r"\s{2,}"]
    if extra_patterns:
        patterns.extend(extra_patterns)
    for pattern in patterns:
        next_parts: List[str] = []
        for part in parts:
            if not part.strip():
                continue
            split_items = re.split(pattern, part, flags=re.IGNORECASE) if pattern != ";" else part.split(";")
            next_parts.extend(split_items)
        parts = next_parts
    results: List[str] = []
    for part in parts:
        candidate = _strip_leading_marker(part)
        if candidate:
            results.append(candidate.rstrip(" ."))
    return results


def extract_sections(text: str) -> Dict[str, object]:
    data: Dict[str, object] = {
        "title": "",
        "context": "",
        "options": [],
        "tradeoffs": [],
        "decision": "",
        "next_step": "",
        "risks": [],
    }

    if not text or not text.strip():
        return data

    stripped_text = text.strip()
    sentences = _split_sentences(stripped_text)
    lines = [line.strip() for line in stripped_text.splitlines() if line.strip()]

    if sentences:
        first_sentence = sentences[0]
        data["title"] = first_sentence if len(first_sentence) <= 120 else "Untitled decision"
    else:
        data["title"] = "Untitled decision"

    option_lines = set()
    tradeoff_lines = set()

    option_keywords = ("option", " vs ", " or ")
    tradeoff_keywords = ("+/-", "pro", "con", "cost", "benefit")

    for idx, line in enumerate(lines):
        lower = line.lower()

        if any(keyword in lower for keyword in option_keywords):
            items = _split_candidates(line, [r"\s+vs\s+", r"\s+versus\s+", r"\s+or\s+"])
            added = False
            for item in items:
                if item and item not in data["options"]:
                    data["options"].append(item)
                    added = True
            if added:
                option_lines.add(idx)
            continue

        if any(keyword in lower for keyword in tradeoff_keywords):
            items = _split_candidates(line)
            added = False
            for item in items:
                if item and item not in data["tradeoffs"]:
                    data["tradeoffs"].append(item)
                    added = True
            if added:
                tradeoff_lines.add(idx)
            continue

        risk_line = False
        if "risk" in lower:
            if any(marker in lower for marker in ("risks", "risk:", " risk if", " risk of", "risk is", "risk =")) or lower.startswith(
                ("risk", "risks")
            ):
                risk_line = True
        if "concern" in lower or "fail" in lower or " if " in lower:
            risk_line = True

        if risk_line:
            items = _split_candidates(line)
            for item in items:
                if item and item not in data["risks"]:
                    data["risks"].append(item)
            continue

    tentative_phrases = ("need to decide", "must decide", "should decide", "have to decide")
    decision_triggers = (
        "decision:",
        "we will",
        "we'll",
        "we choose",
        "we chose",
        "we decided",
        "we have decided",
        "we've decided",
        "we opt",
        "we opted",
        "we select",
        "we selected",
        "we commit",
        "we are committing",
        "we're committing",
        "we go with",
        "we're going with",
        "we proceed",
        "we're proceeding",
        "we move forward",
        "we're moving forward",
    )

    for sentence in sentences:
        lower = sentence.lower()
        if any(phrase in lower for phrase in tentative_phrases):
            continue
        if lower.startswith("decision:") or any(trigger in lower for trigger in decision_triggers):
            data["decision"] = sentence.strip()
            break

    next_triggers = ("next", "owner", "deadline", "due", " by ", "follow-up", "follow up")
    for sentence in sentences:
        lower = sentence.lower()
        if any(trigger in lower for trigger in next_triggers):
            data["next_step"] = sentence.strip()
            break
    if not data["next_step"]:
        for line in lines:
            lower = line.lower()
            if any(trigger in lower for trigger in next_triggers):
                data["next_step"] = line
                break

    context_candidates: List[str] = []
    context_blockers = (
        "option",
        "tradeoff",
        "pros",
        "cons",
        "risk:",
        "risks",
        "next",
        "owner",
        "deadline",
        "due",
        "decision:",
        "benefit",
        "cost",
    )
    for idx, sentence in enumerate(sentences[1:], start=1):
        lower = sentence.lower()
        if sentence.strip() == data["decision"] or sentence.strip() == data["next_step"]:
            continue
        if any(blocker in lower for blocker in context_blockers):
            continue
        context_candidates.append(sentence.strip())
        if len(context_candidates) >= 2:
            break

    if len(context_candidates) < 2:
        for idx, line in enumerate(lines):
            if idx in option_lines or idx in tradeoff_lines:
                continue
            if line == data["title"] or line == data["decision"] or line == data["next_step"]:
                continue
            lower = line.lower()
            if any(blocker in lower for blocker in context_blockers):
                continue
            if line in context_candidates:
                continue
            context_candidates.append(line)
            if len(context_candidates) >= 2:
                break

    data["context"] = " ".join(context_candidates[:2]).strip()

    return data
