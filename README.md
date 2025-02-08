# Hello-agent

### 一、操作步骤

#### 1.1 安装软件包

1、安装 python 软件包，

> pip install -r requirements.txt

2、安装 Node，下载最新版 Node；

3、安装 mcp server-filesystem 包，

> npm install -g @modelcontextprotocol/server-filesystem

#### 1.2 修改模型 Secret

打开 model/model.py，修改 SecretStr 为你自己“通义千问”的 Secret。

#### 1.3 源码及运行配置


| 文件                                | 功能介绍                                         | 运行前修改配置                                                               |
| ----------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------- |
| app/agent/write-local-file-agent.py | 支持写入本地文件                                 |                                                                              |
| app/agent/sql-query-agent.py        | 支持语义查询 MySQL                               | 1. 文件 21～25 行的数据库配置，对应修改；<br />2. 文件 54 行的指令对应修改。 |
| app/agent/multi-agent.py            | 多 Agent，语文老师指导学生修改作文               |                                                                              |
| file_mcp/client.py                  | MCP 客户端实现，支持读、写本地文件               |                                                                              |
| agent_mcp/agent_mcp_adapt.py        | Agent + MCP，利用 MCP 的文件操作能力读写本地文件 |                                                                              |
