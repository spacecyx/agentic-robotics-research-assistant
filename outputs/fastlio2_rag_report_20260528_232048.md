# Paper Analysis Report

## Input

- PDF: `data/fastlio2.pdf`
- Query: Which LiDAR SLAM odometry method reports real-time performance and latency?

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

1. Which LiDAR SLAM odometry method reports real-time performance and latency?

## Retrieved Evidence Metadata

[1] chunk_id=6, score=0.3362, rank=1, source=tfidf+robotics_tag_prior_rerank, page_range=(1, 1), section=Unknown, char_range=(5100, 6100)
[2] chunk_id=13, score=0.3053, rank=2, source=tfidf+robotics_tag_prior_rerank, page_range=(2, 2), section=Unknown, char_range=(11050, 12050)
[3] chunk_id=4, score=0.2890, rank=3, source=tfidf+robotics_tag_prior_rerank, page_range=(1, 1), section=Unknown, char_range=(3400, 4400)

## Retrieved Evidence Details

### Rank 1

- Chunk ID: 6
- Final Score: 0.3362
- Source: tfidf+robotics_tag_prior_rerank
- Page Range: 1 - 1
- Section: Unknown
- Char Range: 5100 - 6100

Retrieval / Rerank Metadata:

- Reranker: robotics_tag_prior
- Rank Before Rerank: 1
- Original Retriever Score: 0.20169023745577558
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
, and high performance
(centimeter accuracy at hundreds of meters measuring range)
solid-state LiDARs [14], [15], drawing much recent research
interests [16]–[20]. The considerably reduced cost, size, weight,
and power of these LiDARs hold the potential to beneﬁt a broad
scope of existing and emerging robotic applications.
The central requirement for adopting LiDAR-based SLAM
approaches to these widespread applications is to obtain ac-
curate, low-latency state estimation, and dense 3-D map with
limited onboard computation resources. However, efﬁcient and
accurate LiDAR odometry and mapping are still challenging
problems, which are given as follows.
1) Current LiDAR sensors produce a large amount of 3-D
points from hundreds of thousands to millions per second.
Processing such a large amount of data in real time and
1552-3098 © 2022 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more
```

### Rank 2

- Chunk ID: 13
- Final Score: 0.3053
- Source: tfidf+robotics_tag_prior_rerank
- Page Range: 2 - 2
- Section: Unknown
- Char Range: 11050 - 12050

Retrieval / Rerank Metadata:

- Reranker: robotics_tag_prior
- Rank Before Rerank: 3
- Original Retriever Score: 0.15754867497290545
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

### Rank 3

- Chunk ID: 4
- Final Score: 0.2890
- Source: tfidf+robotics_tag_prior_rerank
- Page Range: 1 - 1
- Section: Unknown
- Char Range: 3400 - 4400

Retrieval / Rerank Metadata:

- Reranker: robotics_tag_prior
- Rank Before Rerank: 4
- Original Retriever Score: 0.134268881928973
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
[Source 1 | chunk_id=6 | page=1 | section=Unknown | score=0.3362 | rank=1 | source=tfidf+robotics_tag_prior_rerank]
, and high performance
(centimeter accuracy at hundreds of meters measuring range)
solid-state LiDARs [14], [15], drawing much recent research
interests [16]–[20]. The considerably reduced cost, size, weight,
and power of these LiDARs hold the potential to beneﬁt a broad
scope of existing and emerging robotic applications.
The central requirement for adopting LiDAR-based SLAM
approaches to these widespread applications is to obtain ac-
curate, low-latency state estimation, and dense 3-D map with
limited onboard computation resources. However, efﬁcient and
accurate LiDAR odometry and mapping are still challenging
problems, which are given as follows.
1) Current LiDAR sensors produce a large amount of 3-D
points from hundreds of thousands to millions per second.
Processing such a large amount of data in real time and
1552-3098 © 2022 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more

[Source 2 | chunk_id=13 | page=2 | section=Unknown | score=0.3053 | rank=2 | source=tfidf+robotics_tag_prior_rerank]
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

[Source 3 | chunk_id=4 | page=1 | section=Unknown | score=0.2890 | rank=3 | source=tfidf+robotics_tag_prior_rerank]
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

LOCAL_FAKE_SUMMARY: robotics tag prior smoke test

## Technical Critique

LOCAL_FAKE_CRITIQUE: robotics tag prior smoke test



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
