# OpenClaw 中文使用教程

> 本文档基于 OpenClaw 官方文档总结制作，最后更新时间：2026-03-23

## 目录

- [什么是 OpenClaw](#什么是-openclaw)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [常用命令](#常用命令)
- [常见问题](#常见问题)
- [更新日志](#更新日志)

---

## 什么是 OpenClaw

OpenClaw 是一个**自托管的网关**，可以将你喜欢的聊天应用（WhatsApp、Telegram、Discord、iMessage 等）连接到 AI 编程助手。你只需在自己的机器（或服务器）上运行一个 Gateway 进程，它就会成为你的消息应用和始终可用的 AI 助手之间的桥梁。

### 主要特性

- 🚀 **多渠道网关** - 一个 Gateway 进程同时服务 WhatsApp、Telegram、Discord、iMessage 等
- 🔌 **插件渠道** - 通过扩展包添加 Mattermost 等更多渠道
- 🤖 **多代理路由** - 每个代理、工作区或发送者都有独立会话
- 📷 **媒体支持** - 发送和接收图片、音频和文档
- 🖥️ **Web 控制面板** - 用于聊天、配置、会话和节点的浏览器仪表板
- 📱 **移动端节点** - 配对 iOS 和 Android 节点，用于 Canvas、相机和语音工作流

### 适用人群

开发人员和高级用户，希望拥有一个可以从任何地方发消息的个人 AI 助手——而无需放弃数据控制权或依赖托管服务。

---

## 快速开始

### 前置要求

- **Node.js** - 推荐 Node 24（也支持 Node 22.16+）
- **API 密钥** - 来自模型提供商（Anthropic、OpenAI、Google 等）- 入门向导会提示你

检查 Node 版本：
```bash
node --version
```

### 安装 OpenClaw

#### macOS / Linux

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

#### Windows (PowerShell)

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

> **注意**：其他安装方式（Docker、Nix、npm）请参考官方文档。

### 运行入门向导

```bash
openclaw onboard --install-daemon
```

向导会引导你选择模型提供商、设置 API 密钥和配置 Gateway，大约需要 2 分钟。

### 验证 Gateway 是否运行

```bash
openclaw gateway status
```

你应该看到 Gateway 在 18789 端口上监听。

### 打开仪表板

```bash
openclaw dashboard
```

这会在浏览器中打开控制面板。如果能加载，说明一切正常。

### 发送第一条消息

在控制面板聊天中输入一条消息，你应该会收到 AI 回复。

想从手机聊天？最快设置的渠道是 [Telegram](/channels/telegram)（只需一个机器人令牌）。

---

## 配置说明

OpenClaw 从 `~/.openclaw/openclaw.json` 读取可选的 **JSON5** 配置（支持注释和尾随逗号）。

如果文件缺失，OpenClaw 使用安全默认值。添加配置的常见原因：

- 连接渠道并控制谁可以给机器人发消息
- 设置模型、工具、沙箱或自动化（cron、hooks）
- 调整会话、媒体、网络或 UI

### 最小配置

```json5
// ~/.openclaw/openclaw.json
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

### 编辑配置的方式

#### 1. 交互式向导

```bash
openclaw onboard       # 完整入门流程
openclaw configure     # 配置向导
```

#### 2. CLI（单行命令）

```bash
openclaw config get agents.defaults.workspace
openclaw config set agents.defaults.heartbeat.every "2h"
openclaw config unset plugins.entries.brave.config.webSearch.apiKey
```

#### 3. 控制面板

打开 [http://127.0.0.1:18789](http://127.0.0.1:18789) 并使用 **Config** 选项卡。
控制面板从配置模式渲染表单，并提供 **Raw JSON** 编辑器作为后备方案。

#### 4. 直接编辑

直接编辑 `~/.openclaw/openclaw.json`。Gateway 监视文件并自动应用更改。

### 严格验证

> **警告**：OpenClaw 只接受完全匹配模式的配置。未知的键、格式错误的类型或无效值会导致 Gateway **拒绝启动**。

验证失败时：

- Gateway 不启动
- 只有诊断命令有效（`openclaw doctor`、`openclaw logs`、`openclaw health`、`openclaw status`）
- 运行 `openclaw doctor` 查看确切问题
- 运行 `openclaw doctor --fix`（或 `--yes`）应用修复

### 常见配置任务

#### 设置渠道（WhatsApp、Telegram、Discord 等）

每个渠道在 `channels.<provider>` 下都有自己的配置部分。

所有渠道共享相同的 DM 策略模式：

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "123:abc",
      dmPolicy: "pairing",   // pairing | allowlist | open | disabled
      allowFrom: ["tg:123"], // 仅用于 allowlist/open
    },
  },
}
```

#### 选择和配置模型

设置主模型和可选的回退：

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["openai/gpt-5.2"],
      },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "openai/gpt-5.2": { alias: "GPT" },
      },
    },
  },
}
```

#### 控制谁可以给机器人发消息

DM 访问通过 `dmPolicy` 按渠道控制：

- `"pairing"`（默认）：未知发送者获得一次性配对码以批准
- `"allowlist"`：仅 `allowFrom` 中的发送者（或配对的允许存储）
- `"open"`：允许所有入站 DM（需要 `allowFrom: ["*"]`）
- `"disabled"`：忽略所有 DM

对于群组，使用 `groupPolicy` + `groupAllowFrom` 或渠道特定的允许列表。

### 配置热重载

Gateway 监视 `~/.openclaw/openclaw.json` 并自动应用更改——大多数设置无需手动重启。

#### 重载模式

| 模式 | 行为 |
|------|------|
| **`hybrid`**（默认） | 立即热应用安全更改。关键更改自动重启。 |
| **`hot`** | 仅热应用安全更改。需要重启时记录警告——你自己处理。 |
| **`restart`** | 任何配置更改都重启 Gateway，无论是否安全。 |
| **`off`** | 禁用文件监视。更改在下次手动重启时生效。 |

```json5
{
  gateway: {
    reload: { mode: "hybrid", debounceMs: 300 },
  },
}
```

---

## 常用命令

### Gateway 管理

```bash
openclaw gateway status    # 查看 Gateway 状态
openclaw gateway start     # 启动 Gateway
openclaw gateway stop      # 停止 Gateway
openclaw gateway restart   # 重启 Gateway
```

### 配置管理

```bash
openclaw onboard           # 运行完整入门向导
openclaw configure         # 运行配置向导
openclaw config get <key>  # 获取配置值
openclaw config set <key> <value>  # 设置配置值
openclaw config unset <key>         # 取消设置配置值
```

### 诊断和故障排除

```bash
openclaw doctor            # 运行诊断检查
openclaw doctor --fix      # 自动修复问题
openclaw logs              # 查看日志
openclaw health            # 检查健康状态
openclaw status            # 查看状态
```

### 其他常用命令

```bash
openclaw dashboard         # 打开控制面板
openclaw agents            # 列出代理
openclaw sessions          # 列出会话
openclaw skills            # 管理技能
openclaw plugins           # 管理插件
openclaw update            # 更新 OpenClaw
```

---

## 常见问题

### Gateway 无法启动

1. 运行 `openclaw doctor` 查看确切问题
2. 检查配置文件 `~/.openclaw/openclaw.json` 是否有语法错误
3. 确保使用 JSON5 格式（支持注释和尾随逗号）

### 如何连接 Telegram

1. 在 [@BotFather](https://t.me/BotFather) 创建机器人并获取令牌
2. 运行 `openclaw configure` 或直接编辑配置文件：
   ```json5
   {
     channels: {
       telegram: {
         enabled: true,
         botToken: "你的机器人令牌",
         dmPolicy: "pairing",
       },
     },
   }
   ```

### 如何更换模型

使用配置向导或直接编辑配置：

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["openai/gpt-5.2"],
      },
    },
  },
}
```

### 更多帮助

- 查看官方文档：https://docs.openclaw.ai
- 运行 `openclaw help` 获取命令列表
- 访问控制面板：http://127.0.0.1:18789

---

## 更新日志

本文档每周一自动检查并更新。

### 2026-03-23
- 初始版本创建
- 基于官方文档总结快速开始、配置说明、常用命令等内容
- 添加更新日志记录机制

