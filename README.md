# 🔍 Four Ways to Search: Retrieval Cookbooks

One incident, one document corpus, four search methods. Each notebook asks a question
the **previous method demonstrably cannot answer**.

The through-line: *retrieval decides what the LLM sees, and every retrieval method is
blind to something.*

## Why?

"Just use RAG" hides a real decision: **which retrieval method?** Lexical, semantic,
structured, and graph search each excel at a different question shape, and each fails
quietly on the others, often returning a confident, well-formatted, **wrong** answer.

These notebooks make those failures visible by running all four methods against the
same realistic incident: a service is down after a deploy, the docs contain stale
pages, and the answer to each escalating question lives somewhere a single method
can't reach. The takeaway isn't "pick the best one". Production systems run all
four, and route each question to the shape that matches it.

## The notebooks

| # | Notebook | Method | Question it answers | Blind to |
|---|----------|--------|--------------------|----------|
| 1 | [01_lexical_search.ipynb](01_lexical_search.ipynb) | BM25 (keyword) | "I saw error `CONFIGURATION_IS_MISSING` in the logs" | meaning, freshness |
| 2 | [02_semantic_search.ipynb](02_semantic_search.ipynb) | Embeddings | Same incident, *described* instead of quoted | freshness, exact strings |
| 3 | [03_structured_search.ipynb](03_structured_search.ipynb) | LLM → SQL | "For every component: owner, doc count, superseded count" | traversal |
| 4 | [04_graph_search.ipynb](04_graph_search.ipynb) | Graph traversal | "Sapir is down. What else breaks, and who do I page?" | (needs seeds from retrieval) |

Highlights along the way:

- BM25 ranks a **superseded 2024 doc #1**; its fix references a file deleted a year ago.
- Embeddings rescue the described question (#16 → #2) but are **just as date-blind**.
- Stuffing top-8 chunks into the prompt costs *more* than structured SQL, **and gets the count wrong** without flagging it.
- A 3-hop graph traversal **misses the one component** that actually paged on-call.

## What's in here

- **`acme-docs/`**: the demo corpus. 16 markdown docs (71 indexed sections) for
  *Acme*, a fictional six-service platform. Includes architecture overviews,
  runbooks, error references, a postmortem, and (deliberately) two superseded docs.
- **`acme.py`**: shared plumbing. Corpus loading, section splitting, metadata
  parsing, tokenization, BM25. Keeps each notebook focused on its own method.
- **`embeddings.json`**: precomputed vectors so notebook 02 runs offline.
- **`LECTURE_PLAN.md`**: the full narrative, results, and design notes per notebook.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install rank_bm25 langchain-text-splitters networkx openai jupyter
jupyter lab
```

Run the notebooks in order; each builds on the question the previous one couldn't
answer. Notebooks 01 and 04 run fully offline; 02 and 03 call LLM APIs for answer
generation (embeddings are cached, so 02's retrieval itself works offline too).

> Note: `embeddings.json` was generated before the corpus was renamed, so most of its
> cached vectors no longer match the current chunk text. Run the embedding cell in
> `02_semantic_search.ipynb` once with `OPENAI_KEY` set to regenerate it (154 chunks,
> `text-embedding-3-small`); after that, 02's retrieval is offline again.
