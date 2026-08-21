"""Shared plumbing for the Makani retrieval notebooks.

Corpus loading, section splitting, tokenization and BM25 live here so each
notebook can stay short and show only the method it's actually about.
"""
import os
import re
from collections import namedtuple
from pathlib import Path

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi

DOCS_DIR = Path("makani-docs")

Chunk = namedtuple("Chunk", "filename heading text meta")

# metadata lives in the first blockquote under the H1:  > **Status:** current
# match only that first block, so a later `> **Note:**` callout in the prose
# isn't mistaken for a metadata field
META_BLOCK = re.compile(r'(?:^>.*\n)+', re.M)
META_LINE = re.compile(r'\*\*(.+?):\*\*\s*(.+)')

_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "title"), ("##", "section")],
    strip_headers=False,  # the heading is a strong retrieval signal -- keep it
)

MD_HEADING = re.compile(r'^#+ .*$', re.M)


STAMPED = ("component", "owner", "status", "last_updated")


def render(chunk):
    """How a retrieved chunk is handed to the LLM: provenance header, then body.

    Dates stay structured attributes on the chunk and are rendered here, at prompt
    time -- they are never folded into the indexed text. That's how etesian does it
    (server/search/llm/context_render.py renders `- Created:` / `- Updated:`
    into the context block, while the chunk bytes on disk stay pure body text), and it
    keeps two things separate that are easy to confuse: what the ranking function can
    see, and what the model can see.
    """
    head = [f"{chunk.filename} § {chunk.heading}"]
    head += [f"{k.replace('_', ' ')}: {chunk.meta[k]}" for k in STAMPED if chunk.meta.get(k)]
    return "--- " + " | ".join(head) + " ---\n" + chunk.text


def load_chunks(docs_dir=DOCS_DIR, split="sections", chunk_size=800, chunk_overlap=200):
    """Every doc, chunked. The chunk is the retrieval unit *and* the prompt unit.

    split="sections"  split on ## headers. Needs structured markdown.
    split="fixed"     strip every heading, then cut into fixed-size chunks. This is
                      what you fall back to for Confluence exports, PDFs or Slack
                      threads, where there is no reliable structure to split on.
                      chunk_overlap is the only thing stopping an answer from being
                      sliced in half, at the cost of near-duplicate hits.

    Chunk.text is body only. Metadata rides along in Chunk.meta and is rendered into
    the prompt by render(), never into the index -- see render()'s docstring.
    """
    if split not in ("sections", "fixed"):
        raise ValueError(f"split must be 'sections' or 'fixed', got {split!r}")
    fixed = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    chunks = []
    for path in sorted(Path(docs_dir).glob("*.md")):
        raw = path.read_text()
        block = META_BLOCK.search(raw)
        meta = {k.strip().lower().replace(" ", "_"): v.strip()
                for k, v in META_LINE.findall(block.group(0))} if block else {}
        if split == "sections":
            for section in _splitter.split_text(raw):
                heading = section.metadata.get("section") or section.metadata.get("title", "")
                chunks.append(Chunk(path.name, heading, section.page_content, meta))
        else:
            plain = re.sub(r'\n{3,}', '\n\n', MD_HEADING.sub('', raw)).strip()
            for i, text in enumerate(fixed.split_text(plain)):
                chunks.append(Chunk(path.name, f"[chunk {i}]", text, meta))
    return chunks


# split identifiers on case boundaries (ConfigLoader -> Config Loader) before
# lowercasing, since case is the only signal for the boundary
CAMEL_BOUNDARY = re.compile(r'(?<=[a-z0-9])(?=[A-Z])')
# a live demo runs with whatever timestamp is current -- drop them entirely
ISO_TIMESTAMP = re.compile(r'\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?\b')
# snake_case / kebab-case / dotted.paths, kept whole as an exact-match token
COMPOUND = re.compile(r'[A-Za-z0-9]+(?:[_\-.][A-Za-z0-9]+)+')


def tokenize(text):
    """Emit the exact compound AND its parts: CONFIGURATION_IS_MISSING ->
    configuration_is_missing, configuration, is, missing."""
    text = ISO_TIMESTAMP.sub(' ', text)
    exact = [c.lower() for c in COMPOUND.findall(text)]
    # letters and digits as separate classes: also strips trailing punctuation
    # and splits on _ - . : / since none of those are in either class
    words = re.findall(r'[a-z]+|[0-9]+', CAMEL_BOUNDARY.sub(' ', text).lower())
    # drop bare numbers and single chars (the "s" left by "Makani's")
    return exact + [w for w in words if len(w) > 1 and not w.isdigit()]


def bm25_index(chunks):
    return BM25Okapi([tokenize(c.text) for c in chunks])


def show(chunks, scores, top_k=5, fmt="{:6.3f}"):
    """Print the top_k chunks by score."""
    for i in sorted(range(len(scores)), key=lambda i: -scores[i])[:top_k]:
        c = chunks[i]
        stale = "  ⚠️ superseded" if c.meta.get("status", "").startswith("superseded") else ""
        print(f"  {fmt.format(scores[i])}   {c.filename[:31]:31} § {c.heading[:38]}{stale}")


def api_key(name):
    """Keys come from the environment, falling back to a local .env file."""
    if name in os.environ:
        return os.environ[name]
    env_file = Path(os.environ.get("MAKANI_ENV_FILE", ".env"))
    found = dict(re.findall(r'^([A-Z_]+)\s*=\s*"?([^"\n]+?)"?\s*$', env_file.read_text(), re.M))
    return found[name]
