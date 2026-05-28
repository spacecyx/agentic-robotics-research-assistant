# Paper Analysis Report

## Input

- PDF: `data/fastlio2.pdf`
- Query: Which LiDAR and IMU sensors are used by the SLAM system?

## Paper Title

FAST-LIO2: Fast Direct LiDAR-Inertial Odometry

## Retrieval Pipeline

- Retriever Type: tfidf
- Embedding Model: sentence-transformers/all-MiniLM-L6-v2
- Final Top-K: 3
- Retriever Candidate K: 10
- Reranker Type: robotics_tag_prior
- Reranker Top-K: 3
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

1. Which LiDAR and IMU sensors are used by the SLAM system?

## Retrieved Evidence Metadata

[1] chunk_id=35, score=0.2957, rank=1, source=tfidf+robotics_tag_prior_rerank, page_range=(6, 6), section=Unknown, char_range=(29750, 30079)
[2] chunk_id=11, score=0.2875, rank=2, source=tfidf+robotics_tag_prior_rerank, page_range=(2, 2), section=Unknown, char_range=(9350, 10350)
[3] chunk_id=4, score=0.2807, rank=3, source=tfidf+robotics_tag_prior_rerank, page_range=(1, 1), section=Unknown, char_range=(3400, 4400)

## Retrieved Evidence Details

### Rank 1

- Chunk ID: 35
- Final Score: 0.2957
- Source: tfidf+robotics_tag_prior_rerank
- Page Range: 6 - 6
- Section: Unknown
- Char Range: 29750 - 30079

Retrieval / Rerank Metadata:

- Reranker: robotics_tag_prior
- Rank Before Rerank: 1
- Original Retriever Score: 0.14382477372996746
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
re usually performed
before an update.
1) Propagation: Assume the optimal state estimate after fus-
ing the last (i.e., k −1th) LiDAR scan is ¯xk−1 with covariance
matrix ¯Pk−1. The forward propagation is performed upon the
arrival of an IMU measurem

[TRUNCATED] Only the first part of the paper is used in this Day 2 prototype.
```

### Rank 2

- Chunk ID: 11
- Final Score: 0.2875
- Source: tfidf+robotics_tag_prior_rerank
- Page Range: 2 - 2
- Section: Unknown
- Char Range: 9350 - 10350

Retrieval / Rerank Metadata:

- Reranker: robotics_tag_prior
- Rank Before Rerank: 2
- Original Retriever Score: 0.1321510006337379
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
nline]. Available: https://github.com/hku-mars/ikd-Tree
with aggressive motion and in very cluttered environ-
ments. We term this raw points based registration as a
direct method in analogy to visual SLAM [21]. The elim-
ination of a hand-engineered feature extraction makes the
system naturally applicable to different LiDAR sensors.
3) We integrate these two key techniques into a full tightly
coupled lidar-inertial odometry system FAST-LIO [22] we
recently developed. The system uses an IMU to compen-
sate each point’s motion via a rigorous back-propagation
step and estimates the system’s full state via an on-
manifold iterated Kalman ﬁlter. The new system is termed
as FAST-LIO2 and is open-sourced at Github 2 to beneﬁt
the community.
4) We conduct various experiments to evaluate the effective-
ness of the developed ikd-Tree, the direct point registra-
tion, and the overall system. Experiments on 18 sequences
of various sizes show that ikd-Tree achieves superior per-
formance against ex
```

### Rank 3

- Chunk ID: 4
- Final Score: 0.2807
- Source: tfidf+robotics_tag_prior_rerank
- Page Range: 1 - 1
- Section: Unknown
- Char Range: 3400 - 4400

Retrieval / Rerank Metadata:

- Reranker: robotics_tag_prior
- Rank Before Rerank: 3
- Original Retriever Score: 0.12246918203508883
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
doi.org/10.1109/TRO.2022.3141876.
Digital Object Identiﬁer 10.1109/TRO.2022.3141876
xk State x at the kth LiDAR scan end time.
x, ˆx,¯x Ground-true, propagated, and updated value of
state x.
˜x Error between ground-true state x and its
estimation ˆx.
ˆxκ Estimate of the state x in the κth iteration of the
iterated Kalman ﬁlter.
I. I NTRODUCTION
B
UILDING a dense 3-D map of an unknown environment
in real-time and simultaneously localizing in the map (i.e.,
SLAM) is crucial for autonomous robots to navigate in the
unknown environment safely. The localization provides state
feedback for the robot onboard controllers, while the dense 3-D
map provides necessary information about the environment (i.e.,
free space and obstacles) for trajectory planning. Vision-based
SLAM [1]–[4] is very accurate in localization but maintains only
a sparse feature map and suffers from illumination variation
and severe motion blur. On the other hand, real-time dense
mapping [5]–[8] based on visual sensors at hi
```

## Retrieved Context Passed to LLM

```text
[Source 1 | chunk_id=35 | page=6 | section=Unknown | score=0.2957 | rank=1 | source=tfidf+robotics_tag_prior_rerank]
re usually performed
before an update.
1) Propagation: Assume the optimal state estimate after fus-
ing the last (i.e., k −1th) LiDAR scan is ¯xk−1 with covariance
matrix ¯Pk−1. The forward propagation is performed upon the
arrival of an IMU measurem

[TRUNCATED] Only the first part of the paper is used in this Day 2 prototype.

[Source 2 | chunk_id=11 | page=2 | section=Unknown | score=0.2875 | rank=2 | source=tfidf+robotics_tag_prior_rerank]
nline]. Available: https://github.com/hku-mars/ikd-Tree
with aggressive motion and in very cluttered environ-
ments. We term this raw points based registration as a
direct method in analogy to visual SLAM [21]. The elim-
ination of a hand-engineered feature extraction makes the
system naturally applicable to different LiDAR sensors.
3) We integrate these two key techniques into a full tightly
coupled lidar-inertial odometry system FAST-LIO [22] we
recently developed. The system uses an IMU to compen-
sate each point’s motion via a rigorous back-propagation
step and estimates the system’s full state via an on-
manifold iterated Kalman ﬁlter. The new system is termed
as FAST-LIO2 and is open-sourced at Github 2 to beneﬁt
the community.
4) We conduct various experiments to evaluate the effective-
ness of the developed ikd-Tree, the direct point registra-
tion, and the overall system. Experiments on 18 sequences
of various sizes show that ikd-Tree achieves superior per-
formance against ex

[Source 3 | chunk_id=4 | page=1 | section=Unknown | score=0.2807 | rank=3 | source=tfidf+robotics_tag_prior_rerank]
doi.org/10.1109/TRO.2022.3141876.
Digital Object Identiﬁer 10.1109/TRO.2022.3141876
xk State x at the kth LiDAR scan end time.
x, ˆx,¯x Ground-true, propagated, and updated value of
state x.
˜x Error between ground-true state x and its
estimation ˆx.
ˆxκ Estimate of the state x in the κth iteration of the
iterated Kalman ﬁlter.
I. I NTRODUCTION
B
UILDING a dense 3-D map of an unknown environment
in real-time and simultaneously localizing in the map (i.e.,
SLAM) is crucial for autonomous robots to navigate in the
unknown environment safely. The localization provides state
feedback for the robot onboard controllers, while the dense 3-D
map provides necessary information about the environment (i.e.,
free space and obstacles) for trajectory planning. Vision-based
SLAM [1]–[4] is very accurate in localization but maintains only
a sparse feature map and suffers from illumination variation
and severe motion blur. On the other hand, real-time dense
mapping [5]–[8] based on visual sensors at hi
```

## Paper Summary

LOCAL_FAKE_SUMMARY normal 2c

## Technical Critique

LOCAL_FAKE_CRITIQUE normal 2c





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
