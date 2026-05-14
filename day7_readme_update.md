# Day 7 Progress: Modular RAG Retrieval, Reranking, and Evaluation

Day 7 upgraded the project from a basic RAG demo into a more modular, testable, and evaluation-oriented paper RAG system.

The system now supports multiple retrieval strategies, two-stage reranking, context construction, evidence-aware answer generation, and weak retrieval evaluation with Hit@K and MRR@K.

---

## 1. Modular Retriever Layer

Implemented a unified retriever layer for different retrieval strategies.

Currently supported retrievers:

- `TF-IDF Retriever`
- `Embedding Retriever`
- `Hybrid Retriever`

The Hybrid Retriever combines lexical matching and semantic retrieval:

```text
Hybrid Score = alpha * Embedding Score + (1 - alpha) * TF-IDF Score
```

This makes the retrieval layer easier to extend. Future retrievers such as BM25, FAISS, vector databases, or multi-route retrieval can be added without changing the main RAG workflow.

---

## 2. Retriever Factory

Added a Retriever Factory to decouple retrieval strategy selection from business logic.

```text
query + chunks
      ↓
Retriever Factory
      ↓
TF-IDF / Embedding / Hybrid Retriever
      ↓
retrieval results
```

This design allows different retrieval strategies to be switched through configuration instead of modifying the core pipeline code.

---

## 3. Hybrid Retrieval

Implemented Hybrid Retrieval to combine the strengths of TF-IDF and Embedding retrieval.

- TF-IDF is useful for exact keyword matching, technical terms, formulas, and paper-specific phrases.
- Embedding retrieval is useful for semantic similarity and paraphrased queries.
- Hybrid retrieval fuses both scores to improve retrieval robustness.

This is useful for paper RAG because academic papers often contain both exact technical terms and semantic descriptions.

---

## 4. Reranker Layer

Added a second-stage reranking layer after first-stage retrieval.

Implemented modules:

- `BaseReranker`
- `KeywordReranker`
- `ScoreFusionReranker`
- `RerankerFactory`

The reranking workflow is:

```text
query
  ↓
first-stage retriever retrieves candidate chunks
  ↓
reranker reorders candidate chunks
  ↓
top-ranked chunks are passed to the context builder
```

The current reranker is lightweight and keyword-based, but the interface is designed to support future Cross-Encoder rerankers or LLM-based reranking.

---

## 5. Context Builder

Added a `ContextBuilder` module to construct LLM-ready context from retrieved and reranked chunks.

Main responsibilities:

- Deduplicate retrieved chunks
- Control maximum context length
- Preserve chunk metadata
- Preserve retrieval score and rank
- Generate structured evidence information

This separates retrieval from prompt construction and makes the RAG pipeline easier to debug and extend.

---

## 6. Answer Generator

Added an `AnswerGenerator` module for citation-aware question answering.

The QA pipeline is:

```text
query
  ↓
retrieval
  ↓
reranking
  ↓
context construction
  ↓
LLM answer generation
  ↓
answer with evidence
```

The answer generation step is grounded in retrieved context and can attach evidence metadata such as:

- `chunk_id`
- retrieval score
- rank
- source
- character range

This helps reduce hallucination risk and makes the generated answer easier to verify.

---

## 7. Retrieval Evaluation

Upgraded the retrieval evaluation script from manual comparison to weakly supervised evaluation.

Supported metrics:

- `Hit@1`
- `Hit@3`
- `Hit@K`
- `MRR@K`
- `Average Rank`

Evaluated retrieval methods include:

- `tfidf`
- `embedding`
- `hybrid`
- `tfidf + keyword_rerank`
- `hybrid + score_fusion_rerank`

The evaluation logic is keyword-based weak evaluation. It checks whether retrieved chunks contain expected keywords. This is useful for rough retrieval comparison, but it is not a strict semantic evaluation.

---

## 8. Current RAG Pipeline

The current system architecture is:

```text
PDF
  ↓
PDF Loader
  ↓
Text Splitter
  ↓
Retriever Factory
  ↓
TF-IDF / Embedding / Hybrid Retriever
  ↓
Reranker Factory
  ↓
Keyword / Score Fusion Reranker
  ↓
Context Builder
  ↓
LLM-based Summary / Critique / Answer Generation
  ↓
Markdown Report
```

---

## 9. Engineering Value

This update makes the project more than a simple RAG demo.

The system now demonstrates:

- Modular retrieval design
- Factory-based strategy selection
- Hybrid retrieval
- Two-stage retrieval and reranking
- Context construction
- Evidence-aware generation
- Retrieval evaluation with Hit@K and MRR@K
- Clear extension points for production-style RAG systems

From an interview perspective, this allows the project to be described as a modular RAG system rather than a single-script demo.

---

## 10. Known Limitations

Current limitations:

- The evaluation is keyword-based weak evaluation, not semantic evaluation.
- The reranker is still lightweight and does not use a trained Cross-Encoder model.
- The vector retrieval layer has not yet been optimized with FAISS or a persistent vector database.
- The current system is mainly designed for paper-level RAG, not large-scale multi-document retrieval.
- Report generation still depends on retrieved context quality, so poor retrieval can still lead to incomplete summaries.

---

## 11. Future Plus Work

Potential improvements:

- Add FAISS-based local vector index persistence
- Add Cross-Encoder reranker
- Add query expansion or multi-query retrieval
- Add RAGAS-style evaluation metrics
- Add per-query evaluation detail reports
- Add configuration files for reproducible experiments
- Add support for multi-paper knowledge bases
- Add a lightweight CLI for running retrieval, QA, and evaluation

---

## Suggested Git Commit

```bash
git add .
git commit -m "feat: add reranking, context building and retrieval evaluation"
git push
```
