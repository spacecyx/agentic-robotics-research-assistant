# Paper Analysis Report

## Input

- PDF: `data/fastlio2.pdf`
- Query: What dataset and metrics are used?

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
- Use Query Expansion: True
- Query Expansion Max Queries: 4
- Multi-query Per-query K: 10
- Multi-query RRF K: 60

## Expanded Queries

1. What dataset and metrics are used?

## Retrieved Evidence Metadata

[1] chunk_id=35, score=0.0164, rank=1, source=tfidf+multi_query, page_range=(6, 6), section=Unknown, char_range=(29750, 30079)
[2] chunk_id=14, score=0.0161, rank=2, source=tfidf+multi_query, page_range=(2, 3), section=Unknown, char_range=(11900, 12900)

## Retrieved Evidence Details

### Rank 1

- Chunk ID: 35
- Final Score: 0.0164
- Source: tfidf+multi_query
- Page Range: 6 - 6
- Section: Unknown
- Char Range: 29750 - 30079

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

- Multi-query: True
- Matched Query Count: 1
- Best Original Rank: 1
- Best Original Score: 0.16627150051800518
- Original Ranks: [1]
- Original Scores: [0.16627150051800518]
- Matched Queries: ['What dataset and metrics are used?']

Excerpt:

```text
re usually performed
before an update.
1) Propagation: Assume the optimal state estimate after fus-
ing the last (i.e., k −1th) LiDAR scan is ¯xk−1 with covariance
matrix ¯Pk−1. The forward propagation is performed upon the
arrival of an IMU measurem

[TRUNCATED] Only the first part of the paper is used in this Day 2 prototype.
```

### Rank 2

- Chunk ID: 14
- Final Score: 0.0161
- Source: tfidf+multi_query
- Page Range: 2 - 3
- Section: Unknown
- Char Range: 11900 - 12900

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

- Multi-query: True
- Matched Query Count: 1
- Best Original Rank: 2
- Best Original Score: 0.09478342715067753
- Original Ranks: [2]
- Original Scores: [0.09478342715067753]
- Matched Queries: ['What dataset and metrics are used?']

Excerpt:

```text
e odometry, multiple scans are combined into a sweep, which
is then registered and merged to a global map (i.e., mapping).
In this process, the map points are used to build a k-d tree
that enables a very efﬁcient k-nearest neighbor search ( kNN
search). Then, the point cloud registration is achieved by the
iterative closest point (ICP) [24]–[26] method. In order to lower
the time for k-d tree building, the map points are downsampled
2[Online]. Available: https://github.com/hku-mars/FAST_LIO
Authorized licensed use limited to: Southeast University. Downloaded on July 13,2025 at 08:34:57 UTC from IEEE Xplore.  Restrictions apply.
XU et al.: FAST-LIO2: FAST DIRECT LIDAR-INERTIAL ODOMETRY 2055
at a prescribed resolution. The optimized mapping process is
typically performed at a much low rate (1–2 Hz).
Subsequent LiDAR odometry works keep a framework sim-
ilar to LOAM. For example, Lego-LOAM [27] introduces a
ground point segmentation to lower the computation load and a
loop closure module
```

## Retrieved Context Passed to LLM

```text
[Source 1 | chunk_id=35 | page=6 | section=Unknown | score=0.0164 | rank=1 | source=tfidf+multi_query]
re usually performed
before an update.
1) Propagation: Assume the optimal state estimate after fus-
ing the last (i.e., k −1th) LiDAR scan is ¯xk−1 with covariance
matrix ¯Pk−1. The forward propagation is performed upon the
arrival of an IMU measurem

[TRUNCATED] Only the first part of the paper is used in this Day 2 prototype.

[Source 2 | chunk_id=14 | page=2-3 | section=Unknown | score=0.0161 | rank=2 | source=tfidf+multi_query]
e odometry, multiple scans are combined into a sweep, which
is then registered and merged to a global map (i.e., mapping).
In this process, the map points are used to build a k-d tree
that enables a very efﬁcient k-nearest neighbor search ( kNN
search). Then, the point cloud registration is achieved by the
iterative closest point (ICP) [24]–[26] method. In order to lower
the time for k-d tree building, the map points are downsampled
2[Online]. Available: https://github.com/hku-mars/FAST_LIO
Authorized licensed use limited to: Southeast University. Downloaded on July 13,2025 at 08:34:57 UTC from IEEE Xplore.  Restrictions apply.
XU et al.: FAST-LIO2: FAST DIRECT LIDAR-INERTIAL ODOMETRY 2055
at a prescribed resolution. The optimized mapping process is
typically performed at a much low rate (1–2 Hz).
Subsequent LiDAR odometry works keep a framework sim-
ilar to LOAM. For example, Lego-LOAM [27] introduces a
ground point segmentation to lower the computation load and a
loop closure module
```

## Paper Summary

LOCAL_FAKE_SUMMARY weak 2c

## Technical Critique

LOCAL_FAKE_CRITIQUE weak 2c

## Retrieval Quality Warnings

- Query expansion retry was triggered 1 time(s).
- Retrieved evidence remained weak after retry; the report was generated with a warning.
- Final retrieval quality: weak.
- Reason: weak_retrieval_evidence_after_retry.



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
