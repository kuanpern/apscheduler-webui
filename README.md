# APScheduler WebUI

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![Python Version](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/downloads/release/python-380/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/) [![HTMX](https://img.shields.io/badge/HTMX-1.9%2B-336699.svg)](https://htmx.org/) [![APScheduler](https://img.shields.io/badge/APScheduler-3.x-blue.svg)](https://github.com/agronholm/apscheduler)

[中文](README_zh.md) | English

> **Note:** This is a fork of the original [Dragon-GCS/apscheduler-webui](https://github.com/Dragon-GCS/apscheduler-webui) project.
> It was created because [FastUI](https://github.com/pydantic/FastUI), which the original project depended on, has been deactivated.
> Additionally, this fork provides better support for API usage by cleanly separating standard JSON API endpoints (`/api/...`) from UI rendering.

**APScheduler WebUI** is a lightweight, modern task-scheduling web service built on [APScheduler](https://github.com/agronholm/apscheduler), [FastAPI](https://fastapi.tiangolo.com/), and [HTMX](https://htmx.org/). 

It is designed to provide a clean and intuitive dashboard for managing and monitoring scheduled background tasks, while offering a dual-layer architecture: a dynamic web UI for humans, and a standard JSON API (`/api/...`) for SDKs and automation.

![screenshot](./pictures/screenshot.png)

## Table of Contents

- [APScheduler WebUI](#apscheduler-webui)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Quick Start](#quick-start)
    - [Local Deployment](#local-deployment)
    - [Docker](#docker)
  - [Usage Guide](#usage-guide)
    - [Managing Jobs](#managing-jobs)
    - [UV Script Support](#uv-script-support)
    - [Managing Executors and JobStores](#managing-executors-and-jobstores)
    - [Log Management](#log-management)
  - [License](#license)

## Features

- **Comprehensive Job Control:** Create, modify, pause, resume, remove, and reload jobs dynamically.
- **Multiple Triggers:** Full support for `Cron`, `Interval`, and `Date` triggers.
- **Dynamic Infrastructure:** Add and remove Executors and JobStores directly from the UI.
- **Advanced Log Viewer:** Built-in log dashboard with filtering by log level, module, and pagination.
- **`uv` Script Integration:** Run isolated `uv` scripts directly as scheduled background tasks.
- **API First:** Fully separated `/api/` endpoints (JSON) and `/ui/` endpoints (HTMX HTML fragments).

---

## Quick Start

Clone the repository:

```bash
git clone https://github.com/kuanpern/apscheduler-webui
cd apscheduler-webui
```

### Local Deployment

1. **Install dependencies**

   We highly recommend using [uv](https://docs.astral.sh/uv/) for lightning-fast dependency management.

   > **Note:** If you only need specific persistent job stores (e.g., only Redis), you can edit the dependencies. By default, installing `all` includes packages for MongoDB, Redis, and SQLAlchemy.

   ```bash
   # Using uv
   uv sync --extra all 
   ```

   Or using standard `pip`:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install .[all]
   ```

2. **Start the server**

   ```bash
   # Using uv
   uv run uvicorn main:app --host 0.0.0.0 --port 8000
   
   # Using standard python (with venv activated)
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Docker

For containerized deployment, please see [docker/DOCKER.md](docker/DOCKER.md).

---

## Usage Guide

### Managing Jobs

**Adding Jobs via Code:**
You can register jobs directly in your python scripts using the standard APScheduler syntax:

```python
from src.scheduler import scheduler

# Method 1: standard function call
scheduler.add_job(your_func, trigger='cron', hour=12)

# Method 2: decorator
@scheduler.scheduled_job('interval', minutes=5)
def scheduled_task():
    print("Running task...")
```

**Adding Jobs via WebUI (`/`):**
To add a new job through the UI, use the string reference syntax: `module:function`. 
> *Tip: Keep your job scripts organized in a specific folder (e.g., `scripts/`) and reference them in the UI as `scripts.your_module:your_func`.*

![job-detail](./pictures/job-detail.png)

### UV Script Support

If the `uv` CLI tool is available on your host, you can seamlessly run [uv scripts](https://docs.astral.sh/uv/guides/scripts/)! 

In the UI, set the Function field to the special value `uv_run`. 
* Pass the target script path into the `uv_script` field.
* Data provided in the `args` (list format) and `kwargs` (JSON object format) fields will be securely passed as positional and flag arguments.

> [!NOTE]
> Behind the scenes, the `uv_run` wrapper securely spawns a subprocess:
> `uv run {uv_script} {arg0} {arg1} ... --{key1}={value1} --{key2}={value2}`

### Managing Executors and JobStores

- **Persistent Configuration:** Hardcode your base infrastructure inside `src/config.py`.
- **Runtime Configuration:** You can dynamically attach/detach JobStores and Executors via the WebUI (`/store`, `/executor`). 
  *(Note: Infrastructure added via the UI is transient and will reset to `config.py` defaults if the FastAPI service is restarted).*

### Log Management

![log-view](./pictures/log-view.png)

The WebUI includes a dedicated logs page (`/log/jobs`) that automatically parses local log files. Logs are categorized into two types:
1. **Scheduler Logs:** Internal information, job triggers, and system events.
2. **Job Logs:** The standard output and executed behavior of your actual scripts.

The project utilizes [Loguru](https://github.com/Delgan/loguru) for logging, overriding standard logging behavior via the `LOGURU_FORMAT` environment variable to ensure logs are neatly formatted and parsed by the UI. Log files are securely rotated and stored in the `logs/` directory.

> [!IMPORTANT]
> **Logging inside `uv` Scripts:**
> Because `uv` scripts run in isolated subprocesses, their internal logging won't automatically sync to the UI's daily log file unless explicitly configured. 
> To ensure your script's logs show up in the WebUI, do one of the following inside your script:
>
> **Method 1:** Import the configured WebUI logger directly (works if script is in project scope):
> ```python
> from src.log import server_log as logger
> logger.info("This will appear in the WebUI!")
> ```
> 
> **Method 2:** Manually point your script's Loguru instance to the shared log file:
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

## License

This project is open-sourced under the [MIT License](LICENSE).