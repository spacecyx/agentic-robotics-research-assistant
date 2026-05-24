# Agentic Robotics Research Assistant

面向机器人 / SLAM / 3D 感知论文阅读的 **LangGraph-based RAG workflow**。

本项目将本地 research paper PDF 转换为结构化 Markdown 分析报告，重点关注：

- 多阶段论文理解 workflow
- evidence-aware report generation
- modular retriever comparison
- evaluation-driven RAG improvement

当前项目不是 production-level autonomous agent system，也不声称具备完整 autonomous planning、多智能体协作、长期记忆或生产级部署能力。它更准确的定位是：一个围绕论文阅读场景构建的可解释、可评估、可扩展的 RAG workflow。

## Project Overview

`Agentic Robotics Research Assistant` 用 LangGraph 编排论文处理流程，从 PDF 解析、文本切分、检索、重排、上下文构建，到 LLM 生成论文摘要和技术评价，最终保存为 Markdown 报告。

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

这使项目更适合作为大模型应用工程 / AI Agent 应用开发方向的求职展示项目。

## Key Features

- **PDF parsing and cleaning**：读取本地论文 PDF，提取标题并清洗文本。
- **LangGraph workflow**：用节点化流程组织论文分析任务。
- **Modular retrievers**：支持 TF-IDF、Embedding、Hybrid、FAISS。
- **Query expansion and multi-query RRF**：支持启发式 query expansion、多 query 检索和 RRF-style 融合。
- **Reranking**：支持 keyword reranker 和 score fusion reranker。
- **Context construction**：控制上下文长度，并保留 chunk-level evidence metadata。
- **Evidence-aware Markdown report**：报告中展示 chunk id、score、rank、source、char range。
- **Retriever evaluation**：支持 Hit@1、Hit@3、Hit@K、MRR@K、Avg Rank、Latency，并导出 CSV / Markdown。

## System Architecture

主 LangGraph workflow：

```text
PDF
  -> load_pdf_node
  -> split_text_node
  -> retrieve_context_node
  -> summarize_paper_node
  -> critique_paper_node
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

### Rerank

对 first-stage retrieved candidates 二次排序。当前实现包括 keyword rerank 和 score fusion rerank。

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
| tfidf | 0.333 | 0.583 | 0.667 | 0.461 | 3.333 | 1.51 |
| embedding | 0.417 | 0.583 | 0.667 | 0.507 | 3.167 | 7.71 |
| hybrid | 0.417 | 0.500 | 0.667 | 0.496 | 3.333 | 7.71 |
| tfidf+keyword_rerank | 0.417 | 0.667 | 0.750 | 0.544 | 2.917 | 0.96 |
| hybrid+score_fusion_rerank | 0.333 | 0.500 | 0.750 | 0.471 | 3.333 | 9.37 |
| hybrid+query_expansion | 0.333 | 0.583 | 0.667 | 0.447 | 3.417 | 35.44 |
| hybrid+query_expansion+score_fusion_rerank | 0.417 | 0.583 | 0.667 | 0.521 | 3.083 | 34.13 |

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

## Project Structure

```text
app/
  main.py                  CLI entry point
  graph.py                 LangGraph workflow
  states.py                shared workflow state
  nodes/                   LangGraph nodes
  nodes/legacy/            archived old nodes
  tools/
    retrievers/            TF-IDF, embedding, hybrid, FAISS, multi-query
    rerankers/             keyword and score-fusion rerankers
    vector_store/          FAISS vector store
    context_builder.py     evidence-aware context construction
    report_writer.py       Markdown report saving

scripts/
  evaluate_retrievers.py   retrieval evaluation
  compare_retrievers.py    retriever comparison
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
- LangGraph 主流程仍是线性图，尚未加入条件分支和自动 query rewrite。
- chunking 仍是 fixed-size character chunking，不是 section-aware chunking。
- citation 当前主要是 chunk id / char range，不是 page-level citation。
- evaluation 仍是 keyword-based weak evaluation。
- query expansion 当前是 heuristic-based，泛化性有限。
- 尚未加入 faithfulness evaluation。
- 尚未提供 Web UI。

## Roadmap

- **Trace logging**：记录 PDF、retriever、top_k、candidate_k、latency、output path。
- **Minimal pytest**：覆盖 `text_splitter`、`query_expansion`、`reranker`、`context_builder`、`report_writer`。
- **Section-aware chunking**：按 section / paragraph / page 信息组织 chunk。
- **Page citation**：将 evidence 从 char range 升级为 page-level citation。
- **Conditional LangGraph branch**：检索不足时自动 query expansion，context 为空时跳过 LLM 并给出明确错误。
- **Streamlit demo**：展示 PDF、query、answer/report 和 retrieved evidence。
