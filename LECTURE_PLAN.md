# Use case #1 — Debug an error with an LLM

One incident, one corpus, four notebooks. Each asks a question the **previous method
demonstrably cannot answer**. The through-line: *retrieval decides what the LLM sees,
and every retrieval method is blind to something.*

**Corpus:** `acme-docs/` — 16 documents → **71 indexed sections**, 6 components,
2 superseded docs, dates spanning 2024–2026.

**Shared plumbing:** `acme.py` (loading, `##`-section splitting, metadata parsing,
tokenizer, BM25). Each notebook stays ~3 sections and shows only its own method.

```
Sapir ─┬─ Kesh ──┐
       └─ Nugat ─┼─ Lomi ── Tuki
                 └─ Vello
```

---

## `01_lexical_search.ipynb` — Lexical (BM25) ✅ built

**Q1:** *"We saw the following Acme error in the logs: `CONFIGURATION_IS_MISSING`, what should I do?"*
The operator copy-pasted a log line. Rare exact string — BM25's home turf.

**Result:** finds the right topic instantly out of 71 sections, and puts a **superseded
2024 page at #1** (17.4 vs 14.2), with a second stale doc at #4. Its fix,
`sapir --reload-config`, was deleted in 2025.

**Blind to:** meaning, and freshness.

---

## `02_semantic_search.ipynb` — Semantic (embeddings) ✅ built

**Q2 is Q1, described instead of quoted** — same incident, same operator, no log line:
*"Acme won't start after last night's deploy and the logs mention something it needed
but could not find. What should I do?"* Every word that's left (`start`, `logs`,
`deploy`, `find`) is common across the corpus.

**Result:**

| | where the correct current section ranks |
| --- | --- |
| BM25 | **#16** — and its #2 is the *stale twin* of that same section |
| Embeddings | **#2** — inside any realistic context window |

Then the payoff cell: same model, same question, top-3 sections from each ranking.
gpt-oss-120b on BM25's context says *"open `sapir.conf`, add the missing key to the
`[required]` section"* — **a file deleted in the 2025 migration.** On the embedding's
context: *"check the line above the error for the key name, confirm it's in
`acme.config.yaml` or the environment, restart Sapir."* The current procedure.

**Two honest findings that survived measurement** (both are in the notebook):
1. **Put the log line back and embeddings stop helping.** On Q1: same top two as BM25,
   same wrong order, but BM25 spreads them 23% and the embedding only 4%. Semantic wins
   when the operator *describes*, lexical wins when they *paste* — argument for
   **hybrid**, not for replacing `01`.
2. **Embeddings are just as date-blind.** Superseded doc still #1.

**Tools:** `text-embedding-3-small` (`OPENAI_KEY`), vectors cached to `embeddings.json`
so it runs offline on stage. Answers from `openai/gpt-oss-120b` (`OPENROUTER_API_KEY`).
Keys read from a local `.env` via `acme.api_key()`; override with `ACME_ENV_FILE`.

> gpt-oss-120b is a **reasoning** model with no embeddings endpoint — it generates the
> answers, it cannot produce the vectors. It also occasionally spends its whole token
> budget on reasoning and returns empty content, so `answer()` retries. Don't remove that.

---

## `03_structured_search.ipynb` — Structured: intent → SQL ✅ built

**This is the production-pattern notebook.** It reproduces intent-to-SQL translation:
a **small** model (`gpt-4.1-mini`) translates the question into
SQL, and the SQL is executed. Two calls, both small — extraction and SQL writing are
classification, not reasoning.

**Q3 escalates the same incident:** *"For every component: who owns it, how many docs we
have, and how many are superseded?"* No passage contains this answer — it's a join and a
count. Deliberately **not** a date/`ls`-style question.

**§1 Extract the intent into fields** — forced tool call. Two design details do the work:
- `chain_of_thought` is the **first property**, so the model reasons before committing to
  values (order matters: the model fills fields top-down).
- `query_type` (`content_lookup` / `corpus_enumeration` / `aggregate`) gates `keywords`.
  Without it the model emitted `keywords: ["Acme startup failure"]` for a pure
  enumeration, the SQL added a text filter, and **4 of 7 components came back "none"**.
  That field is the difference between the right answer and a confident wrong one.

**§2 Write the SQL from few-shots** — CoT is hand-authored as `-- Step N:` comments inside
each answer. **We write the reasoning; the model copies its shape.** Production ships dozens; we
ship 3. The comments also carry engine traps, not domain knowledge — `conjunctive := 1`
(BM25 is OR-based: `'sapir conf'` matched 13 of 16 docs without it, 2 with it), count
DISTINCT filename because chunks are sections. Production equivalents: *"do NOT use CTEs"*,
*"do NOT use `IN (...)` with your user-lookup function"*.

**§3 The same small model, no structure** — identical question, top-8 chunks instead of a
schema:

| approach | tokens in | $/1k queries | result |
| --- | --- | --- | --- |
| structured (2 small calls) | 1 267 | **$0.94** | correct |
| unstructured `k=8` | 1 161 | $1.14 | **wrong** — 5/7 components |
| unstructured `k=ALL` | 9 418 | $4.54 | correct |

`k=8` costs *more* than structured **and is wrong** — Nugat and Vello vanish, Sapir shows
3 docs not 4, Platform 2 not 4, all rendered as a clean summary table with no hedging.
The only correct unstructured run is the one that pastes the whole database into the
prompt.

**The scaling argument is the real one:** structured input is *constant* (system +
few-shots + question) at any corpus size and prompt-cacheable; stuff-the-context grows
with `k`, and `k` must grow with the corpus. Fine at 16 docs, impossible at 16 000.
Honest weak spot: latency — 2 sequential calls (~9s) vs one (~5.5s). Production runs its
intent and SQL calls concurrently via `asyncio.gather` for exactly this reason.

Every number wrong, nothing flagged as uncertain, formatted to look authoritative. It
can't know what it wasn't shown. Raising `k` hides it rather than fixing it — you reach a
complete list only when `k` ≈ the whole corpus, at which point you've pasted the database
into the prompt. Fine at 16 docs, never again.

**Pattern to state on the slide:** small model · author the CoT · few-shots encode *your*
engine's traps · forced structured output · the LLM writes **structure**, not values
(production discards the model's FTS terms entirely and substitutes its own).

**Blind to:** traversal.

## `04_graph_search.ipynb` — Graph: multi-hop traversal ✅ built

**Q4 closes the incident:** *"Sapir is down. What else breaks before I fix it, and who do I
page?"* No section contains it and no row does either — it is a walk.

**Correction worth knowing:** a production graph store may have **no `PART_OF` / `RELATES_TO` enum.** Edge labels are
strings *derived* by a single `get_edge_type(src_type, dst_type, label)` function, so a
new Jira link type becomes `ticket_relates to` at runtime with no code change. The only named
constants are HR (`REPORTS_TO`, `MEMBER_OF`, `LIVES_IN`, `WORKS_AS`) plus the
`STRUCTURAL_CONTAINMENT_EDGE_LABELS` tuple. The notebook copies that **mechanism** with labels
that fit this corpus: `PART_OF`, `DEPENDS_ON`, `OWNED_BY`, `SUPERSEDED_BY`, `RELATES_TO`.

**§1 Build** — 28 nodes, 29 edges, entirely from metadata we already parse. `nx.MultiDiGraph`
keyed on the label reproduces a `UNIQUE(source, target, label)` index.

**§2 Traverse from the retrieval seeds** — the architectural point: **the graph does not replace
retrieval, it expands it.** production seeds traversal with the top BM25 hits then
runs a 3-hop BFS, colouring nodes by hop (`TraverseHop.first/second/third`). Copied quirks:
edges read **undirected** (`source = :n OR target = :n`) though stored directed; **hubs
suppressed not truncated** (≥100 edges returns *zero*); team nodes attached but never expanded
(production does this for `person`).

Result: **3 retrieved docs → 20 connected nodes**, including `incident-2026-03-config-outage.md`
and `acme-architecture-overview.md`, which match no query term and arrive purely by connection.

**The find:** the 3-hop cap **misses Tuki** — the very component that paged on-call at 02:15 in
the postmortem. Seeds are documents, so one hop is spent reaching a component at all:
`doc → Sapir → {Kesh, Nugat} → {Vello, Lomi}` runs out one hop short. production traversal is built
for *prompt-context expansion*, which is a different operation from *reachability*.

**§3 Answer** — same graph, filtered to one edge type, no hop cap:

| component | hops | talk to | in 3-hop BFS? |
| --- | --- | --- | --- |
| Kesh | 1 | security-team | yes |
| Nugat | 1 | core-team | yes |
| Lomi | 2 | edge-team | yes |
| Vello | 2 | observability-team | yes |
| **Tuki** | 3 | core-team | **no** |

Five components dark, five teams about to be woken, one that can actually fix it
(platform-team owns Sapir).

**Honest note in the notebook:** retrieval is *not* useless here — `§ Blast radius` lands at #5
and says *"all five downstream components stay dark"* — but it never names them; the names are
in a different section, the owners in a third, the escalation rule in a fourth. Also flagged:
I authored a section literally called "Blast radius", so retrieval performs **better** here than
it would on real docs.

**Tool:** `networkx` (installed). No drawing yet — matplotlib isn't in the venv; say the word if
you want the graph rendered for a slide.

**Closing line:** four methods, one question each — you don't pick one. You pick the shape that
matches the question, and production runs all four, which is exactly what production does: BM25 seeds → graph
traversal → scoring → token budget, with an LLM-written SQL query alongside.
