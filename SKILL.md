---
name: visually-teach-me
description: Research any topic (technical or non-technical) and teach it as a single self-contained, visual, ADHD-friendly HTML lesson with a dark low-glare theme, a master analogy, small concept chunks, Mermaid and inline SVG diagrams, step-by-step build-ups, worked examples, quick-check micro-quizzes, common confusions, a glossary, and a final quiz. Use when someone asks to learn, understand, explain, or be taught any topic, concept, system, or skill visually or step by step.
metadata:
  version: "1.0"
  author: visually-teach-me
---

# Visually Teach Me

Turns any topic into a calm, visual, ADHD-friendly single-page HTML lesson for a curious
adult learner. Every lesson shares one dark-first, low-glare template; each topic is a
single JSON content file validated and compiled by `scripts/build.py`.

## Files in this skill

All paths below are relative to the folder that contains this `SKILL.md`. In Claude Code
and Cowork that folder is `${CLAUDE_SKILL_DIR}`. In other agents, use the folder you loaded
this file from.

| File | Use it to |
|---|---|
| `references/lesson-format.md` | Learn every section type, its fields, and how to write it. **Read before writing content.** |
| `assets/example-how-wifi-works.json` | See a complete, valid lesson using every section type. Copy its structure, not its content. |
| `assets/template.html` | The shared design and renderer. Never edit it while making a lesson. |
| `scripts/build.py` | Validate a content file and build the HTML page. Python 3.8+, standard library only. |

## Workflow

### 1. Scope
From the request, settle:
- **Topic and boundaries.** What the learner wants to understand and what to leave out so
  the lesson stays focused (one clear mental model, not a textbook).
- **Learner level.** Assume a curious adult who is new to this topic unless they tell you
  otherwise.
- **Core concepts.** Pick 3 to 6 core ideas that carry the whole topic.

If a key boundary is ambiguous and would change the whole lesson, ask one short question.
Otherwise start.

### 2. Research
- Check facts against primary, authoritative sources (official docs, standards, textbooks,
  reputable explainers).
- Anything that changes over time (numbers, limits, versions, standards, laws, prices)
  needs a source and an "as of" month/year in the text or source record.
- When sources disagree or a detail is uncertain, say so plainly in the lesson.
- Record every source you rely on in `sources`. Paraphrase; quote at most 15 words.
- **No web search available?** Tell the user before starting, write from what you know,
  mark time-sensitive claims as "unverified as of <your knowledge date>", and only include
  `sources` URLs you are sure exist.

### 3. Choose the master analogy
- Pick **one** concrete, everyday world (a neighborhood post office, a kitchen line, a
  subway map, a library desk, a water pipe network).
- Map every core concept to one clear role in that world.
- Test it: the analogy should explain how the parts interact and where things break down.
  Include a short `limits` note saying where the analogy stops matching reality.
- Reuse the same world in per-concept analogy boxes across the lesson.

### 4. Plan the chunks
Design for an ADHD-friendly reading rhythm:
- Start with a `tldr` (3 bullets) and the `analogy` (master analogy + role map).
- Break the topic into small `concept` cards: one idea per card, short paragraphs, max ~60
  words per chunk. Put extra depth inside collapsible `deeper` blocks so the main path stays
  short.
- Drop a 1-question `check` right after tricky chunks for instant feedback.
- Use `diagram` (Mermaid or inline SVG) and `buildup` (step-by-step assembly) to show how
  pieces connect visually.
- Add a concrete `example` (worked input -> steps -> output), a `compare` table if there
  are modes or options to contrast, `confusions` (myth vs reality), a short `glossary`, a
  4 to 6 question scenario `quiz`, and a `recap`.

### 5. Assign hues
Pick one hue per core concept from the 6 muted palette colors:
`teal`, `amber`, `sage`, `rose`, `violet`, `slate`.

Reuse the same hue for that concept in the hero chips, analogy role map, concept cards,
build-up steps, compare columns, and glossary terms. The color acts like a transit line so
the learner can spot the same concept at a glance.

### 6. Write the JSON content file
Save it as `<slug>.json` in the user's folder, never inside the skill folder (the skill
folder may be read-only and is replaced on update). Use the folder the user named;
otherwise use a `lessons/` folder in the working directory, or your environment's outputs
folder if it has one.

Follow the schema in `references/lesson-format.md`.

### 7. Build and validate
```
python3 scripts/build.py <path-to>/<slug>.json
```
This validates the JSON and writes `<slug>.html` next to it. Fix every error. Fix every
warning (including em dashes and chunks over ~80 words) unless you have a strong reason
not to. Use `python3` or `python`, whichever exists.

### 8. Check the work
- Re-read each fact against its source, especially numbers, dates, and definitions.
- Check every `check` and `quiz` answer is right and its explanation addresses the tempting
  wrong choice.
- Check every Mermaid diagram syntax carefully (valid node IDs, quoted labels if they have
  punctuation) and make sure every diagram has a helpful `caption` and `alt` fallback.
- If you can render pages (a browser tool, Playwright, or a preview), open the built HTML
  at desktop and phone widths. Verify Mermaid diagrams render, quick checks and quiz work,
  collapsible `deeper` panels open, and the light/dark toggle works.

### 9. Deliver
Pick the first option that fits your environment:
- **A tool that publishes an HTML file as a page or artifact.** Publish `<slug>.html`. If
  the tool wraps content in its own `<!doctype>`/`<html>`/`<body>`, rebuild with
  `--fragment` and publish `<slug>.fragment.html` instead. Save the URL to
  `meta.published_url` so updates republish in place.
- **A tool that sends or attaches files.** Send `<slug>.html`.
- **A local coding agent.** Give the user the full path to `<slug>.html` and note that it
  opens in any browser. Offer to open it if you can run a command.

Never retype or paste the built HTML into a reply by hand.

Reply with a short summary of what the lesson covers, any uncertain points to keep in mind,
and a Sources list.

## Writing rules
- Plain, short sentences in active voice.
- Keep each chunk to one idea and ~60 words or fewer.
- Define every acronym the first time you use it.
- **No em dashes anywhere.** Use commas, periods, or parentheses instead.
- **No "not X, but Y" framing.** State what the thing is directly.
- Bold the first few words of list items so they scan cleanly.
- Say what is uncertain or simplified, especially where an analogy bends reality.
- Check facts against sources and record "as of" dates for anything that changes.

## Updating an existing lesson
Edit its `<slug>.json`, rebuild with `scripts/build.py`, and republish to
`meta.published_url` if it has one.

## Changing the design for all lessons
Only when the user asks to change the template:
1. Edit `assets/template.html` in the user's source copy of the skill and bump
   `TEMPLATE_VERSION`.
2. Rebuild a folder of lessons: `python3 scripts/build.py <lessons-folder>/`.
3. Republish any lesson that has a `published_url`.

To add a section type: add its renderer to `R` in `assets/template.html`, add its
validation rules to `scripts/build.py`, and document it in `references/lesson-format.md`.

## No Python available
Build manually with file tools: read `assets/template.html`, replace `{{TITLE}}` and
`{{DESCRIPTION}}` with escaped meta values, replace `{{DATA}}` with the JSON string (with
every `<` escaped as `\u003c`), split on `<!-- vtm:body -->` to wrap in `<!doctype html>`,
`<html>`, `<head>`, and `<body>`, and write `<slug>.html`. Check the JSON against
`references/lesson-format.md` yourself.
