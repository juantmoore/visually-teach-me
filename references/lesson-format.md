# Lesson format

Every lesson is a single JSON file (`<slug>.json`) stored in the user's own folder. The
design and interactive renderer live in `assets/template.html`. `scripts/build.py`
validates the JSON against this specification and builds `<slug>.html`.
`assets/example-how-wifi-works.json` is a complete, valid example using every section type.

---

## 1. Top-level shape

```json
{
  "meta":     { ... },
  "hero":     { ... },
  "sections": [ ... ],
  "sources":  [ ... ]
}
```

### `meta`

| Field | Required | Notes |
|---|---|---|
| `slug` | yes | Lowercase letters, digits, and hyphens. Becomes `<slug>.html`. |
| `title` | yes | Short lesson name (2 to 6 words) for the browser tab. |
| `description` | yes | One-sentence summary for metadata. |
| `eyebrow` | yes | Small label above the title, e.g. `Visual lesson · Networking`. |
| `researched` | yes | `YYYY-MM-DD`, the date facts were checked. |
| `readingTime` | no | Short estimate, e.g. `6 min`. Shown in the hero. |
| `footer` | no | Extra note in the footer (for example, an "as of" note). |
| `published_url` | no | URL where this lesson was published, for in-place updates. |

### `hero`

| Field | Required | Notes |
|---|---|---|
| `headline` | yes | Clear, inviting title or question that frames the lesson. |
| `lede` | yes | 1 to 2 short sentences naming what the learner will understand by the end. |
| `chips` | no | Color legend of core concepts: array of `{ "label": "DNS", "hue": "violet" }`. |

### `sources`

```json
{ "title": "MDN: How the Web works", "url": "https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works", "asOf": "2025-05" }
```

- `title` (required): readable source name.
- `url` (required): must start with `https://`.
- `asOf` (optional): month or date checked, e.g. `2025-05` or `May 2025`.

---

## 2. Hues (color palette)

Six muted, low-glare hues are available so each core concept keeps the same color across
the whole page (like transit lines):

`teal` · `amber` · `sage` · `rose` · `violet` · `slate`

Attach `"hue": "<name>"` to hero chips, analogy roles, concept cards, diagrams, build-up
steps, example steps/tokens, compare columns, and glossary terms.

---

## 3. Inline markup and paragraphs

Every text field supports three inline patterns (everything else renders as plain text):

| Write | Result |
|---|---|
| `**bold**` | **bold** |
| `` `code` `` | `code` |
| `[label](https://example.com)` | link opening in a new tab |

Fields marked *paragraphs* accept either a single string or an array of strings (one per
paragraph). Keep each paragraph to ~60 words or fewer; `build.py` warns above ~80 words.
Never use em dashes (U+2014) in text fields.

---

## 4. Reusable sub-objects

### Diagram object (`diagram`)

Used in `diagram` sections, `concept.diagram`, and `buildup.steps[].diagram`.

```json
{
  "mermaid": "flowchart LR\n  A[Laptop] --> B[Router] --> C[Server]",
  "caption": "Your laptop talks to the router first, never directly to the website.",
  "alt": "Flowchart with three boxes from left to right: Laptop connects to Router, which connects to Server."
}
```

Or with inline SVG:

```json
{
  "svg": "<svg viewBox=\"0 0 420 110\" xmlns=\"http://www.w3.org/2000/svg\">...</svg>",
  "caption": "One web page split into three numbered packets.",
  "alt": "Three small rounded boxes labeled Packet 1 of 3, Packet 2 of 3, and Packet 3 of 3."
}
```

- Provide **either** `mermaid` **or** `svg` (not both).
- `caption` (required): short 1-sentence takeaway shown below the visual.
- `alt` (required): plain-text description shown as a fallback if Mermaid fails to load and
  used for accessibility.
- For inline `svg`, use `currentColor` or CSS variables (`var(--ink)`, `var(--muted)`,
  `var(--surface)`, `var(--line)`, `var(--c)`, `var(--soft)`) so the graphic adapts cleanly
  to both dark and light themes.

### Collapsible "go deeper" object (`deeper`)

Optional on `concept`, `diagram`, `example`, and `prose`. Keeps the main path short.

```json
{
  "summary": "Go deeper: how DNS caching speeds this up",
  "body": [
    "Your laptop remembers recent lookups in a local cache for a set time called TTL (Time to Live).",
    "While the cache is fresh, your browser skips the lookup and connects right away."
  ]
}
```

---

## 5. Sections

`sections` is an ordered array. Every section has a `type` and accepts these common
optional fields:

| Field | Notes |
|---|---|
| `id` | Anchor slug. Defaults to `<type>-<index>`. |
| `nav` | Short label (1 to 3 words) for the "you are here" progress nav. Omit to hide from nav. |
| `eyebrow` | Small uppercase label above the heading. |
| `title` | Section heading. |
| `intro` | *paragraphs* shown under the heading. |

---

### `tldr`: TL;DR in 3 bullets

Put this first so the learner gets the whole shape in 20 seconds.

```json
{
  "type": "tldr",
  "nav": "TL;DR",
  "eyebrow": "30-second version",
  "title": "The whole picture in 3 bullets",
  "bullets": [
    "**Your laptop asks for an address.** DNS turns a website name into a numbered IP address.",
    "**Wi-Fi carries small envelopes.** Your router moves tiny numbered packets over radio waves.",
    "**Your browser reassembles the page.** Packets arrive in pieces and snap back into a web page."
  ]
}
```

Required: `title`, `bullets` (aim for 3 bullets).

---

### `analogy`: master analogy + role map

Introduces the single analogy world for the lesson and maps each concept to a role.

```json
{
  "type": "analogy",
  "nav": "Analogy",
  "eyebrow": "Master analogy",
  "title": "Think of a neighborhood post office with radio couriers",
  "premise": "Imagine sending a letter to a friend across the country. You write their name, look up their street address, and hand envelopes to a local courier.",
  "roles": [
    {
      "concept": "DNS",
      "role": "The address book",
      "why": "Turns a friendly name like example.com into a numbered street address.",
      "hue": "violet"
    }
  ],
  "limits": "Real packets travel at nearly the speed of light and take different routes, unlike a single paper mail truck."
}
```

Required: `title`, `premise` (*paragraphs*), `roles` (each with `concept`, `role`, `why`;
optional `hue`). Optional: `limits`.

---

### `concept`: one chunk card

Teaches a single idea in a calm, bordered card colored by its `hue`.

```json
{
  "type": "concept",
  "nav": "DNS",
  "eyebrow": "Concept 1",
  "title": "DNS finds the numbered address",
  "hue": "violet",
  "analogy": "Like checking your address book before writing on an envelope.",
  "body": [
    "Computers route traffic using numeric IP (Internet Protocol) addresses like `93.184.216.34`.",
    "DNS (Domain Name System) translates human names like `example.com` into those numbers in milliseconds."
  ],
  "takeaway": "You type a name; DNS hands back the numeric address.",
  "deeper": {
    "summary": "Go deeper: why addresses are cached",
    "body": "Your laptop saves recent answers for minutes or hours so repeat visits skip the lookup."
  }
}
```

Required: `title`, `body` (*paragraphs*).
Optional: `hue`, `analogy`, `diagram`, `takeaway`, `deeper`.

---

### `diagram`: standalone visual

Shows a Mermaid diagram or inline SVG with a caption and text fallback.

```json
{
  "type": "diagram",
  "nav": "Full trip",
  "eyebrow": "Visual map",
  "title": "One web request from laptop to server and back",
  "hue": "teal",
  "mermaid": "sequenceDiagram\n  Laptop->>Router: Radio packets\n  Router->>Server: Internet request\n  Server-->>Router: HTML packets\n  Router-->>Laptop: Radio packets",
  "caption": "Every web page makes a round trip through your router before reaching the wider internet.",
  "alt": "Sequence diagram showing Laptop sending radio packets to Router, Router forwarding an internet request to Server, Server returning HTML packets to Router, and Router sending radio packets back to Laptop."
}
```

Required: `title`, `caption`, `alt`, and either `mermaid` or `svg`. Optional: `hue`, `deeper`.

---

### `buildup`: step-by-step assembly

Pieces concepts together one layer at a time. Each numbered step adds one thing to the
picture and can include its own diagram.

```json
{
  "type": "buildup",
  "nav": "Build it up",
  "eyebrow": "Step by step",
  "title": "Watch the connection come together",
  "steps": [
    {
      "title": "Start with radio waves in your room",
      "adds": "Local wireless link",
      "hue": "teal",
      "body": "Your laptop's Wi-Fi chip turns digital bits into radio waves and beams them to your router.",
      "diagram": {
        "mermaid": "flowchart LR\n  L[Laptop] <-->|Wi-Fi radio| R[Router]",
        "caption": "Wi-Fi only covers the short hop between your device and your router.",
        "alt": "Laptop connected by a two-way Wi-Fi radio arrow to Router."
      }
    }
  ],
  "summary": "Together, local radio, router translation, and internet routing turn a click into a loaded page."
}
```

Required: `title`, `steps` (each with `title`, `body`; optional `adds`, `hue`, `diagram`).
Optional: `summary`.

---

### `example`: worked example

Shows a concrete input transformed step by step into a concrete output. Supports monospace
`code` blocks and `tokens` rows.

```json
{
  "type": "example",
  "nav": "Worked example",
  "eyebrow": "Trace a real request",
  "title": "Loading example.com step by step",
  "input": {
    "label": "You type in the browser",
    "value": "https://example.com",
    "code": true
  },
  "steps": [
    {
      "label": "1. Look up the IP address",
      "hue": "violet",
      "detail": "Your laptop asks a DNS resolver for `example.com`.",
      "code": "DNS A? example.com  ->  93.184.216.34"
    },
    {
      "label": "2. Slice the reply into packets",
      "hue": "amber",
      "detail": "The server breaks the HTML into numbered pieces.",
      "tokens": [
        { "text": "PKT 1/3", "label": "Header", "hue": "amber" },
        { "text": "PKT 2/3", "label": "Body", "hue": "amber" },
        { "text": "PKT 3/3", "label": "End", "hue": "amber" }
      ]
    }
  ],
  "output": {
    "label": "What appears on screen",
    "value": "The rendered Example Domain web page in your browser tab."
  }
}
```

Required: `title`, `input`, `steps` (each with `label`, `detail`; optional `code`, `tokens`,
`hue`), `output`.
`input` and `output` can be a plain string or `{ "label", "value", "code"? }`.
Each item in `tokens` can be a plain string or `{ "text", "label"?, "hue"? }`.

---

### `compare`: comparison table

Lines up options or concepts side by side. Scrolls horizontally on small screens.

```json
{
  "type": "compare",
  "nav": "Compare",
  "eyebrow": "Side by side",
  "title": "Wi-Fi frequency bands",
  "columns": [
    { "label": "2.4 GHz", "hue": "amber" },
    { "label": "5 GHz", "hue": "teal" }
  ],
  "rows": [
    { "label": "Range through walls", "cells": ["Reaches farther", "Shorter range"] },
    { "label": "Typical speed", "cells": ["Slower", "Faster"] }
  ]
}
```

Required: `title`, `columns` (strings or `{ "label", "hue"? }`), `rows` (each with `label`
and `cells` matching the number of columns).

---

### `confusions`: common confusions

Pairs a common misconception (`myth`) with a clear correction (`reality`).

```json
{
  "type": "confusions",
  "nav": "Confusions",
  "eyebrow": "Common confusions",
  "title": "Three myths that trip people up",
  "items": [
    {
      "myth": "Wi-Fi is the internet.",
      "reality": "Wi-Fi is only the wireless hop to your router. You can have full Wi-Fi bars even when your internet line is down."
    }
  ]
}
```

Required: `title`, `items` (each with `myth` and `reality`).

---

### `check`: quick-check micro-quiz

A single-question check placed right after a concept chunk. Clicking an option gives
instant feedback.

```json
{
  "type": "check",
  "eyebrow": "Quick check",
  "prompt": "You type `example.com` and press Enter. What job does DNS do first?",
  "options": [
    "Converts the page into Wi-Fi radio waves",
    "Looks up the numeric IP address for example.com",
    "Encrypts your password"
  ],
  "answer": 1,
  "explain": "DNS acts like an address book. It returns the IP address so your laptop knows where to send packets."
}
```

Required: `prompt`, `options` (at least 2), `answer` (0-based index), `explain`.
Optional: `title`, `eyebrow` (defaults to `Quick check`).

---

### `glossary`: short glossary

Compact reference of key terms introduced in the lesson.

```json
{
  "type": "glossary",
  "nav": "Glossary",
  "eyebrow": "Key terms",
  "title": "Words worth keeping",
  "terms": [
    { "term": "DNS", "definition": "Domain Name System. Translates website names into IP addresses.", "hue": "violet" },
    { "term": "Packet", "definition": "A small numbered chunk of data sent across a network.", "hue": "amber" }
  ]
}
```

Required: `title`, `terms` (each with `term` and `definition`; optional `hue`).

---

### `quiz`: final quiz

Interactive 4 to 6 question quiz, one question at a time with a score counter.

```json
{
  "type": "quiz",
  "nav": "Final quiz",
  "eyebrow": "Test yourself",
  "title": "Four quick scenarios",
  "questions": [
    {
      "prompt": "Your laptop shows full Wi-Fi bars, yet no website loads. What is most likely broken?",
      "options": [
        "Your laptop's Wi-Fi antenna",
        "The internet link past your router or DNS",
        "Your browser's screen renderer"
      ],
      "answer": 1,
      "explain": "Full Wi-Fi bars only confirm a strong radio link to the router. The break is usually between the router and the internet."
    }
  ]
}
```

Required: `title`, `questions` (4 to 6 items, each with `prompt`, `options`, `answer`,
`explain`). Vary the `answer` index across questions.

---

### `recap`: end-of-lesson summary

Closes the loop with a short checklist of what the learner now knows.

```json
{
  "type": "recap",
  "nav": "Recap",
  "eyebrow": "What you learned",
  "title": "Keep these three ideas",
  "points": [
    "**DNS** finds the numeric address before any page loads.",
    "**Wi-Fi** is only the local radio hop to your router.",
    "**Packets** let big web pages travel in small, reliable pieces."
  ],
  "nextSteps": [
    "Open your browser's Network tab on any site to watch requests happen live."
  ]
}
```

Required: `title`, `points`. Optional: `nextSteps`.

---

### `prose`: fallback section

For anything that does not fit the structured types above. Use sparingly.

```json
{
  "type": "prose",
  "eyebrow": "Side note",
  "title": "What happens when a packet gets lost",
  "body": "Wi-Fi signals bounce off walls and run into interference. When a packet drops, TCP notices the missing number and asks for a fresh copy.",
  "callout": {
    "tone": "good",
    "text": "You rarely notice a single dropped packet because retries happen in milliseconds."
  }
}
```

Required: `title`, `body` (*paragraphs*).
Optional: `callout` (`tone` is `good`, `warn`, or `neutral`, plus `text`), `deeper`.
