你现在是这个项目的代码审计员和 AI Agent 工程架构顾问。

项目名称：Agentic Robotics Research Assistant

项目背景：
这是一个面向机器人、SLAM、三维感知、AI 论文阅读的 Agentic Research Assistant。当前项目已经实现了基于 LangGraph 的论文处理工作流，并逐步加入了 PDF 解析、文本清洗、文本切分、RAG 检索、TF-IDF 检索、Embedding 检索、Hybrid 检索、Query Expansion、Rerank、检索效果评估、报告生成等能力。

我的目标岗位：
- Agent 应用开发工程师
- 大模型应用工程师
- AI Agent 开发工程师

本次任务：
请你对当前代码仓库进行一次完整的只读代码审计。

非常重要：
1. 本轮不要修改任何代码。
2. 不要创建、删除、重命名任何文件。
3. 不要自动重构。
4. 只阅读、分析、总结。
5. 如果你发现问题，只在报告中说明，不要直接修复。

请完成以下分析：

一、项目结构分析
- 总结当前目录结构。
- 说明每个主要目录和关键文件的职责。
- 识别哪些文件属于核心业务逻辑，哪些文件属于脚本、测试、数据或文档。

二、核心工作流分析
- 梳理当前从输入论文到生成报告的完整数据流。
- 说明 LangGraph 中有哪些节点。
- 每个节点的输入、输出和职责是什么。
- 当前 State / Schema 是如何传递信息的。
- 是否存在节点职责过重、状态字段混乱、模块边界不清的问题。

三、RAG 检索系统分析
- 当前支持哪些检索方式。
- 各 retriever 的接口是否统一。
- chunk、document、metadata、retrieval result 的数据结构是否清晰。
- 当前 evaluation 脚本是否足够支撑 Hit@k、MRR、Latency 等指标。
- 当前 RAG 系统距离一个可展示、可面试讲解的工程系统还差什么。

四、工程质量分析
- import 路径是否清晰。
- 是否存在重复代码。
- 是否存在脚本与 app 模块耦合严重的问题。
- 是否有异常处理不足的问题。
- 是否有日志、配置、测试、文档不完善的问题。
- 是否存在不适合继续扩展的设计。

五、求职竞争力分析
请从 Agent 应用开发工程师 / 大模型应用工程师 / AI Agent 开发工程师面试官视角评价：
- 当前项目最有价值的亮点是什么？
- 当前项目最容易被质疑的地方是什么？
- 哪些部分可以写进简历？
- 哪些部分目前还不够成熟，不建议过度包装？
- 如果想从普通 RAG Demo 中脱颖而出，最应该优先补强什么？

六、输出格式
请输出一份结构化审计报告，包含：

# Project Audit Report

## 1. Current Project Summary
## 2. Directory Structure Analysis
## 3. Core Workflow Analysis
## 4. LangGraph State and Node Analysis
## 5. RAG System Analysis
## 6. Evaluation System Analysis
## 7. Engineering Quality Analysis
## 8. Strengths
## 9. Weaknesses and Risks
## 10. Job-Oriented Value Assessment
## 11. Recommended Upgrade Roadmap
## 12. Suggested Next Codex Tasks

要求：
- 语言使用中文。
- 结论明确，不要空泛。
- 每个问题尽量指出对应文件或模块。
- 不要只说“可以优化”，要说明为什么、怎么优化、优先级如何。
- 按“必须做 / 建议做 / 可暂缓做”区分后续任务。
- 本轮不改代码，只输出分析报告。