# Agentic Robotics Research Assistant

面向机器人 / SLAM / 3D 感知论文阅读的 **LangGraph-based RAG workflow**。

本项目将本地 research paper PDF 转换为结构化 Markdown 分析报告，重点关注：

- 多阶段论文理解 workflow
- evidence-aware report generation
- modular retriever comparison
- evaluation-driven RAG improvement
- retrieval-quality-aware conditional branching

当前项目不是 production-level autonomous agent system，也不声称具备完整 autonomous planning、多智能体协作、长期记忆或生产级部署能力。它更准确的定位是：一个围绕论文阅读场景构建的可解释、可评估、可扩展的 RAG workflow。

## Project Overview

`Agentic Robotics Research Assistant` 用 LangGraph 编排论文处理流程，从 PDF 解析、文本切分、检索、重排、上下文构建，到 LLM 生成论文摘要和技术评价，最终保存为 Markdown 报告。项目支持可选的 retrieval quality 条件分支：证据充足时继续生成，证据较弱时最多触发一次 query expansion / retrieval retry，证据为空时使用 fallback 输出，避免对空 context 做无意义 LLM 调用。

目标用户包括：

- 机器人 / SLAM / 3D 感知方向工程师
- 正在学习深度学习、大模型应用、Agent 工程的开发者
- 希望用项目展示 RAG 工程能力和论文分析能力的求职者

典型输出报告包含：

- paper summary
- technical critique
- retrieved evidence
- retriever configuration
- query expansion / rerank metadata

## Why This Project

普通 PDF QA demo 往往只解决“问一句、答一句”的问题，难以体现检索证据、检索质量和系统工程取舍。

本项目关注的是论文阅读场景下更完整的 RAG workflow：

- 用 LangGraph 将论文分析拆成多个明确节点。
- 用 retrieved evidence 解释 LLM 报告依据。
- 对比 TF-IDF、Embedding、Hybrid、Query Expansion、Rerank 等检索策略。
- 用 Hit@K、MRR@K、Avg Rank 和 Latency 做 retrieval evaluation。
- 用 retrieval quality scoring 将 RAG workflow 从固定线性链路扩展为 failure-aware conditional workflow。

这使项目更适合作为大模型应用工程 / AI Agent 应用开发方向的求职展示项目。

## Key Features

- **PDF parsing and cleaning**：读取本地论文 PDF，提取标题并清洗文本。
- **LangGraph workflow**：用节点化流程组织论文分析任务。
- **Modular retrievers**：支持 TF-IDF、Embedding、Hybrid、FAISS。
- **Query expansion and multi-query RRF**：支持启发式 query expansion、多 query 检索和 RRF-style 融合。
- **Robotics-aware chunk metadata**：用规则/词典方式为 chunk 标注 sensor、dataset、metric、task、system module 和 deployment constraint 等领域标签。
- **Reranking**：支持 keyword、score fusion、section prior 和 robotics tag prior reranker。
- **Conditional LangGraph branch**：可通过 `--enable-conditional-branch` 启用 retrieval quality 判断；证据较弱时自动触发一次 query expansion / retrieval retry，context 为空时使用 fallback / warning，避免无意义 LLM 调用。
- **Context construction**：控制上下文长度，并保留 chunk-level evidence metadata。
- **Evidence-aware Markdown report**：报告中展示 chunk id、score、rank、source、page range、section、char range。
- **LLM invocation safety**：LLM 调用支持 timeout、有限 retry、错误分类、fallback 输出和 trace/error logging。
- **Retriever evaluation**：支持 Hit@1、Hit@3、Hit@K、MRR@K、Avg Rank、Latency，并导出 CSV / Markdown。

## System Architecture

默认主 LangGraph workflow 保持兼容：

```text
PDF
  -> load_pdf_node
  -> split_text_node
  -> retrieve_context_node
  -> evaluate_retrieval_quality_node
  -> summarize_paper_node
  -> critique_paper_node
  -> generate_report_node
  -> Markdown report
```

启用 `--enable-conditional-branch` 后，retrieval quality 会决定后续路径：

```text
PDF
  -> load_pdf_node
  -> split_text_node
  -> retrieve_context_node
  -> evaluate_retrieval_quality_node
       |-- good evidence -> summarize_paper_node -> critique_paper_node
       |-- weak evidence -> query expansion / retrieval retry -> evaluate_retrieval_quality_node
       |-- empty evidence -> fallback_generation_node
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
  generated reports and evaluation results
```

## RAG Pipeline

### TF-IDF Retriever

关键词匹配 baseline，适合术语明确的问题，速度快，便于和其他检索策略对比。

### Embedding Retriever

基于 `sentence-transformers` 的语义检索，适合 query 和论文原文表达不完全一致的情况。

### Hybrid Retriever

融合 TF-IDF 和 embedding 分数，兼顾关键词精确匹配和语义召回。

### FAISS Retriever

使用本地 FAISS 向量索引，避免每次运行重复构建文档 embedding。当前用于 paper-level local retrieval，不是大规模向量检索服务。

### Query Expansion + Multi-query RRF

对复杂问题生成多个 query variants，分别检索后进行去重和 RRF-style 融合。该方法可能提升召回，但也会增加 per-query latency。

### Retrieval Quality and Conditional Branching

`evaluate_retrieval_quality_node` 会调用规则式 retrieval quality scorer，对 retrieved results 进行轻量判断。该判断不调用 LLM，使用的信号包括：

- retrieved chunk 数量
- top score / average score
- section coverage，尤其是 Experiments / Evaluation / Results 类 section
- robotics tag coverage，例如 sensor / dataset / metric tags

评分结果包含 `quality_label` 和 `recommended_action`。当前路径包括：

- `good` / `proceed`：继续 `summarize_paper_node` 和 `critique_paper_node`。
- `weak` / `expand_query`：如果尚未 retry 且 query expansion 未开启，则设置 `use_query_expansion=True`，回到 `retrieve_context_node` 最多重试一次。
- retry 后仍 weak：继续生成报告，但在 Markdown 中加入简短 warning。
- `empty` / `fallback`：进入 `fallback_generation_node`，跳过 summary / critique 的 LLM 调用，仍生成 Markdown 报告。

该能力默认关闭，需要通过 `--enable-conditional-branch` 显式启用。默认 CLI 命令仍保持原有使用方式。

### Rerank

对 first-stage retrieved candidates 二次排序。当前实现包括 keyword rerank、score fusion rerank、section prior rerank 和 robotics tag prior rerank。

Section prior reranker 使用轻量规则式 query intent classifier，不调用 LLM。它根据 query intent 和 chunk section metadata 给候选结果一个小的 section bias，例如 method 类问题更偏向 Method / Approach / Model，experiment 类问题更偏向 Experiments / Evaluation / Results。该模块只对已召回 candidates 重排，不改变底层 retriever scoring，也不凭空召回新 chunk。

Robotics tag prior reranker 复用 chunk 中的 `robotics_tags` metadata，对传感器、数据集、指标、任务类型、系统模块和部署限制等 query 增加轻量 tag prior。例如 LiDAR / KITTI / ATE / real-time 相关问题会优先提升包含对应 robotics tags 的候选 chunk。该 reranker 仍然只对 first-stage candidates 重排，不新增召回结果，也不调用 LLM。

### Robotics-aware Metadata

`split_text_into_chunks` 会为每个 `TextChunk` 附加轻量 robotics metadata：

- `robotics_tags`
- `robotics_tag_count`
- `robotics_flat_tags`

当前标签由 `app/tools/robotics_schema.py` 中的规则/词典抽取，覆盖 sensor modality、dataset、metric、task type、system module 和 deployment constraint。该模块用于增强 trace、评估和 rerank metadata，不是完整机器人领域知识图谱。

### LLM Safety and Traceability

`summarize_paper_node` 和 `critique_paper_node` 通过统一的 `safe_llm_invoke` 调用 LLM，支持：

- timeout control
- limited retry
- error classification
- latency statistics
- fallback output
- trace/error logging

如果 LLM 调用失败，workflow 不会直接中断，而是在报告中写入清晰的 fallback 文本，并在 trace JSON 中记录 `llm_invocations` 和 `errors`。这不是 production-grade high availability 机制，而是为了让本地 RAG workflow 在 API timeout、网络错误或上下文过长时更容易调试和复现。

## Evaluation

评估脚本：[scripts/evaluate_retrievers.py](scripts/evaluate_retrievers.py)

当前支持指标：

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

说明：

- 当前 relevance 判断仍是 keyword-based weak evaluation。
- Latency 不包含 retriever 初始化、embedding 模型加载、FAISS index loading/building。
- Latency 包含每个 method 内部的 query expansion、multi-query retrieval、rerank 成本。
- 后续计划加入 `relevant_chunk_ids`、page citation 和 faithfulness evaluation。

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

Hybrid retrieval 示例：

```bash
python -m app.main \
  --pdf data/resnet.pdf \
  --query "What are the main problem, method, contribution, experimental results, and limitations of this paper?" \
  --top-k 5 \
  --retriever-type hybrid
```

FAISS retrieval 示例：

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

Query expansion 示例：

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

Section prior rerank 示例：

```bash
python -m app.main \
  --pdf data/resnet.pdf \
  --query "What experiments and evaluation are reported in this paper?" \
  --top-k 5 \
  --retriever-type hybrid \
  --reranker-type section_prior \
  --retriever-weight 0.8
```

Robotics tag prior rerank 示例：

```bash
python -m app.main \
  --pdf data/fastlio2.pdf \
  --query "Which LiDAR SLAM odometry method reports real-time performance and latency?" \
  --top-k 3 \
  --retriever-type tfidf \
  --reranker-type robotics_tag_prior \
  --retriever-weight 0.7
```

Conditional branch 示例：

```bash
python -m app.main \
  --pdf data/fastlio2.pdf \
  --query "What dataset and metrics are used?" \
  --top-k 3 \
  --retriever-type tfidf \
  --enable-conditional-branch
```

Trace logging 默认开启，主流程会在 `outputs/traces/` 下保存轻量 JSON trace。Trace 只记录配置、中间状态摘要、短 preview 和输出路径，不记录完整论文全文、完整 retrieved context、完整 report 或 API key。

Trace 中会记录检索和生成相关的结构化 metadata，例如：

- retrieved chunk 的 page range / section
- retrieval quality 的 `quality_label`、`recommended_action`
- conditional branch 的 `branch_decision`、`retry_count`、`fallback_reason`、`query_expansion_used`
- section prior rerank 的 `query_intent`、`section_prior_score`
- robotics metadata 的 `robotics_tags`、`robotics_tag_summary`
- robotics tag prior rerank 的 `matched_robotics_tags`、`robotics_tag_score`、`final_score`
- LLM 调用的 `llm_invocations`
- 失败时的 `errors`、`fallback_used`、`error_type`、`attempts`、`latency_ms`

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

不保存评估结果、只看命令行输出：

```bash
python -m scripts.evaluate_retrievers \
  --pdf data/resnet.pdf \
  --eval-json data/eval_queries.json \
  --top-k 5 \
  --no-save-results
```

### 5. Run Smoke Tests

LLM safe invoke 离线 smoke test：

```bash
python scripts/test_safe_llm_invoke.py
```

该脚本不请求外部 LLM API，覆盖成功调用、普通异常、timeout、content-too-long 不重试等场景。

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

如果启用了 conditional branch，正常路径不会输出 retrieval warning。证据较弱、触发过 query expansion retry，或 context 为空进入 fallback 时，报告会额外包含简短的：

```text
Retrieval Quality Warnings
```

context 为空时报告仍会生成，并在 summary / critique 位置写入 fallback reason。

如果 LLM 调用失败，报告会继续生成，并额外包含简短的：

```text
Generation Warnings
```

正常路径不会输出该 warning 小节。

## Project Structure

```text
app/
  main.py                  CLI entry point
  graph.py                 LangGraph workflow
  states.py                shared workflow state
  nodes/                   LangGraph nodes
  nodes/evaluate_retrieval_quality.py conditional branch decision node
  nodes/fallback_generation.py fallback output node for empty evidence
  nodes/legacy/            archived old nodes
  tools/
    retrievers/            TF-IDF, embedding, hybrid, FAISS, multi-query
    rerankers/             keyword, score-fusion, section-prior, robotics-tag-prior rerankers
    vector_store/          FAISS vector store
    context_builder.py     evidence-aware context construction
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
  test_retrieval_quality.py retrieval quality smoke test
  test_robotics_schema.py  robotics metadata smoke test
  test_robotics_tag_prior_reranker.py robotics reranker smoke test
  test_safe_llm_invoke.py  offline LLM safety smoke test
  test_*.py                smoke tests and module checks

data/
  sample PDFs and evaluation queries

outputs/
  generated reports and evaluation results

docs/
  audit and design notes
```

## Current Limitations

- 当前是 workflow-first，不是完整 autonomous agent。
- Conditional branch 当前基于规则式 retrieval quality scoring，不是 learned / calibrated confidence model。
- chunking 仍以 fixed-size character chunking 为主，但已附加启发式 page range / section metadata。
- citation 当前已包含启发式 page range / section，但还不是严格的版面级 citation。
- evaluation 仍是 keyword-based weak evaluation。
- query expansion 当前是 heuristic-based，泛化性有限；conditional branch 最多只进行一次 retrieval retry，避免循环。
- robotics-aware metadata 当前是规则/词典式抽取，不是完整领域知识图谱，也不是 LLM-based 信息抽取。
- robotics tag prior reranker 只对已召回 candidates 做轻量重排，不提供完整 robotics reasoning。
- LLM safety 已有 timeout / retry / fallback / trace 记录，但还不是生产级可观测性或多模型 fallback。
- 尚未加入 faithfulness evaluation。
- 尚未提供 Web UI。

## Roadmap

- **Trace logging**：继续增强 LLM 调用、retrieval、rerank 和报告生成的可复现记录。
- **Minimal tests**：补充核心模块的最小 smoke/pytest 测试，优先覆盖 `text_splitter`、`query_expansion`、`reranker`、`context_builder`、`llm_safe_call`。
- **Section-aware chunking**：从启发式 section metadata 逐步升级到更稳定的 section / paragraph / page-aware chunking。
- **Page citation**：将启发式 page range 继续增强为更可靠的 page-level citation。
- **Retrieval quality scoring**：继续增强检索质量评分，例如 learned / calibrated retrieval confidence 和更稳定的 query rewrite。
- **Evidence verifier**：加入 faithfulness evaluation / evidence verifier，检查 summary 和 critique 是否被 retrieved evidence 支撑。
- **Streamlit demo**：展示 PDF、query、answer/report 和 retrieved evidence。
