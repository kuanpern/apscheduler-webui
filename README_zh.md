# APScheduler WebUI

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![Python Version](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/downloads/release/python-380/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/) [![HTMX](https://img.shields.io/badge/HTMX-1.9%2B-336699.svg)](https://htmx.org/) [![APScheduler](https://img.shields.io/badge/APScheduler-3.x-blue.svg)](https://github.com/agronholm/apscheduler)

中文 | [English](README.md)

> **注意：** 本项目是原始 [Dragon-GCS/apscheduler-webui](https://github.com/Dragon-GCS/apscheduler-webui) 项目的一个分支（fork）。
> 创建此分支的原因是原项目所依赖的 [FastUI](https://github.com/pydantic/FastUI) 库已停止维护。
> 此外，本分支通过将标准的 JSON API 路由（`/api/...`）与 UI 渲染页面完全分离，为 API 调用提供了更好的支持。

**APScheduler WebUI** 是一个基于 [APScheduler](https://github.com/agronholm/apscheduler)、[FastAPI](https://fastapi.tiangolo.com/) 和 [HTMX](https://htmx.org/) 构建的轻量级、现代化的任务调度 Web 服务。

它旨在提供一个简洁直观的仪表板，用于管理和监控后台定时任务。同时它采用了双层架构：为日常人员操作提供动态 Web UI，为 SDK 和自动化脚本提供标准的 JSON API (`/api/...`)。

![screenshot](./pictures/screenshot.png)

## 目录

- [APScheduler WebUI](#apscheduler-webui)
  - [目录](#目录)
  - [特性](#特性)
  - [快速开始](#快速开始)
    - [本地部署](#本地部署)
    - [Docker](#docker)
  - [使用指南](#使用指南)
    - [任务管理](#任务管理)
    - [UV 脚本支持](#uv-脚本支持)
    - [执行器与任务存储管理](#执行器与任务存储管理)
    - [日志管理](#日志管理)
  - [开源协议](#开源协议)

## 特性

- **全面的任务控制:** 动态创建、修改、暂停、恢复、删除和重载定时任务。
- **多种触发器:** 全面支持 `Cron`、`Interval` (间隔) 和 `Date` (日期) 触发器。
- **动态基础设施:** 直接在 UI 面板中添加或移除执行器 (Executors) 和任务存储 (JobStores)。
- **高级日志视图:** 内置日志仪表板，支持按日志级别、模块进行过滤及分页查看。
- **`uv` 脚本集成:** 可直接将独立的 `uv` 脚本作为后台定时任务运行。
- **API 优先:** 完全分离的 `/api/` 路由 (返回 JSON) 和 `/ui/` 路由 (返回 HTMX HTML 渲染片段)。

---

## 快速开始

克隆仓库：

```bash
git clone https://github.com/kuanpern/apscheduler-webui
cd apscheduler-webui
```

### 本地部署

1. **安装依赖**

   我们强烈建议使用 [uv](https://docs.astral.sh/uv/) 来获得极速的依赖管理体验。

   > **注意:** 如果您只需要特定的持久化任务存储（例如仅需 Redis），您可以按需修改依赖项。默认情况下，安装 `all` 会包含 MongoDB、Redis 和 SQLAlchemy 的相关依赖包。

   ```bash
   # 使用 uv
   uv sync --extra all 
   ```

   或者使用标准的 `pip`：

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install .[all]
   ```

2. **启动服务**

   ```bash
   # 使用 uv
   uv run uvicorn main:app --host 0.0.0.0 --port 8000
   
   # 使用标准 python（在激活虚拟环境后）
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Docker

对于容器化部署，请参阅 [docker/DOCKER.md](docker/DOCKER.md)。

---

## 使用指南

### 任务管理

**通过代码添加任务:**
您可以直接在 Python 脚本中使用标准的 APScheduler 语法注册任务：

```python
from src.scheduler import scheduler

# 方式 1: 标准的函数调用
scheduler.add_job(your_func, trigger='cron', hour=12)

# 方式 2: 装饰器
@scheduler.scheduled_job('interval', minutes=5)
def scheduled_task():
    print("Running task...")
```

**通过 WebUI 添加任务 (`/`):**
要通过 UI 界面添加新任务，请使用字符串引用语法：`module:function` (模块名:函数名)。
> *提示：将您的任务脚本统一组织在特定的文件夹（如 `scripts/`）中，在 UI 里的函数字段就可以通过 `scripts.your_module:your_func` 的形式来引用。*

![job-detail](./pictures/job-detail.png)

### UV 脚本支持

如果您所在的宿主机环境已安装 `uv` 命令行工具，您可以无缝运行 [uv scripts](https://docs.astral.sh/uv/guides/scripts/)！

在 UI 表单中，将 函数 (Function) 字段设置为特殊值 `uv_run`：
* 在 `uv_script` 字段中填入目标脚本的路径。
* 在 `args` (列表格式 `[]`) 和 `kwargs` (JSON 对象格式 `{}`) 字段中提供的数据，将被自动解析并作为位置参数和标志参数传递给脚本。

> [!NOTE]
> 在底层实现中，`uv_run` 包装器会安全地派生一个子进程来执行：
> `uv run {uv_script} {arg0} {arg1} ... --{key1}={value1} --{key2}={value2}`

### 执行器与任务存储管理

- **持久化配置:** 您可以在 `src/config.py` 中硬编码您的基础调度基础设施。
- **运行时配置:** 您也可以通过 WebUI (`/store` 和 `/executor` 页面) 动态挂载或卸载 JobStores 和 Executors。
  *(注意：通过 UI 添加的基础设施是临时生效的，如果重启 FastAPI 服务，它们将会被重置为 `config.py` 中的默认状态)。*

### 日志管理

![log-view](./pictures/log-view.png)

WebUI 包含一个专门的日志页面 (`/log/jobs`)，可自动解析本地日志文件。日志分为两类：
1. **Scheduler (调度器) 日志:** 框架内部信息、任务触发记录和系统事件。
2. **Job (任务) 日志:** 您的实际脚本产生的标准输出和运行行为记录。

本项目使用 [Loguru](https://github.com/Delgan/loguru) 进行日志记录，通过 `LOGURU_FORMAT` 环境变量覆盖了标准日志行为，以确保日志格式整齐并能被 UI 准确解析。日志文件会按天安全地进行轮转，并存储在 `logs/` 目录中。

> [!IMPORTANT]
> **在 `uv` 脚本中记录日志:**
> 由于 `uv` 脚本在隔离的子进程中运行，除非显式配置，否则它们的内部日志**不会**自动同步到 UI 对应的每日日志文件中。
> 为了确保您的脚本日志能显示在 WebUI 中，请在您的脚本内执行以下操作之一：
>
> **方法 1:** 直接导入 WebUI 预设好的 logger（适用于脚本与项目在同一文件作用域的情况）：
> ```python
> from src.log import server_log as logger
> logger.info("这条日志将会出现在 WebUI 中！")
> ```
> 
> **方法 2:** 手动将脚本中的 Loguru 实例指向项目的共享日志文件：
> ```python
> from loguru import logger
> from src.config import LOG_PATH
> import datetime
>
> logger.add(
>     LOG_PATH / "jobs.{time:YYYY-MM-DD}.log", 
>     rotation=datetime.time(0, 0)
> )
> ```

---

## 开源协议

本项目基于 [MIT License](LICENSE) 开源。