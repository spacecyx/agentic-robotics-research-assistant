# Paper Analysis Report

## Input

- PDF: `data/fastlio2.pdf`
- Query: Which LiDAR SLAM method is proposed?

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

1. Which LiDAR SLAM method is proposed?

## Retrieved Evidence Metadata

[1] chunk_id=19, score=0.1360, rank=1, source=tfidf, page_range=(3, 3), section=Unknown, char_range=(16150, 17150)
[2] chunk_id=13, score=0.1344, rank=2, source=tfidf, page_range=(2, 2), section=Unknown, char_range=(11050, 12050)

## Retrieved Evidence Details

### Rank 1

- Chunk ID: 19
- Final Score: 0.1360
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

### Rank 2

- Chunk ID: 13
- Final Score: 0.1344
- Source: tfidf
- Page Range: 2 - 2
- Section: Unknown
- Char Range: 11050 - 12050

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
orks. We give an overview of the
complete system pipeline and the details of each key compo-
nents in Sections III, IV, and V, respectively. The benchmark
comparison on open datasets are presented in Section VI, and
the real-world experiments are reported in Section VII. Finally,
Section IX concludes this article.
II. R ELA TEDWORKS
A. LiDAR(-Inertial) Odometry
Existing works on 3-D LiDAR SLAM typically inherit the
LOAM structure proposed in [23]. It consists of three main
modules: feature extraction, odometry, and mapping. In order
to reduce the computation load, a new LiDAR scan ﬁrst goes
through feature points (i.e., edge and plane) extraction based on
the local smoothness. Then, theodometry module (scan-to-scan)
matches feature points from two consecutive scans to obtain a
rough yet real-time (e.g., 10 Hz) LiDAR pose odometry. With
the odometry, multiple scans are combined into a sweep, which
is then registered and merged to a global map (i.e., mapping).
In this process, the map po
```

## Retrieved Context Passed to LLM

```text
[Source 1 | chunk_id=19 | page=3 | section=Unknown | score=0.1360 | rank=1 | source=tfidf]
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

[Source 2 | chunk_id=13 | page=2 | section=Unknown | score=0.1344 | rank=2 | source=tfidf]
orks. We give an overview of the
complete system pipeline and the details of each key compo-
nents in Sections III, IV, and V, respectively. The benchmark
comparison on open datasets are presented in Section VI, and
the real-world experiments are reported in Section VII. Finally,
Section IX concludes this article.
II. R ELA TEDWORKS
A. LiDAR(-Inertial) Odometry
Existing works on 3-D LiDAR SLAM typically inherit the
LOAM structure proposed in [23]. It consists of three main
modules: feature extraction, odometry, and mapping. In order
to reduce the computation load, a new LiDAR scan ﬁrst goes
through feature points (i.e., edge and plane) extraction based on
the local smoothness. Then, theodometry module (scan-to-scan)
matches feature points from two consecutive scans to obtain a
rough yet real-time (e.g., 10 Hz) LiDAR pose odometry. With
the odometry, multiple scans are combined into a sweep, which
is then registered and merged to a global map (i.e., mapping).
In this process, the map po
```

## Paper Summary

LOCAL_FAKE_SUMMARY default path

## Technical Critique

LOCAL_FAKE_CRITIQUE default path





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
