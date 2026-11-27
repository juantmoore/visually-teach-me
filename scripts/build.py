#!/usr/bin/env python3
"""Build visually-teach-me lesson pages from JSON content files and the shared template.

    python3 scripts/build.py my-topic.json            # validate and build one lesson
    python3 scripts/build.py ~/lessons/               # rebuild every lesson in a folder
    python3 scripts/build.py --check my-topic.json    # validate only, write nothing
    python3 scripts/build.py --fragment my-topic.json # body fragment only, for hosts
                                                      # that add their own <html> wrapper

Each lesson is written next to its JSON file as <slug>.html (override with -o DIR).
The template is found relative to this script (../assets/template.html), so the command
works from any working directory. Standard library only, Python 3.8+.
The content format is documented in references/lesson-format.md.
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "assets" / "template.html"
BODY_MARKER = "<!-- vtm:body -->"

HUES = {"teal", "amber", "sage", "rose", "violet", "slate"}
CALLOUT_TONES = {"good", "warn", "neutral"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CHUNK_WORD_LIMIT = 80

# Required fields per section type (beyond "type").
SECTION_FIELDS = {
    "tldr": ["title", "bullets"],
    "analogy": ["title", "premise", "roles"],
    "concept": ["title", "body"],
    "diagram": ["title", "caption", "alt"],
    "buildup": ["title", "steps"],
    "example": ["title", "input", "steps", "output"],
    "compare": ["title", "columns", "rows"],
    "confusions": ["title", "items"],
    "check": ["prompt", "options", "answer", "explain"],
    "glossary": ["title", "terms"],
    "quiz": ["title", "questions"],
    "recap": ["title", "points"],
    "prose": ["title", "body"],
}

# Keys that contain diagram source or raw code, skipped for prose/em-dash/HTML checks.
SKIP_PROSE_KEYS = {"mermaid", "svg", "code", "url", "published_url"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")


def _prose_fields(obj, path=""):
    """Yield (path, string) for prose strings inside obj, skipping raw code/diagram keys."""
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in SKIP_PROSE_KEYS:
                continue
            yield from _prose_fields(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _prose_fields(v, f"{path}[{i}]")


def _as_list(val) -> list:
    if val is None:
        return []
    return val if isinstance(val, list) else [val]


def _check_chunk_length(r: Report, where: str, value) -> None:
    for idx, chunk in enumerate(_as_list(value)):
        if not isinstance(chunk, str):
            continue
        words = len(chunk.split())
        if words > CHUNK_WORD_LIMIT:
            loc = f"{where}[{idx}]" if isinstance(value, list) else where
            r.warn(loc, f"chunk has {words} words (aim for <=60, warn above {CHUNK_WORD_LIMIT})")


def _check_hue(r: Report, where: str, hue) -> None:
    if hue is not None and hue not in HUES:
        r.err(where, f"hue '{hue}' must be one of {sorted(HUES)}")


def _validate_diagram(r: Report, where: str, d: dict) -> None:
    if not isinstance(d, dict):
        r.err(where, "diagram must be an object")
        return
    has_mmd = bool(d.get("mermaid"))
    has_svg = bool(d.get("svg"))
    if not has_mmd and not has_svg:
        r.err(where, "diagram needs either 'mermaid' or 'svg'")
    elif has_mmd and has_svg:
        r.err(where, "set 'mermaid' or 'svg', not both")
    if has_svg:
        s = str(d["svg"]).strip()
        if not s.startswith("<svg") or "</svg>" not in s:
            r.err(f"{where}.svg", "inline svg must start with '<svg' and contain '</svg>'")
        if "<script" in s.lower():
            r.err(f"{where}.svg", "inline svg must not contain <script> tags")
    for f in ("caption", "alt"):
        if not d.get(f):
            r.err(where, f"missing '{f}'")


def _validate_deeper(r: Report, where: str, d) -> None:
    if d is None:
        return
    if not isinstance(d, dict):
        r.err(where, "'deeper' must be an object with 'summary' and 'body'")
        return
    if not d.get("summary"):
        r.err(where, "missing 'summary'")
    if not d.get("body"):
        r.err(where, "missing 'body'")
    else:
        _check_chunk_length(r, f"{where}.body", d["body"])


def _validate_question(r: Report, where: str, q: dict) -> None:
    if not isinstance(q, dict):
        r.err(where, "question must be an object")
        return
    opts = q.get("options") or []
    if not isinstance(opts, list) or len(opts) < 2:
        r.err(where, "needs at least 2 options")
    ans = q.get("answer")
    if not isinstance(ans, int) or isinstance(ans, bool) or not 0 <= ans < len(opts):
        r.err(where, "answer must be the zero-based index of an option")
    for f in ("prompt", "explain"):
        if not q.get(f):
            r.err(where, f"missing '{f}'")


def validate(lesson: dict) -> Report:
    r = Report()
    if not isinstance(lesson, dict):
        r.err("root", "content must be a JSON object")
        return r

    # meta
    m = lesson.get("meta") or {}
    for f in ("slug", "title", "description", "eyebrow", "researched"):
        if not m.get(f):
            r.err("meta", f"missing '{f}'")
    if m.get("slug") and not ID_RE.match(m["slug"]):
        r.err("meta.slug", "use lowercase letters, digits, and hyphens")
    if m.get("researched") and not DATE_RE.match(m["researched"]):
        r.err("meta.researched", "use YYYY-MM-DD")

    # hero
    hero = lesson.get("hero") or {}
    for f in ("headline", "lede"):
        if not hero.get(f):
            r.err("hero", f"missing '{f}'")
    for i, chip in enumerate(hero.get("chips") or []):
        cw = f"hero.chips[{i}]"
        if not isinstance(chip, dict) or not chip.get("label"):
            r.err(cw, "each chip needs a 'label'")
        else:
            _check_hue(r, cw, chip.get("hue"))

    # sections
    secs = lesson.get("sections") or []
    if not secs:
        r.err("sections", "add at least one section")
    sec_ids: set[str] = set()
    types_seen: list[str] = []

    for i, s in enumerate(secs):
        if not isinstance(s, dict):
            r.err(f"sections[{i}]", "section must be an object")
            continue
        t = s.get("type")
        w = f"sections[{i}] ({t})"
        if t not in SECTION_FIELDS:
            r.err(w, f"unknown type; use one of {sorted(SECTION_FIELDS)}")
            continue
        types_seen.append(t)
        sid = s.get("id") or f"{t}-{i + 1}"
        if not ID_RE.match(sid):
            r.err(w, "id must be lowercase letters, digits, and hyphens")
        if sid in sec_ids or sid == "sources":
            r.err(w, f"duplicate or reserved section id '{sid}'")
        sec_ids.add(sid)

        for f in SECTION_FIELDS[t]:
            if s.get(f) in (None, "", []):
                r.err(w, f"missing '{f}'")

        _check_hue(r, w, s.get("hue"))
        if s.get("intro"):
            _check_chunk_length(r, f"{w}.intro", s["intro"])

        if t == "tldr":
            bullets = s.get("bullets") or []
            if len(bullets) != 3:
                r.warn(w, f"TL;DR has {len(bullets)} bullets; aim for 3")
            _check_chunk_length(r, f"{w}.bullets", bullets)

        elif t == "analogy":
            _check_chunk_length(r, f"{w}.premise", s.get("premise"))
            for j, role in enumerate(s.get("roles") or []):
                rw = f"{w}.roles[{j}]"
                if not isinstance(role, dict):
                    r.err(rw, "role must be an object")
                    continue
                for rf in ("concept", "role", "why"):
                    if not role.get(rf):
                        r.err(rw, f"missing '{rf}'")
                _check_hue(r, rw, role.get("hue"))
                _check_chunk_length(r, f"{rw}.why", role.get("why"))

        elif t == "concept":
            _check_chunk_length(r, f"{w}.body", s.get("body"))
            if s.get("analogy"):
                _check_chunk_length(r, f"{w}.analogy", s["analogy"])
            if s.get("diagram"):
                _validate_diagram(r, f"{w}.diagram", s["diagram"])
            _validate_deeper(r, f"{w}.deeper", s.get("deeper"))

        elif t == "diagram":
            _validate_diagram(r, w, s)
            _validate_deeper(r, f"{w}.deeper", s.get("deeper"))

        elif t == "buildup":
            for j, st in enumerate(s.get("steps") or []):
                sw = f"{w}.steps[{j}]"
                if not isinstance(st, dict):
                    r.err(sw, "step must be an object")
                    continue
                for sf in ("title", "body"):
                    if not st.get(sf):
                        r.err(sw, f"missing '{sf}'")
                _check_hue(r, sw, st.get("hue"))
                _check_chunk_length(r, f"{sw}.body", st.get("body"))
                if st.get("diagram"):
                    _validate_diagram(r, f"{sw}.diagram", st["diagram"])

        elif t == "example":
            for edge in ("input", "output"):
                val = s.get(edge)
                if isinstance(val, dict) and not val.get("value"):
                    r.err(f"{w}.{edge}", "object needs a 'value'")
            for j, st in enumerate(s.get("steps") or []):
                sw = f"{w}.steps[{j}]"
                if not isinstance(st, dict):
                    r.err(sw, "step must be an object")
                    continue
                for sf in ("label", "detail"):
                    if not st.get(sf):
                        r.err(sw, f"missing '{sf}'")
                _check_hue(r, sw, st.get("hue"))
                _check_chunk_length(r, f"{sw}.detail", st.get("detail"))
                for k, tok in enumerate(st.get("tokens") or []):
                    if isinstance(tok, dict):
                        if not tok.get("text"):
                            r.err(f"{sw}.tokens[{k}]", "token object needs 'text'")
                        _check_hue(r, f"{sw}.tokens[{k}]", tok.get("hue"))
            _validate_deeper(r, f"{w}.deeper", s.get("deeper"))

        elif t == "compare":
            cols = s.get("columns") or []
            for j, col in enumerate(cols):
                if isinstance(col, dict):
                    if not col.get("label"):
                        r.err(f"{w}.columns[{j}]", "column object needs 'label'")
                    _check_hue(r, f"{w}.columns[{j}]", col.get("hue"))
            for j, row in enumerate(s.get("rows") or []):
                rw = f"{w}.rows[{j}]"
                if not isinstance(row, dict) or not row.get("label"):
                    r.err(rw, "row needs a 'label'")
                    continue
                cells = row.get("cells") or []
                if len(cells) != len(cols):
                    r.err(rw, f"has {len(cells)} cells, expected {len(cols)}")

        elif t == "confusions":
            for j, it in enumerate(s.get("items") or []):
                iw = f"{w}.items[{j}]"
                if not isinstance(it, dict):
                    r.err(iw, "item must be an object")
                    continue
                for cf in ("myth", "reality"):
                    if not it.get(cf):
                        r.err(iw, f"missing '{cf}'")
                _check_chunk_length(r, f"{iw}.reality", it.get("reality"))

        elif t == "check":
            _validate_question(r, w, s)

        elif t == "glossary":
            for j, term in enumerate(s.get("terms") or []):
                tw = f"{w}.terms[{j}]"
                if not isinstance(term, dict):
                    r.err(tw, "term must be an object with 'term' and 'definition'")
                    continue
                for tf in ("term", "definition"):
                    if not term.get(tf):
                        r.err(tw, f"missing '{tf}'")
                _check_hue(r, tw, term.get("hue"))

        elif t == "quiz":
            qs = s.get("questions") or []
            if qs and not 4 <= len(qs) <= 6:
                r.warn(w, f"quiz has {len(qs)} questions; aim for 4 to 6")
            for j, q in enumerate(qs):
                _validate_question(r, f"{w}.questions[{j}]", q)
            answers = [q.get("answer") for q in qs if isinstance(q, dict)]
            if len(answers) >= 4 and len(set(answers)) == 1:
                r.warn(w, "every correct answer is in the same position; vary it")

        elif t == "recap":
            _check_chunk_length(r, f"{w}.points", s.get("points"))

        elif t == "prose":
            _check_chunk_length(r, f"{w}.body", s.get("body"))
            c = s.get("callout")
            if c is not None:
                if not isinstance(c, dict) or not c.get("text"):
                    r.err(f"{w}.callout", "callout needs 'text'")
                elif c.get("tone", "neutral") not in CALLOUT_TONES:
                    r.err(f"{w}.callout", f"tone must be one of {sorted(CALLOUT_TONES)}")
            _validate_deeper(r, f"{w}.deeper", s.get("deeper"))

    if "tldr" not in types_seen:
        r.warn("sections", "no tldr section; open with a 3-bullet TL;DR")
    if "analogy" not in types_seen:
        r.warn("sections", "no analogy section; include one master analogy")
    if "quiz" not in types_seen:
        r.warn("sections", "no quiz section; add a final quiz so the learner can check themselves")

    # sources
    srcs = lesson.get("sources") or []
    if not srcs:
        r.warn("sources", "no sources listed")
    for i, src in enumerate(srcs):
        if not isinstance(src, dict) or not src.get("title") or not str(src.get("url", "")).startswith("https://"):
            r.err(f"sources[{i}]", "needs a 'title' and an https:// 'url'")

    # prose style & inline markup checks
    for path, text in _prose_fields({k: lesson.get(k) for k in ("meta", "hero", "sections")}):
        if "\u2014" in text:
            r.warn(path, "em dash found; replace with commas, periods, or parentheses")
        if text.count("**") % 2:
            r.warn(path, "unbalanced ** bold markers")
        if text.count("`") % 2:
            r.warn(path, "unbalanced ` code markers")
        if re.search(r"<[a-zA-Z/]", re.sub(r"`[^`]*`", "", text)):
            r.warn(path, "HTML tags render as plain text; use **bold**, `code`, or [label](url)")

    return r


def render(lesson: dict, template: str, fragment: bool = False) -> str:
    m = lesson["meta"]
    # Escape "<" so embedded JSON cannot break out of its <script> tag.
    data = json.dumps(lesson, ensure_ascii=False, indent=1).replace("<", "\\u003c")
    values = {
        "TITLE": html.escape(m["title"]),
        "DESCRIPTION": html.escape(m.get("description", ""), quote=True),
        "DATA": data,
    }
    page = re.sub(r"\{\{(TITLE|DESCRIPTION|DATA)\}\}", lambda mo: values[mo.group(1)], template)
    if fragment:
        return page
    head, body = page.split(BODY_MARKER, 1)
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        + head.strip() + "\n</head>\n<body>\n" + body.strip() + "\n</body>\n</html>\n"
    )


def collect(paths: list[str]) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for p in paths:
        path = pathlib.Path(p).expanduser()
        if path.is_dir():
            files += sorted(path.glob("*.json"))
        else:
            files.append(path)
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="content JSON files, or folders of them")
    ap.add_argument("--check", action="store_true", help="validate only, write nothing")
    ap.add_argument("--fragment", action="store_true",
                    help="write page body without <!doctype>/<html>/<head>/<body> wrapper")
    ap.add_argument("-o", "--out", help="output folder (default: next to each JSON file)")
    ap.add_argument("--template", default=str(TEMPLATE), help="template file path")
    args = ap.parse_args()

    files = collect(args.paths)
    if not files:
        print("No .json content files found.", file=sys.stderr)
        return 2

    try:
        template = pathlib.Path(args.template).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Can't read template ({exc}). Expected at {TEMPLATE}.", file=sys.stderr)
        return 2
    for ph in ("{{TITLE}}", "{{DESCRIPTION}}", "{{DATA}}", BODY_MARKER):
        if ph not in template:
            print(f"Template is missing {ph}.", file=sys.stderr)
            return 2

    failed = False
    for f in files:
        try:
            lesson = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"✗ {f}: can't read JSON ({exc})")
            failed = True
            continue

        rep = validate(lesson)
        for wmsg in rep.warnings:
            print(f"  warning  {wmsg}")
        for emsg in rep.errors:
            print(f"  error    {emsg}")
        if rep.errors:
            print(f"✗ {f}: {len(rep.errors)} error(s), not built")
            failed = True
            continue
        if args.check:
            print(f"✓ {f}: valid ({len(rep.warnings)} warning(s))")
            continue

        if args.out:
            out_dir = pathlib.Path(args.out).expanduser()
        elif SKILL_DIR in f.resolve().parents:
            out_dir = pathlib.Path.cwd()
        else:
            out_dir = f.resolve().parent

        name = lesson["meta"]["slug"] + (".fragment.html" if args.fragment else ".html")
        dest = out_dir / name
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            dest.write_text(render(lesson, template, args.fragment), encoding="utf-8")
        except OSError as exc:
            print(f"✗ {f}: can't write {dest} ({exc}). Pass -o with a writable folder.")
            failed = True
            continue

        size = dest.stat().st_size
        note = "  (over 1 MB; trim content)" if size > 1_000_000 else ""
        print(f"✓ {f} -> {dest} ({size / 1024:.0f} KB, {len(rep.warnings)} warning(s)){note}")
        if lesson["meta"].get("published_url"):
            print(f"  previously published at {lesson['meta']['published_url']}; republish there to update it")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
