请只润色 README.md，不要修改任何代码文件。

任务目标：
当前 README.md 内容基本完整，但表达上 AI 感较强，存在一些空泛、重复、过度解释或不自然的表述。请在不改变项目事实和技术边界的前提下，对 README 做一次“工程项目展示型润色”，让它更像开发者自己写的开源项目文档，而不是 AI 生成说明。

项目路径：
./agentic-robotics-research-assistant/README.md

请先做事实审计，不要立即修改：
1. 阅读当前 README.md。
2. 运行 git status --short。
3. 如果工作区有代码改动，运行 git diff --stat 和 git diff --name-status，了解当前 README 描述是否需要保持一致。
4. 不需要修改任何代码，只需要基于当前 README 和真实项目内容润色文档。

润色目标：
1. 降低 AI 感：
   - 删除或改写过于模板化、宣传化、重复解释的句子。
   - 避免“当前项目不是……也不声称……”这类过度自证式表达反复出现。
   - 避免“这使项目更适合作为……”这类像求职包装的语气。
   - 避免堆叠抽象词，例如“可解释、可评估、可扩展、工程闭环”等反复出现。
   - 保留必要限制，但用自然、克制的工程文档语气表达。

2. 保持真实准确：
   - 不新增未实现功能。
   - 不夸大为 production-level autonomous agent。
   - 不夸大为完整 multi-agent system、长期记忆、生产级高可用或严格事实校验。
   - 不声称一定提升效果，除非 README 中已有真实评估结果支持。
   - 不删除重要限制，例如 weak evaluation、heuristic query expansion、非生产级观测性等。

3. 优化结构：
   - 保留 README 原有主要结构，但可以适度调整小节标题和段落顺序。
   - 让开头更直接：项目是什么、输入是什么、输出是什么、核心能力是什么。
   - 减少重复小节之间的信息重叠，例如 Project Overview、Why This Project、Key Features 中反复说明同一件事。
   - Quick Start、Evaluation、Project Structure、Limitations 等部分要保持清晰可读。
   - 如果某些小节太长，请适度压缩，但不要删掉关键命令或真实能力。

4. 优化语言风格：
   - 使用简洁、自然、工程化的中文表达。
   - 中英文技术词保持统一，例如：
     - LangGraph workflow
     - RAG
     - retriever
     - reranker
     - trace
     - fallback
     - query expansion
   - 不要把每句话都写成“支持 A、B、C、D、E”的堆叠句。
   - 能用短句就不要用很长的复合句。
   - 标题和 bullet 要具体，不要空泛。

5. 重点润色这些高 AI 感区域：
   - 开头项目介绍
   - Project Overview
   - Why This Project
   - Key Features
   - RAG Pipeline
   - LLM Safety / Conditional Branch / Evidence Verification 等能力描述
   - Current Limitations
   - Roadmap

6. 对以下内容保持谨慎：
   - 命令行示例必须保持真实可运行，不要随意改命令。
   - 表格中的评估结果不要改数值。
   - 文件路径和模块名必须与项目一致。
   - 如果不确定某个新增模块是否存在，不要写进 README。

严格限制：
- 只能修改 README.md。
- 不要修改 Python 代码。
- 不要修改 tests。
- 不要修改 requirements / environment。
- 不要创建新文件。
- 不要新增 badge、logo、宣传语。
- 不要把 README 改成求职简历风格。
- 不要把项目包装成 production-ready 系统。
- 不要删除所有限制说明；只是让限制说明更自然。

建议风格示例：

不推荐：
“本项目不是 production-level autonomous agent system，也不声称具备完整 autonomous planning、多智能体协作、长期记忆或生产级部署能力。”

推荐：
“当前实现更接近一个面向论文阅读的 RAG workflow，而不是完整的 autonomous agent 系统。”

不推荐：
“这使项目更适合作为大模型应用工程 / AI Agent 应用开发方向的求职展示项目。”

推荐：
“项目重点放在检索证据、流程可追踪和检索策略对比上。”

不推荐：
“支持 timeout、有限 retry、错误分类、fallback 输出和 trace/error logging。”

推荐：
“LLM 调用经过统一封装，失败时会记录错误并返回 fallback，避免单次请求中断整个流程。”

完成后请输出：
1. README 中主要润色了哪些部分。
2. 哪些内容被压缩或合并了。
3. 是否保留了所有真实功能和限制。
4. 是否存在你没有改动的高风险表述，以及原因。
5. 运行 git diff -- README.md，确认只修改 README。