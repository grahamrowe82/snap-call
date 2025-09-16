from __future__ import annotations

from flask import Flask, render_template, request

from .logic import extract_sections


app = Flask(__name__)

MAX_INPUT_CHARS = 2000
SECTION_LAYOUT = [
    ("title", "Title", "text"),
    ("context", "Context", "text"),
    ("options", "Options", "list"),
    ("tradeoffs", "Tradeoffs", "list"),
    ("decision", "Decision", "text"),
    ("next_step", "Next Step", "text"),
    ("risks", "Risks", "list"),
]


def _empty_result() -> dict[str, object]:
    result: dict[str, object] = {}
    for key, _label, kind in SECTION_LAYOUT:
        result[key] = [] if kind == "list" else ""
    return result


def _merge_result(raw: dict[str, object] | None) -> dict[str, object]:
    merged = _empty_result()
    if not raw:
        return merged
    for key, _label, kind in SECTION_LAYOUT:
        value = raw.get(key)
        if kind == "list":
            merged[key] = list(value) if isinstance(value, list) else []
        else:
            merged[key] = str(value).strip() if value else ""
    return merged


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        sections=SECTION_LAYOUT,
        result=_empty_result(),
        text="",
        error=None,
        warning=False,
        max_chars=MAX_INPUT_CHARS,
    )


@app.route("/snapshot", methods=["POST"])
def snapshot():
    text = request.form.get("situation", "")
    error = None
    warning = False
    trimmed_text = text.strip()

    if not trimmed_text:
        error = "Please paste a situation to evaluate."
    elif len(text) > MAX_INPUT_CHARS:
        error = "Trim input to 2,000 characters."

    result = _empty_result()
    if not error:
        extracted = extract_sections(trimmed_text)
        result = _merge_result(extracted)
        has_signal = any(
            [
                bool(result["options"]),
                bool(result["tradeoffs"]),
                bool(result["decision"]),
                bool(result["next_step"]),
                bool(result["risks"]),
            ]
        )
        warning = not has_signal

    return render_template(
        "index.html",
        sections=SECTION_LAYOUT,
        result=result,
        text=text,
        error=error,
        warning=warning,
        max_chars=MAX_INPUT_CHARS,
    )


if __name__ == "__main__":
    app.run(debug=True)
