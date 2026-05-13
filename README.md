# Agentic Robotics Research Assistant

An agentic research assistant for robotics, SLAM, 3D perception, and AI-related papers.

This project aims to build a LangGraph-based workflow that can read research papers, summarize key ideas, analyze their technical value, and generate structured Markdown reports.

## Progress

### Day 1

Implemented a minimal LangGraph workflow using manually provided paper information.

Main features:

- Set up the basic project structure
- Connected the LLM client
- Built a minimal LangGraph workflow
- Implemented paper summarization, critique, and report generation nodes
- Generated a Markdown report from mock paper input

Workflow:

```text
paper title + abstract
        ↓
summarize_paper_node
        ↓
critique_paper_node
        ↓
generate_report_node
        ↓
Markdown report
```

### Day 2

Extended the project from mock paper input to real PDF paper processing.

Main features:

- Added PDF loading support with `pypdf`
- Extracted text from local research paper PDFs
- Added lightweight paper text cleaning
- Added heuristic paper title extraction
- Added `load_pdf_node` to the LangGraph workflow
- Updated `PaperState` to support PDF-based paper analysis
- Organized the code into `nodes`, `tools`, `states`, and `graph`
- Generated structured Markdown reports from real PDF papers

Current workflow:

```text
local PDF file
        ↓
load_pdf_node
        ↓
PDF text extraction
        ↓
paper title extraction
        ↓
paper text cleaning
        ↓
summarize_paper_node
        ↓
critique_paper_node
        ↓
generate_report_node
        ↓
Markdown report
```

### Day 3

Extended the project from full-paper summarization to basic retrieval preparation for RAG.

Main features:

- Added text chunking support for cleaned paper text
- Implemented overlapping text chunks with chunk metadata
- Added a simple TF-IDF based retriever
- Supported top-k relevant chunk retrieval for user queries
- Added test scripts for text splitting and retrieval
- Connected PDF loading, text cleaning, chunking, and simple retrieval into a local test pipeline
- Prepared the project foundation for future embedding-based retrieval and RAG question answering

Current retrieval preparation workflow:

```text
local PDF file
        ↓
load_pdf_text
        ↓
clean_paper_text
        ↓
split_text_into_chunks
        ↓
TF-IDF vectorization
        ↓
retrieve_top_k
        ↓
relevant paper chunks
```

### Day 4/5

Polished the LangGraph-based RAG pipeline into a more reproducible and debuggable paper analysis system.

Main features:

- Cleaned the main CLI entry point.
- Added `--top-k` argument for controlling the number of retrieved chunks.
- Added PDF path validation.
- Standardized `PaperState` fields across the pipeline.
- Added retrieval evidence tracking in the final Markdown report.
- Added report writer utilities for saving Markdown reports.
- Added an end-to-end pipeline smoke test.

Current Workflow:

```text
PDF path + query + top_k
        ↓
load_pdf_node
        ↓
split_text_node
        ↓
retrieve_context_node
        ↓
summarize_paper_node
        ↓
critique_paper_node
        ↓
generate_report_node
        ↓
Markdown report saved to outputs/
```

## Day 6

Upgraded the retrieval layer from a single TF-IDF retriever to a modular retriever architecture.

Main features:

- Added a pluggable retriever interface.
- Refactored the original TF-IDF retriever into `TfidfRetriever`.
- Added `EmbeddingRetriever` based on `sentence-transformers`.
- Added `RetrieverFactory` for switching retrieval strategies.
- Added CLI options:
  - `--retriever-type`
  - `--embedding-model`
  - `--top-k`
- Added a retriever comparison script.

# Retriever Types
```text
tfidf       keyword-based retrieval using TF-IDF cosine similarity
embedding  semantic retrieval using sentence-transformer embeddings
```

Current Workflow
```text
PDF + query + retriever config
        ↓
PDF parsing
        ↓
text splitting
        ↓
retriever factory
        ↓
TF-IDF retriever or embedding retriever
        ↓
retrieved context
        ↓
LangGraph analysis nodes
        ↓
Markdown report
```

## Test

Test the PDF loader:

```bash
python -m scripts.test_pdf_loader
```

Test text chunking
```bash
python -m scripts.test_text_splitter --pdf ./data/transformer.pdf
```

Test simple retrieval:
```bash
python -m scripts.test_retriever --pdf ./data/transformer.pdf --query "multi-head attention"
```

Test simple RAG based paper report: 
```bash
python -m scripts.test_pipeline_day5 \
  --pdf data/resnet.pdf \
  --query "What is the main contribution and limitation of this paper?" \
  --top-k 3
```

Test upgraded RAG based paper report: (embedding as an example)
```bash
python scripts/test_pipeline.py \
  --pdf data/resnet.pdf \
  --query "What is the main contribution of this paper?" \
  --top-k 3 \
  --retriever-type embedding
  # --retriever-type tfidf
```

## Run(present)
```bash
python -m app.main \
  --pdf data/resnet.pdf \
  --query "What are the main problem, method, contribution, experimental results, and limitations of this paper?" \
  --top-k 3
```

## Run with TF-IDF
```bash
python -m app.main \
  --pdf data/resnet.pdf \
  --query "What is the degradation problem in deep neural networks?" \
  --top-k 5 \
  --retriever-type embedding
```

## Run with Embedding Retrieval
```bash
python -m app.main \
  --pdf data/resnet.pdf \
  --query "What is the degradation problem in deep neural networks?" \
  --top-k 5 \
  --retriever-type embedding
```
## Output

Generated reports are saved under:

```text
outputs/
```