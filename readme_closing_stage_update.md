### Closing Stage

Finished the core closing tasks for the paper RAG system.

This stage upgraded the project from a modular retrieval system into a more complete retrieval-to-generation pipeline with reranking, context construction, citation-aware answering, and extended retrieval evaluation.

Main features:

- Added a modular reranker layer.
- Implemented `KeywordReranker` as a lightweight reranking baseline.
- Implemented `ScoreFusionReranker` to combine original retriever scores with keyword rerank scores.
- Added `RerankerFactory` for switching reranking strategies.
- Added `ContextBuilder` to construct LLM-ready context from retrieved and reranked chunks.
- Added structured evidence metadata, including `chunk_id`, score, rank, source, and character range.
- Added `AnswerGenerator` for grounded question answering based on retrieved context.
- Upgraded the retrieval evaluation script to compare original retrievers and reranked retrievers.
- Added evaluation support for `tfidf+keyword_rerank` and `hybrid+score_fusion_rerank`.

Closing-stage workflow:

```text
PDF + query
        ↓
load_pdf_node
        ↓
split_text_node
        ↓
Retriever Factory
        ↓
TF-IDF / Embedding / Hybrid Retriever
        ↓
Reranker Factory
        ↓
Keyword / Score Fusion Reranker
        ↓
ContextBuilder
        ↓
retrieved context + structured evidence
        ↓
summarize_paper_node / critique_paper_node / AnswerGenerator
        ↓
Markdown report or citation-aware answer
```

Retrieval evaluation workflow:

```text
evaluation queries
        ↓
TF-IDF / Embedding / Hybrid retrieval
        ↓
optional reranking
        ↓
keyword-based weak matching
        ↓
Hit@1 / Hit@3 / Hit@K / MRR@K / Average Rank
        ↓
retriever comparison table
```

Supported evaluated methods:

```text
tfidf
embedding
hybrid
tfidf+keyword_rerank
hybrid+score_fusion_rerank
```

Current limitations:

- The evaluation is still keyword-based weak evaluation, not strict semantic evaluation.
- The current reranker is lightweight and does not yet use a Cross-Encoder model.
- The vector index is not yet persisted with FAISS or a vector database.
- The system is still focused on single-paper RAG rather than multi-paper knowledge bases.

This closing stage makes the project suitable for interview presentation as a modular RAG system rather than a simple retrieval demo.
