# Visually Teach Me

An agent skill that turns any topic (technical or non-technical) into a single,
self-contained, visual, ADHD-friendly HTML lesson.

Each lesson is authored as one JSON file and compiled with a shared low-glare dark-mode
template using a zero-dependency Python script.

## What makes a lesson ADHD-friendly

- **3-bullet TL;DR up top** so you get the shape of the topic in 20 seconds.
- **Sticky progress bar and numbered step nav** so you always know where you are.
- **One master analogy** carried across the whole lesson, plus per-concept analogies.
- **Small chunks** (one idea per card, ~60 words per chunk) with optional collapsible
  **Go deeper** drawers.
- **Diagrams everywhere** via Mermaid (rendered client-side with a text fallback) and inline
  SVG.
- **Step-by-step build-ups and worked examples** that show concrete inputs turning into
  outputs.
- **Quick-check micro-quizzes** right after chunks, plus a 4 to 6 question final quiz.
- **Calm, low-glare dark mode by default** (with an optional light-mode toggle saved in
  `localStorage`) and full support for `prefers-reduced-motion`.

## Repository layout

```
visually-teach-me/
├── SKILL.md                             # Agent workflow and writing rules
├── references/
│   └── lesson-format.md                 # Full JSON schema for all 13 section types
├── assets/
│   ├── template.html                    # Shared dark-first HTML/CSS/JS template
│   └── example-how-wifi-works.json      # Complete valid example using every section type
├── scripts/
│   └── build.py                         # Validator and HTML builder (Python 3.8+, stdlib)
└── README.md
```

## Install

Copy this folder into your agent's skills directory (for example,
`~/.claude/skills/visually-teach-me/` or your project's `.claude/skills/visually-teach-me/`).
No packages or build tools are required beyond Python 3.8+.

## Quick start

Validate and build the included example lesson:

```bash
python3 scripts/build.py assets/example-how-wifi-works.json -o /tmp/vtm-demo
```

Then open `/tmp/vtm-demo/how-wifi-works.html` in any browser.

### Useful commands

```bash
# Validate a lesson without writing HTML
python3 scripts/build.py --check path/to/my-lesson.json

# Build a single lesson (writes <slug>.html next to the JSON)
python3 scripts/build.py path/to/my-lesson.json

# Rebuild every lesson in a folder
python3 scripts/build.py path/to/lessons/

# Build a body fragment for publishing tools that add their own <html> wrapper
python3 scripts/build.py --fragment path/to/my-lesson.json
```

## Requirements

- Python 3.8 or newer (standard library only).
- Any modern browser. Lessons are self-contained; Mermaid diagrams load from jsDelivr CDN
  and automatically show their plain-text description if you are offline.
