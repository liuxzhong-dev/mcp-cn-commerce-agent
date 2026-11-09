# 基于 MCP 协议的电商数据分析 Agent (mcp-cn-commerce)

> 本项目在原开源项目 **mcp-cn-commerce** 基础上做了本地化部署与调试改进：重写了服务端 Mock 响应层，并完成 Cherry Studio / DeepSeek 的客户端与模型适配。下文「核心亮点」第 2 条就是这部分改动。

本项目是一个基于 Anthropic **MCP (Model Context Protocol)** 标准架构构建的电商自动化分析智能体（Agent）。
系统通过将大语言模型（LLM）与拼多多/抖店工具链进行解耦对接，实现了利用自然语言驱动工具调用（Tool Calling），完成店铺商品查询、订单分析与经营决断输出。

---

## 🌟 核心亮点与工程改进

1. **MCP 标准架构落地**：遵循 Model Context Protocol 协议规范，通过 Stdio 管道实现 Client 与 本地 MCP Server 的双向通信。
2. **Mock 数据层设计（免真实凭证离线运行）**：重写服务端核心 `_call` 响应逻辑，注入规范的电商业务模拟 JSON 数据，无需企业级真实 API 凭证即可实现全流程离线运行与 Agent 链路验证。
3. **多客户端与多模型解耦**：验证了架构的跨平台兼容性，成功从 Claude Desktop 迁移至 **Cherry Studio**，并适配 **DeepSeek-V3 / R1** 大模型，将工具调用成本降低 90% 以上。

---

## 🛠️ 技术栈

* **Protocol**: Model Context Protocol (MCP)
* **Language**: Python 3.10+
* **Dependency Manager**: `uv`
* **Clients Supported**: Cherry Studio, Claude Desktop, Cursor
* **Models Tested**: DeepSeek-V3, DeepSeek-R1, Claude 3.5 Sonnet

---

## 🚀 快速本地部署

### 1. 克隆本项目与安装依赖
```bash
git clone https://github.com/liuxzhong-dev/mcp-cn-commerce-agent.git
cd mcp-cn-commerce-agent
uv sync
```

### 2. 在 Cherry Studio 中配置 MCP 服务

在 Cherry Studio 的「设置 → MCP 服务器」中添加：

名称: mcp-cn-commerce

类型: stdio

命令: uv

参数: run mcp-cn-commerce start pinduoduo

环境变量:
PINDUODUO_CLIENT_ID=mock_client_id
PINDUODUO_CLIENT_SECRET=mock_client_secret
PINDUODUO_ACCESS_TOKEN=mock_access_token

💡 使用示例
在客户端对话框中发送指令：

"帮我查一下拼多多店铺的商品和订单列表，分析一下哪款衬衫卖得最好。"

Agent 智能体执行链路：

识别意图，触发 get_product_list 和 get_order_list 工具。

本地 MCP Server 拦截请求并返回 Mock 结构化数据。

大模型解析 JSON 数据并生成诊断报告。
