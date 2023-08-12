# 什么是langchain

LangChain是一个用于构建基于大型语言模型（LLM）的应用程序的库。它可以帮助开发者将LLM与其他计算或知识源结合起来，创建更强大的应用程序。

例如，可以使用LangChain开发以下类型的应用程序：

\- 在特定文档上进行问答

\- 聊天机器人

\- 智能代理

LangChain提供了以下几个主要模块来支持这些应用程序的开发：

\- Prompts：这包括提示管理、提示优化和提示序列化。

\- LLMs：这包括所有LLM的通用接口，以及与LLM相关的常用工具。

\- Document Loaders：这包括加载文档的标准接口，以及与各种文本数据源的特定集成。

\- Utils：语言模型在与其他知识或计算源交互时通常更强大。这可能包括Python REPL、嵌入、搜索引擎等。LangChain提供了一系列常用的工具来在应用程序中使用。

\- Chains：Chains不仅仅是一个单独的LLM调用，而是一系列的调用（无论是对LLM还是其他工具）。LangChain提供了链的标准接口，许多与其他工具的集成，以及常见应用程序的端到端链。

\- Indexes：语言模型在与自己的文本数据结合时通常更强大 - 这个模块涵盖了这样做的最佳实践。

\- Agents：Agents涉及到一个LLM在决定采取哪些行动、执行该行动、看到一个观察结果，并重复这个过程直到完成。LangChain提供了代理的标准接口，可供选择的代理，以及端到端代理的示例。

\- Memory：Memory是在链/代理调用之间持久化状态的概念。LangChain提供了内存的标准接口，一系列内存实现，以及使用内存的链/代理示例。

\- Chat：Chat模型是一种与语言模型不同的API - 它们不是使用原始文本，而是使用消息。LangChain提供了一个标准接口来使用它们，并做所有上述相同的事情。

LangChain是一个近期非常活跃的开源代码库，目前也还在快速发展中