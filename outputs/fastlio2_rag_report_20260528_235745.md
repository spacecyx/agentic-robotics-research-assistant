# Paper Analysis Report

## Input

- PDF: `data/fastlio2.pdf`
- Query: Which LiDAR-inertial odometry method is proposed?

## Paper Title

FAST-LIO2: Fast Direct LiDAR-Inertial Odometry

## Retrieval Pipeline

- Retriever Type: tfidf
- Embedding Model: sentence-transformers/all-MiniLM-L6-v2
- Final Top-K: 2
- Retriever Candidate K: 10
- Reranker Type: none
- Reranker Top-K: 2
- Retriever Weight: 0.7
- Hybrid Alpha: 
- Max Context Chars: 
- Max Chunk Chars: 
- FAISS Index Dir: 
- Rebuild FAISS Index: False
- Use Query Expansion: False
- Query Expansion Max Queries: 4
- Multi-query Per-query K: 10
- Multi-query RRF K: 60

## Expanded Queries

1. Which LiDAR-inertial odometry method is proposed?

## Retrieved Evidence Metadata

[1] chunk_id=16, score=0.2297, rank=1, source=tfidf, page_range=(3, 3), section=Unknown, char_range=(13600, 14600)
[2] chunk_id=19, score=0.2048, rank=2, source=tfidf, page_range=(3, 3), section=Unknown, char_range=(16150, 17150)

## Retrieved Evidence Details

### Rank 1

- Chunk ID: 16
- Final Score: 0.2297
- Source: tfidf
- Page Range: 3 - 3
- Section: Unknown
- Char Range: 13600 - 14600

Retrieval / Rerank Metadata:

- Reranker: N/A
- Rank Before Rerank: N/A
- Original Retriever Score: N/A
- Normalized Retriever Score: N/A
- Keyword Rerank Score: N/A
- Fusion Score: N/A

FAISS / Embedding Metadata:

- FAISS Score: N/A
- Embedding Score: N/A
- FAISS Index Dir: N/A

Multi-query Metadata:

- Multi-query: False
- Matched Query Count: N/A
- Best Original Rank: N/A
- Best Original Score: N/A
- Original Ranks: N/A
- Original Scores: N/A
- Matched Queries: N/A

Excerpt:

```text
good initial
pose required by ICP . More tightly coupled LiDAR-inertial
fusion works [17], [28]–[30] perform odometry i nas m a l ls i z e
local map consisting of a ﬁxed number of recent LiDAR scans
(or keyframes). Compared with scan-to-scan registration, the
scan to local map registration is usually more accurate by using
more recent information. More speciﬁcally, LIOM [28] presents
a tightly coupled LiDAR inertial fusion method where the IMU
preintegrations are introduced into the odometry. LILI-OM [17]
develops a new feature extraction method for nonrepetitive
scanning LiDARs and performs scan registration in a small
map consisting of 20 recent LiDAR scans for the odometry.
The odometry of LIO-SAM [29] requires a nine-axis IMU to
produce attitude measurement as the prior of scan registration
within a small local map. LINS [30] introduces a tightly coupled
iterated Kalman ﬁlter and robocentric formula into the LiDAR
pose optimization in the odometry. Since the local map in the
previo
```

### Rank 2

- Chunk ID: 19
- Final Score: 0.2048
- Source: tfidf
- Page Range: 3 - 3
- Section: Unknown
- Char Range: 16150 - 17150

Retrieval / Rerank Metadata:

- Reranker: N/A
- Rank Before Rerank: N/A
- Original Retriever Score: N/A
- Normalized Retriever Score: N/A
- Keyword Rerank Score: N/A
- Fusion Score: N/A

FAISS / Embedding Metadata:

- FAISS Score: N/A
- Embedding Score: N/A
- FAISS Index Dir: N/A

Multi-query Metadata:

- Multi-query: False
- Matched Query Count: N/A
- Best Original Rank: N/A
- Best Original Score: N/A
- Original Ranks: N/A
- Original Scores: N/A
- Matched Queries: N/A

Excerpt:

```text
e
accuracy and robustness of odometry and mapping, especially
when a new scan contains no prominent features (e.g., due to
small FoV and/or structure-less environments). Compared with
the previous tightly coupled LiDAR-inertial methods, which all
use feature points, our method is more lightweight and achieves
increased mapping rate and odometry accuracy, and eliminates
the need for parameter tuning for feature extraction.
The idea of directly registering raw points in our work has
been explored in LION [32], which is, however, a loosely
coupled method as reviewed previously. This idea is also very
similar to the generalized-ICP (G-ICP) proposed in [26], where
a point is registered to a small local plane in the map. This
ultimately assumes that the environment is smooth and hence
can be viewed as a plane locally. However, the computation load
of G-ICP is usually large [33]. Other works based on normal
distribution transformation (NDT) [34]–[36] also register raw
points, but NDT has lowe
```

## Retrieved Context Passed to LLM

```text
[Source 1 | chunk_id=16 | page=3 | section=Unknown | score=0.2297 | rank=1 | source=tfidf]
good initial
pose required by ICP . More tightly coupled LiDAR-inertial
fusion works [17], [28]–[30] perform odometry i nas m a l ls i z e
local map consisting of a ﬁxed number of recent LiDAR scans
(or keyframes). Compared with scan-to-scan registration, the
scan to local map registration is usually more accurate by using
more recent information. More speciﬁcally, LIOM [28] presents
a tightly coupled LiDAR inertial fusion method where the IMU
preintegrations are introduced into the odometry. LILI-OM [17]
develops a new feature extraction method for nonrepetitive
scanning LiDARs and performs scan registration in a small
map consisting of 20 recent LiDAR scans for the odometry.
The odometry of LIO-SAM [29] requires a nine-axis IMU to
produce attitude measurement as the prior of scan registration
within a small local map. LINS [30] introduces a tightly coupled
iterated Kalman ﬁlter and robocentric formula into the LiDAR
pose optimization in the odometry. Since the local map in the
previo

[Source 2 | chunk_id=19 | page=3 | section=Unknown | score=0.2048 | rank=2 | source=tfidf]
e
accuracy and robustness of odometry and mapping, especially
when a new scan contains no prominent features (e.g., due to
small FoV and/or structure-less environments). Compared with
the previous tightly coupled LiDAR-inertial methods, which all
use feature points, our method is more lightweight and achieves
increased mapping rate and odometry accuracy, and eliminates
the need for parameter tuning for feature extraction.
The idea of directly registering raw points in our work has
been explored in LION [32], which is, however, a loosely
coupled method as reviewed previously. This idea is also very
similar to the generalized-ICP (G-ICP) proposed in [26], where
a point is registered to a small local plane in the map. This
ultimately assumes that the environment is smooth and hence
can be viewed as a plane locally. However, the computation load
of G-ICP is usually large [33]. Other works based on normal
distribution transformation (NDT) [34]–[36] also register raw
points, but NDT has lowe
```

## Paper Summary

[LLM generation failed in summarize_paper_node: timeout. Please check trace log for details.]

## Technical Critique

should not matter



## Evidence Verification

- Method: lexical_overlap weak evidence alignment.
- Claims Checked: 0
- Average Support Score: 0.000
- Status: skipped, no_claims_extracted
- No obvious weakly supported claims detected by lexical evidence check.

## Generation Warnings

Some LLM generation steps failed and fallback text was used so the report could still be generated.

- Node: summarize_paper_node; Error Type: timeout; Attempts: 0; Latency(ms): 0.00; Timeout(s): 60; Max Retries: 2

## Final Notes

This report was generated by a LangGraph-based RAG pipeline.

The current pipeline includes:

```text
PDF loading
  -> text splitting
  -> candidate retrieval
  -> optional FAISS vector retrieval
  -> optional query expansion / multi-query retrieval
  -> optional reranking
  -> context construction
  -> evidence-aware report generation
```

The analysis is grounded in the retrieved paper chunks listed above.
