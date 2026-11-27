# Example: LLM tokens, tokenizers and embeddings

Generated with the visually-teach-me skill (content drafted by Venice `gemini-4-neon`, then fact-checked).

- `llm-tokens.json`: the lesson content
- `llm-tokens.html`: the built page (open in any browser)
- `screenshots/`: desktop (1280px, split into parts) and phone (390px) renders in dark mode

Rebuild: `python3 scripts/build.py examples/llm-tokens/llm-tokens.json`

Fact checks applied: token splits and IDs in the worked example come from `tiktoken` (`cl100k_base`, n_vocab 100,277) and the Hugging Face `bert-base-uncased` tokenizer (vocab 30,522), run on 2026-11-26.
