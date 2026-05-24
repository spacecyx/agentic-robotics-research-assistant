# Project Audit Report

## 1. Current Project Summary

`Agentic Robotics Research Assistant` 是一个面向机器人、SLAM、三维感知和 AI 论文阅读的 LangGraph-based RAG workflow 项目。

当前项目已经实现了从本地论文 PDF 到结构化 Markdown 报告的完整链路：

```text
PDF
  -> PDF text extraction
  -> text cleaning
  -> text chunking
  -> retrieval
  -> optional query expansion / multi-query retrieval
  -> optional reranking
  -> context construction
  -> LLM summary and critique
  -> Markdown report
```

核心判断：

- 当前项目已经明显超过普通“PDF 问答 demo”，具备模块化 RAG、LangGraph workflow、检索评估和 evidence-aware 报告生成等工程要素。
- 但它目前更准确的定位是 **LangGraph-based RAG workflow**，还不是完整意义上的 Agent 系统。
- 如果用于求职展示，建议重点包装为“论文理解场景下的可解释 RAG 工作流”，不要过度包装成“自主 Agent 平台”。

当前最有价值的方向不是堆更多模型或外部服务，而是把已有链路打磨成可复现、可解释、可评估、可展示的工程项目。

## 2. Directory Structure Analysis

当前主要目录结构：

```text
agentic-robotics-research-assistant/
├── app/
│   ├── main.py
│   ├── graph.py
│   ├── states.py
│   ├── nodes/
│   └── tools/
├── scripts/
├── data/
├── outputs/
├── prompts/
├── models/
├── docs/
├── requirements.txt
├── environment.yml
├── .env.example
└── README.md
```

主要目录职责：

- `app/`：核心应用代码。
- `app/main.py`：CLI 入口，负责解析 PDF、query、retriever、FAISS、query expansion 等参数。
- `app/graph.py`：LangGraph workflow 定义，当前是线性图。
- `app/states.py`：工作流共享状态 `PaperState`。
- `app/nodes/`：LangGraph 节点层，把工具能力接入 workflow。
- `app/tools/`：底层能力层，包括 PDF loader、text splitter、retriever、reranker、context builder、LLM client、report writer。
- `scripts/`：实验、测试、评估脚本。
- `data/`：样例论文 PDF、评估 query、FAISS 索引。
- `outputs/`：已生成的 Markdown 报告。
- `prompts/`：任务和审计 prompt。
- `docs/`：项目文档，适合放审计报告、路线图、架构说明。

核心业务逻辑集中在：

- `app/graph.py`
- `app/states.py`
- `app/nodes/load_pdf.py`
- `app/nodes/split_text.py`
- `app/nodes/retrieve_context.py`
- `app/nodes/summarize_paper.py`
- `app/nodes/critique_paper.py`
- `app/nodes/generate_report.py`
- `app/tools/retrievers/`
- `app/tools/rerankers/`
- `app/tools/context_builder.py`
- `app/tools/vector_store/faiss_store.py`

脚本、测试、数据或文档包括：

- `scripts/test_*.py`
- `scripts/evaluate_retrievers.py`
- `scripts/compare_retrievers.py`
- `data/eval_queries.json`
- `data/*.pdf`
- `outputs/*.md`
- `README.md`
- `docs/project_audit.md`

需要后续整理的历史文件：

- `app/nodes/retrieve_context_old.py`
- `app/nodes/retrieve_context_oldest.py`
- `app/nodes/generate_report_old.py`
- `app/tools/simple_retriever.py`
- `app/tools/pdf_loader.py`

这些文件不一定要立刻删除，但需要在文档中说明是否为 legacy，避免面试或代码审查时显得主线混乱。

## 3. Core Workflow Analysis

当前 LangGraph 流程定义在 `app/graph.py`：

```text
load_pdf
  -> split_text
  -> retrieve_context
  -> summarize_paper
  -> critique_paper
  -> generate_report
  -> END
```

节点职责：

- `load_pdf_node`
  - 输入：`pdf_path`
  - 输出：`raw_text`、`paper_text`、`paper_title`
  - 职责：读取 PDF、提取文本、清洗文本、提取标题。

- `split_text_node`
  - 输入：`paper_text`
  - 输出：`chunks`
  - 职责：将清洗后的论文文本切分为可检索 chunk。

- `retrieve_context_node`
  - 输入：`query`、`chunks`、retriever 配置、reranker 配置、query expansion 配置。
  - 输出：`retrieval_results`、`retrieved_context`、`retrieval_evidence`、`expanded_queries` 等。
  - 职责：创建 retriever、召回候选、可选 query expansion、可选 rerank、构造 LLM context。

- `summarize_paper_node`
  - 输入：`retrieved_context`
  - 输出：`paper_summary`
  - 职责：基于检索上下文生成论文摘要。

- `critique_paper_node`
  - 输入：`retrieved_context`、`paper_summary`
  - 输出：`paper_critique`
  - 职责：从技术学习、机器人/3D 感知、大模型/Agent 求职角度评价论文。

- `generate_report_node`
  - 输入：论文标题、检索配置、检索证据、摘要、评价。
  - 输出：`final_report`、`output_path`
  - 职责：拼接 Markdown 报告并保存文件。

整体流程清楚，适合求职展示。当前不足是 workflow 仍然是线性的，没有条件分支、自动 query rewrite、检索不足检测、人工确认、工具路由等更典型的 Agent 行为。

## 4. LangGraph State and Node Analysis

`app/states.py` 使用 `TypedDict(total=False)` 定义 `PaperState`。这对快速迭代友好，但随着功能增加，State 字段已经开始膨胀。

当前 State 中包含：

- 用户输入：`pdf_path`、`query`、`top_k`
- 检索配置：`retriever_type`、`embedding_model`、`hybrid_alpha`
- FAISS 配置：`faiss_index_dir`、`rebuild_faiss_index`
- Query expansion 配置：`use_query_expansion`、`query_expansion_max_queries`
- Rerank 配置：`reranker_type`、`reranker_top_k`、`retriever_weight`
- 中间结果：`raw_text`、`paper_text`、`chunks`、`retrieval_results`
- LLM 输出：`paper_summary`、`paper_critique`
- 报告输出：`final_report`、`output_path`

主要问题：

- `chunks: list[Any]` 和 `retrieval_results: list[Any]` 类型过松。
- 配置字段、业务中间态、最终输出都混在一个 State 中。
- 多个默认值分散在 `main.py`、`retrieve_context.py`、retriever/reranker 类中。
- `retrieve_context_node` 职责偏重，但不建议把“立即拆分”放在最高优先级。

更合理的节奏是：

1. 先补 evaluation，让项目有可量化结果。
2. 再补轻量 trace logging，让每次运行可解释。
3. 补最小 pytest，保护核心模块行为。
4. 最后再拆分 `retrieve_context_node`，避免无测试支撑下重构。

## 5. RAG System Analysis

当前支持的 retriever：

- `TfidfRetriever`
  - 文件：`app/tools/retrievers/tfidf_retriever.py`
  - 特点：关键词匹配，适合术语明确的问题。

- `EmbeddingRetriever`
  - 文件：`app/tools/retrievers/embedding_retriever.py`
  - 特点：基于 sentence-transformers 的语义检索。

- `HybridRetriever`
  - 文件：`app/tools/retrievers/hybrid_retriever.py`
  - 特点：融合 TF-IDF 和 Embedding 分数。

- `FaissRetriever`
  - 文件：`app/tools/retrievers/faiss_retriever.py`
  - 特点：使用本地 FAISS 向量索引。

- `MultiQueryRetriever`
  - 文件：`app/tools/retrievers/multi_query_retriever.py`
  - 特点：对 query variants 分别检索，再用 RRF 合并。

接口统一性较好：

```python
search(query: str, top_k: int = 5) -> list[RetrievalResult]
```

核心数据结构：

- `TextChunk`
  - 文件：`app/tools/text_splitter.py`
  - 字段：`chunk_id`、`text`、`start_char`、`end_char`

- `RetrievalResult`
  - 文件：`app/tools/retrievers/schemas.py`
  - 字段：`chunk`、`score`、`source`、`metadata`

- `Evidence`
  - 文件：`app/tools/context_builder.py`
  - 字段：`source_id`、`chunk_id`、`score`、`source`、`rank`、`start_char`、`end_char`

亮点：

- retriever 工厂模式清楚。
- FAISS 持久化索引有 fingerprint 校验，避免错用索引。
- reranker 和 retriever 分层明确。
- context builder 会生成 evidence metadata，便于解释检索来源。

关键不足：

- chunk 只有字符范围，没有 page citation。
- chunking 是固定字符窗口，没有利用论文结构。
- Query Expansion 是启发式规则，且偏 ResNet / Transformer，不具备通用性。
- `metadata` 是自由字典，扩展灵活但缺少 schema 约束。
- 目前还缺少 answer faithfulness、citation correctness、retrieval sufficiency 等评估。

## 6. Evaluation System Analysis

当前评估脚本：

- 文件：`scripts/evaluate_retrievers.py`
- 数据：`data/eval_queries.json`

已支持指标：

- Hit@1
- Hit@3
- Hit@K
- MRR@K
- Avg Rank

已支持方法对比：

- `tfidf`
- `embedding`
- `hybrid`
- `tfidf+keyword_rerank`
- `hybrid+score_fusion_rerank`
- `hybrid+query_expansion`
- `hybrid+query_expansion+score_fusion_rerank`

这是项目中很值得保留和强化的部分。它说明项目不是只关注“能生成答案”，也关注 RAG 检索质量。

当前问题：

- evaluation 偏弱，目前主要基于 keyword matching。
- 缺少 latency 指标，无法比较不同 retriever 的性能成本。
- 缺少真实 `relevant_chunk_ids`，无法做更可靠的 recall@k / precision@k / nDCG。
- eval query 数量较少，且主要围绕 ResNet。
- 缺少稳定实验结果保存机制，例如固定输出 `outputs/eval/*.csv` 或 `docs/evaluation_results.md`。
- 没有端到端生成质量评估，也没有 citation correctness 评估。

优先改进方向：

1. 在现有 `evaluate_retrievers.py` 增加 latency。
2. 将每次评估结果稳定保存为 CSV / Markdown。
3. 在 eval JSON 中增加 `relevant_chunk_ids`。
4. 逐步扩充多论文、多问题类型评估集。

这部分对求职展示非常重要。相比直接加新模型，能展示“我知道如何评估 RAG 系统”更有说服力。

## 7. Engineering Quality Analysis

优点：

- `nodes/` 和 `tools/` 分层方向正确。
- Retriever / Reranker 有统一接口和工厂方法。
- FAISS index build / save / load / search 逻辑完整。
- `ContextBuilder` 把检索结果和 evidence 组织成 LLM 可用上下文。
- CLI 参数较丰富，方便展示不同 retrieval strategy。

问题：

- `print` 较多，缺少轻量 trace logging。
- `retrieve_context_node` 同时承担检索、query expansion、rerank、context construction，职责偏重。
- `PaperState` 类型较松，`Any` 较多。
- 配置默认值分散，后续不利于复现实验。
- README 更像迭代日志，缺少求职展示所需的架构图、运行命令、评估结果和设计取舍。
- 测试脚本偏手动运行，缺少最小 pytest 保护核心模块。
- 历史文件仍在主目录，影响项目专业感。

优先级判断：

- 最高优先级不是立即大重构，而是先让项目“可展示、可复现、可解释”。
- 先补 evaluation、trace logging、最小 pytest，再做结构性重构更稳。

## 8. Strengths

适合求职展示的亮点：

- 场景定位明确：机器人 / SLAM / 3D 感知工程师阅读 AI 论文。
- 使用 LangGraph 构建多阶段论文分析 workflow。
- 实现模块化 RAG 检索层，支持 TF-IDF、Embedding、Hybrid、FAISS。
- 实现 Query Expansion + Multi-query RRF。
- 实现 Reranker 抽象和 score fusion baseline。
- 输出报告包含 retrieved evidence，具备可解释性。
- 已有 retrieval evaluation 脚本，可以对比不同检索策略。

可以写进简历的表达：

- “基于 LangGraph 构建论文分析 RAG workflow，覆盖 PDF parsing、chunking、retrieval、reranking、context construction 和 Markdown report generation。”
- “设计模块化 retriever / reranker 接口，支持 TF-IDF、Embedding、Hybrid、FAISS 和 Multi-query RRF。”
- “构建 retrieval evaluation pipeline，对比 Hit@K、MRR@K、Avg Rank，并计划扩展 latency 与真实 relevant chunk 标注。”
- “实现 evidence-aware report generation，为 LLM 输出提供 chunk-level source metadata。”

## 9. Weaknesses and Risks

求职面试中最容易被追问的问题：

- 为什么叫 Agent？当前是否只是 pipeline？
  - 建议回答：当前版本更准确是 LangGraph-based RAG workflow，后续计划通过条件分支、检索不足检测、query rewrite 和工具路由增强 Agent 能力。

- RAG 效果怎么证明？
  - 当前只能用 keyword-based weak evaluation 初步证明，需要补 latency、真实 relevant_chunk_ids 和更大 eval set。

- citation 是否可靠？
  - 当前只有 chunk id 和 char range，缺少 page citation。后续需要在 PDF parsing 和 chunking 阶段保留 page number。

- 是否生产级？
  - 当前不是生产级服务，更适合定位为求职展示型工程项目。生产化还需要 API/UI、配置管理、日志、测试、部署和监控。

- 是否通用？
  - 当前 Query Expansion 规则偏 ResNet / Transformer，需要逐步通用化或替换为可配置 query rewrite。

## 10. Job-Oriented Value Assessment

对 Agent 应用开发工程师岗位：

- 当前项目能展示 LangGraph workflow、工具模块化、RAG pipeline 设计能力。
- 但 Agent 决策能力还不强，需要补条件分支和自适应检索策略。

对大模型应用工程师岗位：

- 当前项目能展示 PDF RAG、上下文构建、prompt-based summary / critique、evidence-aware report。
- 需要补生成质量评估和 citation correctness，才能更有说服力。

对 AI Agent 开发工程师岗位：

- 当前项目可以作为 Agent 工程雏形。
- 但应诚实表达为 workflow-first，不要过度声称具备自主规划、多工具协作、长期记忆等能力。

建议求职展示策略：

- 主线讲“我如何把普通 PDF RAG 打磨成可评估、可解释、可扩展的论文研究 workflow”。
- 不要主线讲“我做了一个完整 autonomous agent”。
- 面试重点放在工程取舍：为什么要 Hybrid、为什么要 Rerank、为什么要 evaluation、为什么要 evidence。

## 11. Recommended Upgrade Roadmap

### 必须做

1. 保存审计文档
   - 当前文档作为项目改造基线。
   - 目标：后续每一步升级都有明确依据，而不是随意堆功能。

2. 清理历史文件清单
   - 先输出清单，不急着删除。
   - 涉及文件：`retrieve_context_old.py`、`retrieve_context_oldest.py`、`generate_report_old.py`、`simple_retriever.py`、旧版 `pdf_loader.py`。
   - 目标：明确哪些是 legacy，哪些仍被引用。

3. 增强 evaluation：latency + 稳定结果保存
   - 在 `scripts/evaluate_retrievers.py` 中增加 per-query latency 和 method average latency。
   - 将结果稳定保存到 CSV 或 Markdown。
   - 后续增加 `relevant_chunk_ids`，让评估从 weak keyword matching 逐步升级。
   - 这是求职展示优先级最高的工程增强。

4. 改造 README
   - 从学习日志改成项目展示文档。
   - 增加：项目定位、架构图、运行命令、检索策略说明、评估结果、已知限制、路线图。
   - 目标：让面试官 3 分钟内看懂项目价值。

5. 增加轻量 trace logging
   - 用标准 `logging` 替代关键路径上的 `print`。
   - 至少记录：PDF path、chunk count、retriever type、top_k、candidate_k、reranker、latency、output path。
   - 不需要一开始就接 LangSmith 或 OpenTelemetry。

6. 补充最小 pytest
   - 不要求迁移所有 `scripts/test_*.py`。
   - 优先覆盖核心纯逻辑模块：
     - `text_splitter`
     - `query_expansion`
     - `keyword_reranker`
     - `score_fusion_reranker`
     - `context_builder`
     - `report_writer`
   - 目标：为后续重构提供最低限度安全网。

### 建议做

7. 增加 section-aware chunking / page citation
   - 在 PDF loader 阶段保留 page number。
   - chunk metadata 增加 `page_start`、`page_end`、`section_title`。
   - 报告中的 evidence 从 char range 升级为 page citation。
   - 这是 RAG 项目从 demo 走向可信系统的关键增强。

8. 拆分 `retrieve_context_node`
   - 在 evaluation、trace、最小测试完成后进行。
   - 建议拆为：
     - `retrieve_candidates_node`
     - `rerank_context_node`
     - `build_context_node`
   - 目标：让 LangGraph 节点职责更清楚，也便于插入条件分支。

9. 增加 LangGraph 条件分支
   - 示例：
     - 如果检索结果低于阈值，自动 query expansion。
     - 如果 context 为空，跳过 LLM 生成并返回明确错误。
     - 如果 evidence 不足，扩大 candidate_k 或切换 retriever。
   - 这一步能让项目从 workflow 更接近 Agent。

10. Streamlit Demo
   - 用轻量 UI 展示 PDF 选择、query 输入、answer/report、evidence。
   - 适合求职演示。
   - 优先级高于 FastAPI，因为展示效果更直接。

### 可暂缓做

- FastAPI 服务化。
- Cross-Encoder reranker。
- LangSmith tracing。
- OpenTelemetry。
- LLM-as-judge 自动评估。
- 多用户、数据库、权限、部署。

这些不是没价值，而是不应抢在 evaluation、README、trace、最小测试之前。

## 12. Suggested Next Codex Tasks

建议后续任务按下面顺序推进：

1. “请只读分析当前历史文件和重复模块，生成 legacy cleanup 清单，不修改代码。”
2. “请增强 `scripts/evaluate_retrievers.py`，加入 latency 指标和稳定 CSV 输出。”
3. “请改造 README，使其适合求职展示，包括项目定位、架构、运行命令和评估结果位置。”
4. “请为核心运行链路增加轻量 logging，不引入外部 tracing 服务。”
5. “请补充最小 pytest，只覆盖 text_splitter、query_expansion、reranker、context_builder、report_writer。”
6. “请设计 section-aware chunking 和 page citation 的数据结构，不急着实现。”
7. “请在已有测试保护下拆分 `retrieve_context_node`。”
8. “请为 LangGraph 增加检索不足时的条件分支。”
9. “请实现一个 Streamlit demo，用于求职展示。”

最终目标：

把当前项目从“功能丰富的学习型 RAG workflow”升级为“有评估、有证据、有日志、有展示界面、能清楚讲工程取舍的求职作品”。
