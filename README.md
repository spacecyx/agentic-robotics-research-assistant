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

## Usage

Test the PDF loader:

```bash
python -m scripts.test_pdf_loader
```

Run the full paper analysis workflow:

```bash
python -m app.main --pdf ./data/resnet.pdf
```

```bash
python -m app.main --pdf ./data/transformer.pdf
```

Test text chunking
```bash
python -m scripts.test_text_splitter --pdf ./data/transformer.pdf
```

Test simple retrieval:
```bash
python -m scripts.test_retriever --pdf ./data/transformer.pdf --query "multi-head attention"
```

## Output

Generated reports are saved under:

```text
outputs/
```