# Agentic Robotics Research Assistant

面向机器人 / SLAM / 3D 感知论文阅读的 **LangGraph-based RAG workflow**。

输入部分由一篇本地论文 PDF 和一个阅读问题 query 组成，输出是一份带检索证据、技术总结、批判性分析和 trace 信息的 Markdown 报告。当前实现更接近一个面向论文阅读的 RAG workflow，而不是完整 autonomous agent 系统；项目重点放在证据检索、流程可追踪、检索策略对比和失败路径处理上。

## TL;DR

这个项目把一篇 research paper PDF 转换为 evidence-aware Markdown 分析报告。核心思路是：

1. 先检索和重排论文片段，再让 LLM 基于 retrieved evidence 生成总结与评价。
2. 记录 retrieval、rerank、branch decision、LLM invocation 和 evidence verification 的轻量 trace。
3. 为机器人 / SLAM / 3D 感知论文加入 robotics-aware metadata 与 tag-prior rerank。
4. 在检索证据不足或 LLM 调用失败时，保留 fallback / warning，而不是直接中断流程。

## Project Overview

`Agentic Robotics Research Assistant` 使用 LangGraph 组织论文阅读流程：

```text
PDF -> chunks -> retrieval / rerank -> context -> summary / critique -> verification -> report
```

当前支持的主要能力：

- PDF parsing、文本清洗和 chunking
- TF-IDF / Embedding / Hybrid / FAISS 检索
- query expansion 和 multi-query RRF
- keyword / score fusion / section prior / robotics tag prior rerank
- robotics-aware chunk metadata
- retrieval quality scoring 和可选 conditional branch
- LLM safe invoke、fallback 和 trace logging
- weak evidence alignment，用于检查生成内容和 retrieved evidence 的对应关系
- retriever evaluation，并导出 CSV / Markdown 结果

典型报告包含：

- paper summary
- technical critique
- retrieved evidence
- retrieval / rerank configuration
- query expansion metadata
- retrieval quality warnings
- evidence verification summary

## Why This Project

很多 PDF QA demo 只展示“问一句、答一句”。论文阅读通常需要更完整的上下文：哪些片段支撑了总结？不同检索策略效果如何？检索结果太弱时是否应该重试？LLM 调用失败后是否还能留下可排查的结果？

这个项目把重点放在 RAG workflow 的工程问题上：证据构建、检索对比、条件分支、失败降级和 trace 复现，而不是 UI 或长链 autonomous planning。

## Key Features

- **PDF parsing and cleaning**：读取本地论文 PDF，提取标题并清洗文本。
- **LangGraph workflow**：用节点组织论文分析流程，并保留清晰的 State 传递。
- **Modular retrievers**：支持 TF-IDF、Embedding、Hybrid、FAISS。
- **Query expansion and multi-query RRF**：支持启发式 query expansion、多 query 检索和 RRF-style 融合。
- **Robotics-aware metadata**：为 chunk 标注 sensor、dataset、metric、task、system module 和 deployment constraint 等标签。
- **Reranking**：支持 keyword、score fusion、section prior 和 robotics tag prior reranker。
- **Retrieval quality scoring**：用规则式 scorer 判断 retrieved evidence 是否足够。
- **Conditional branch**：通过 `--enable-conditional-branch` 启用；证据较弱时最多触发一次 query expansion / retrieval retry，context 为空时 fallback。
- **Evidence verifier**：用 lexical overlap 对 summary / critique 的关键句和 retrieved evidence 做 weak evidence alignment。
- **Trace logging**：记录配置、中间状态摘要、retrieval metadata、rerank metadata、branch decision、LLM invocation 和输出路径。
- **Retriever evaluation**：支持 Hit@1、Hit@3、Hit@K、MRR@K、Avg Rank、Latency，并导出 CSV / Markdown。

## System Architecture

默认 workflow 会执行检索、重排、retrieval quality scoring、LLM 生成、evidence verification 和报告写入，但 retrieval quality 只记录结果，不改变主流程路径。

```text
PDF
  -> load_pdf_node
  -> split_text_node
  -> retrieve_context_node
  -> evaluate_retrieval_quality_node
  -> summarize_paper_node
  -> critique_paper_node
  -> verify_evidence_node
  -> generate_report_node
  -> Markdown report
```

启用 `--enable-conditional-branch` 后，`evaluate_retrieval_quality_node` 会参与路径选择：

```text
PDF
  -> load_pdf_node
  -> split_text_node
  -> retrieve_context_node
  -> evaluate_retrieval_quality_node
       |-- good evidence
       |     -> summarize_paper_node
       |     -> critique_paper_node
       |
       |-- weak evidence
       |     -> enable query expansion
       |     -> retrieve_context_node
       |     -> evaluate_retrieval_quality_node
       |     -> summarize_paper_node / critique_paper_node
       |
       |-- empty evidence
       |     -> fallback_generation_node
  -> verify_evidence_node
  -> generate_report_node
  -> Markdown report
```

模块视角：

```text
app/
  main.py        CLI entry point
  graph.py       LangGraph workflow definition
  states.py      shared workflow state
  nodes/         workflow nodes
  tools/         PDF, retrieval, rerank, context, report utilities

scripts/
  evaluation and smoke-test scripts

outputs/
  generated reports, traces, and evaluation results
```

## RAG Pipeline

### Retrievers

**TF-IDF Retriever**  
关键词 baseline，适合术语明确的问题，速度快，便于对比。

**Embedding Retriever**  
基于 `sentence-transformers` 做语义检索，适合 query 和论文原文表述不完全一致的情况。

**Hybrid Retriever**  
融合 TF-IDF 和 embedding 分数，兼顾关键词匹配和语义召回。

**FAISS Retriever**  
使用本地 FAISS 向量索引，避免每次运行重复构建文档 embedding。当前用于 paper-level local retrieval，不是大规模向量检索服务。

### Query Expansion + Multi-query RRF

`HeuristicQueryExpander` 根据规则生成 query variants。`MultiQueryRetriever` 对多个 query 分别检索，再用 RRF-style 分数融合和去重。这个功能可以提高召回，但会增加 per-query latency。

### Retrieval Quality and Conditional Branching

`evaluate_retrieval_quality_node` 使用规则式 scorer 判断 retrieved evidence 是否足够。它不调用 LLM，主要参考：

- retrieved chunk 数量
- top score / average score
- section coverage，尤其是 Experiments / Evaluation / Results 类 section
- robotics tag coverage，例如 sensor / dataset / metric tags

输出中包含 `quality_label` 和 `recommended_action`：

- `good` / `proceed`：继续 summary 和 critique。
- `weak` / `expand_query`：如果还没有 retry，则设置 `use_query_expansion=True`，回到 `retrieve_context_node`，最多重试一次。
- retry 后仍 weak：继续生成报告，但写入 retrieval quality warning。
- `empty` / `fallback`：进入 `fallback_generation_node`，跳过 summary / critique 的 LLM 调用，仍生成报告。

该能力默认只记录 retrieval quality。要让它控制 workflow 路径，需要显式传入 `--enable-conditional-branch`。

### Rerank

对 first-stage candidates 做二次排序。当前包括：

- `keyword`
- `score_fusion`
- `section_prior`
- `robotics_tag_prior`

`section_prior` 使用规则式 query intent classifier，根据 query intent 和 chunk section metadata 给候选结果轻量 bias。

`robotics_tag_prior` 复用 chunk 中的 `robotics_tags` metadata。传感器、数据集、指标或部署相关问题会优先提升包含对应 robotics tags 的候选 chunk。它只对已召回 candidates 重排，不新增召回结果，也不调用 LLM。

### Robotics-aware Metadata

`split_text_into_chunks` 会为每个 `TextChunk` 附加：

- `robotics_tags`
- `robotics_tag_count`
- `robotics_flat_tags`

标签由 `app/tools/robotics_schema.py` 中的规则/词典抽取，覆盖 sensor modality、dataset、metric、task type、system module 和 deployment constraint。它用于 trace、评估和 rerank metadata，不是完整机器人领域知识图谱。

### Evidence Verification

`verify_evidence_node` 在 summary / critique 之后、report 之前运行。当前 verifier 使用 `app/tools/evidence_verifier.py` 中的 lexical overlap 方法，将 summary / critique 中抽取出的 claim-like sentences 与 retrieved evidence chunks 做弱匹配。

输出字段包括：

- `summary_verification`
- `critique_verification`
- `weakly_supported_claims`
- `evidence_alignment_score`

这个模块用于提示哪些生成句子可能缺少 retrieved evidence 支撑。它是 weak evidence alignment，不是严格事实校验，也不保证报告完全无幻觉。

### LLM Safety and Traceability

`summarize_paper_node` 和 `critique_paper_node` 通过 `safe_llm_invoke` 调用 LLM。失败时会记录错误并返回 fallback 文本，避免单次请求中断整个 workflow。

trace JSON 会记录：

- input / config
- chunk 和 retrieval preview
- query expansion metadata
- retrieval quality 和 branch decision
- rerank metadata
- evidence verification summary
- LLM invocation status
- report / trace output path

trace 只保存摘要、preview 和结构化 metadata，不保存完整论文全文、完整 report 或 API key。

## Evaluation

评估脚本：[scripts/evaluate_retrievers.py](scripts/evaluate_retrievers.py)

当前指标：

- Hit@1
- Hit@3
- Hit@K
- MRR@K
- Avg Rank
- Avg Latency(ms)

评估结果默认保存到：

```text
outputs/eval/
```

评估配置：

- PDF: `data/resnet.pdf`
- Eval queries: `data/eval_queries.json`
- Top-K: `5`
- Number of queries: `12`

示例评估结果：

| Method | Hit@1 | Hit@3 | Hit@5 | MRR@5 | Avg Rank | Avg Latency(ms) |
|---|---:|---:|---:|---:|---:|---:|
| tfidf | 0.333 | 0.583 | 0.667 | 0.461 | 3.333 | 0.37 |
| embedding | 0.417 | 0.583 | 0.667 | 0.507 | 3.167 | 4.44 |
| hybrid | 0.417 | 0.500 | 0.667 | 0.496 | 3.333 | 4.76 |
| tfidf+keyword_rerank | 0.417 | 0.667 | 0.750 | 0.544 | 2.917 | 0.90 |
| tfidf+section_prior_rerank | 0.333 | 0.500 | 0.667 | 0.440 | 3.500 | 0.34 |
| tfidf+robotics_tag_prior_rerank | 0.417 | 0.667 | 0.750 | 0.535 | 2.917 | 2.29 |
| hybrid+score_fusion_rerank | 0.333 | 0.500 | 0.750 | 0.471 | 3.333 | 6.54 |
| hybrid+section_prior_rerank | 0.500 | 0.583 | 0.750 | 0.579 | 2.917 | 4.64 |
| hybrid+robotics_tag_prior_rerank | 0.417 | 0.583 | 0.667 | 0.521 | 3.083 | 7.43 |
| hybrid+query_expansion | 0.333 | 0.583 | 0.667 | 0.447 | 3.417 | 17.59 |
| hybrid+query_expansion+score_fusion_rerank | 0.417 | 0.583 | 0.667 | 0.521 | 3.083 | 17.07 |

该表主要用于比较不同 retrieval / rerank 策略在同一小规模评估集上的相对表现，不代表通用 benchmark 性能。

说明：

- 当前 relevance 判断是 keyword-based weak evaluation。
- Latency 不包含 retriever 初始化、embedding 模型加载、FAISS index loading/building。
- Latency 包含每个 method 内部的 query expansion、multi-query retrieval、rerank 成本。
- 后续可以加入 `relevant_chunk_ids`、page citation 和更严格的 faithfulness evaluation。

## Quick Start

### 1. Create Environment

推荐使用 conda：

```bash
conda env create -f environment.yml
conda activate agentic-robotics
```

也可以使用 requirements：

```bash
pip install -r requirements.txt
```

### 2. Configure `.env`

```bash
cp .env.example .env
```

`.env` 示例：

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

### 3. Run Main Workflow

Hybrid retrieval：

```bash
python -m app.main \
  --pdf data/resnet.pdf \
  --query "What are the main problem, method, contribution, experimental results, and limitations of this paper?" \
  --top-k 5 \
  --retriever-type hybrid
```

FAISS retrieval：

```bash
python -m app.tools.build_faiss_index \
  --pdf data/resnet.pdf \
  --index-dir data/index/resnet \
  --embedding-model sentence-transformers/all-MiniLM-L6-v2
```

```bash
python -m app.main \
  --pdf data/resnet.pdf \
  --query "What is residual learning and why does ResNet use shortcut connections?" \
  --top-k 3 \
  --retriever-type faiss \
  --faiss-index-dir data/index/resnet
```

Query expansion：

```bash
python -m app.main \
  --pdf data/resnet.pdf \
  --query "What are the main method and limitations of ResNet?" \
  --top-k 3 \
  --retriever-type hybrid \
  --use-query-expansion \
  --query-expansion-max-queries 4 \
  --multi-query-per-query-k 8
```

Section prior rerank：

```bash
python -m app.main \
  --pdf data/resnet.pdf \
  --query "What experiments and evaluation are reported in this paper?" \
  --top-k 5 \
  --retriever-type hybrid \
  --reranker-type section_prior \
  --retriever-weight 0.8
```

Robotics tag prior rerank：

```bash
python -m app.main \
  --pdf data/<your_robotics_paper>.pdf \
  --query "Which sensor modalities, datasets, metrics, and deployment constraints are discussed?" \
  --top-k 3 \
  --retriever-type tfidf \
  --reranker-type robotics_tag_prior \
  --retriever-weight 0.7
```

Conditional branch：

```bash
python -m app.main \
  --pdf data/<your_robotics_paper>.pdf \
  --query "What dataset and metrics are used?" \
  --top-k 3 \
  --retriever-type tfidf \
  --enable-conditional-branch
```

自定义 trace 输出目录：

```bash
python -m app.main \
  --pdf data/resnet.pdf \
  --query "What are the main contributions of this paper?" \
  --top-k 3 \
  --retriever-type tfidf \
  --trace-dir outputs/traces
```

关闭 trace：

```bash
python -m app.main \
  --pdf data/resnet.pdf \
  --query "What are the main contributions of this paper?" \
  --top-k 3 \
  --retriever-type tfidf \
  --disable-trace
```

### 4. Run Retriever Evaluation

```bash
python -m scripts.evaluate_retrievers \
  --pdf data/resnet.pdf \
  --eval-json data/eval_queries.json \
  --top-k 5 \
  --output-dir outputs/eval
```

评估结果会保存为：

```text
outputs/eval/retriever_eval_YYYYMMDD_HHMMSS.csv
outputs/eval/retriever_eval_YYYYMMDD_HHMMSS.md
```

只看命令行输出：

```bash
python -m scripts.evaluate_retrievers \
  --pdf data/resnet.pdf \
  --eval-json data/eval_queries.json \
  --top-k 5 \
  --no-save-results
```

### 5. Run Smoke Tests

```bash
python scripts/test_safe_llm_invoke.py
python scripts/test_evidence_verifier.py
python scripts/test_conditional_branch.py
python scripts/test_retrieval_quality.py
python scripts/test_robotics_schema.py
python scripts/test_robotics_tag_prior_reranker.py
```

这些脚本用于离线 smoke test，不请求外部 LLM API。

## Example Output

主流程生成的报告保存在：

```text
outputs/
```

报告主要包含：

- input PDF and query
- paper title
- retrieval pipeline config
- expanded queries
- retrieved evidence metadata
- retrieved evidence details
- context passed to LLM
- paper summary
- technical critique
- evidence verification summary

如果启用了 conditional branch，正常路径不会输出 retrieval warning。证据较弱、触发过 query expansion retry，或 context 为空进入 fallback 时，报告会包含：

```text
Retrieval Quality Warnings
```

报告也会包含：

```text
Evidence Verification
```

该小节只展示 verifier method、claims checked、average support score、status 和 weakly-supported claims 数量。没有明显 weak claims 时会显示：

```text
No obvious weakly supported claims detected by lexical evidence check.
```

LLM 调用失败时，报告会继续生成，并包含：

```text
Generation Warnings
```

## Project Structure

```text
app/
  main.py                  CLI entry point
  graph.py                 LangGraph workflow
  states.py                shared workflow state
  nodes/                   LangGraph nodes
  nodes/evaluate_retrieval_quality.py conditional branch decision node
  nodes/fallback_generation.py fallback output node for empty evidence
  nodes/verify_evidence.py weak evidence alignment node
  nodes/legacy/            archived old nodes
  tools/
    retrievers/            TF-IDF, embedding, hybrid, FAISS, multi-query
    rerankers/             keyword, score-fusion, section-prior, robotics-tag-prior rerankers
    vector_store/          FAISS vector store
    context_builder.py     evidence-aware context construction
    evidence_verifier.py   lexical weak evidence alignment
    llm_safe_call.py       safe LLM invocation wrapper
    query_understanding.py rule-based query intent classifier
    retrieval_quality.py   rule-based retrieval quality scoring
    robotics_schema.py     rule-based robotics metadata extraction
    report_writer.py       Markdown report saving
    trace_writer.py        lightweight workflow trace writer

scripts/
  evaluate_retrievers.py   retrieval evaluation
  compare_retrievers.py    retriever comparison
  test_conditional_branch.py conditional branch smoke test
  test_evidence_verifier.py evidence verifier smoke test
  test_retrieval_quality.py retrieval quality smoke test
  test_robotics_schema.py  robotics metadata smoke test
  test_robotics_tag_prior_reranker.py robotics reranker smoke test
  test_safe_llm_invoke.py  offline LLM safety smoke test
  test_*.py                smoke tests and module checks

data/
  sample PDFs and evaluation queries

outputs/
  generated reports, traces, and evaluation results

docs/
  audit and design notes
```

## Current Limitations

**Workflow and retrieval**

- 当前实现偏 workflow，不是完整 autonomous agent 系统。
- Conditional branch 基于规则式 retrieval quality scoring，不是 learned / calibrated confidence model。
- query expansion 是 heuristic-based；conditional branch 最多只进行一次 retrieval retry，避免循环。
- robotics tag prior reranker 只对已召回 candidates 做轻量重排，不提供完整 robotics reasoning。

**Document understanding**

- chunking 仍以 fixed-size character chunking 为主，只附加启发式 page range / section metadata。
- citation 包含启发式 page range / section，但还不是严格版面级 citation。
- robotics-aware metadata 是规则/词典式抽取，不是完整领域知识图谱，也不是 LLM-based 信息抽取。

**Evaluation and verification**

- evaluation 仍是 keyword-based weak evaluation。
- evidence verifier 是 lexical overlap 弱匹配，不是 NLI 模型或严格 fact-checker，不能保证事实完全正确。
- 尚未加入基于人工标注或 NLI 的严格 faithfulness evaluation。

**Engineering**

- LLM safety 有 timeout / retry / fallback / trace 记录，但还不是生产级可观测性或多模型 fallback。
- 尚未提供 Web UI。

## Roadmap

- **Trace schema**：继续增强 branch、rerank、verification 等中间结果的结构化记录。
- **Tests**：从 smoke tests 逐步补充 pytest tests，覆盖 graph routing、rerank scoring 和 report generation。
- **Section-aware chunking**：从启发式 section metadata 升级到更稳定的 section / paragraph / page-aware chunking。
- **Page citation**：将启发式 page range 增强为更可靠的 page-level citation。
- **Retrieval quality scoring**：探索 learned / calibrated retrieval confidence 和更稳定的 query rewrite。
- **Evidence verifier**：从 lexical weak alignment 增强到 faithfulness evaluation、NLI-based verifier 或人工标注评估。
- **Streamlit demo**：展示 PDF、query、answer/report 和 retrieved evidence。
