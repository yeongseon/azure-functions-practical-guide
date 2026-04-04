# Python Runtime

This reference covers the Python runtime configuration for Azure Functions — supported versions, worker process settings, async function support, dependency management, and performance tuning.

## Supported Python Versions

Azure Functions v4 runtime supports the following Python versions:

| Python Version | Support Status | End of Life |
|---------------|---------------|-------------|
| **3.14** | 🔮 Preview | Pending |
| **3.13** | ✅ GA | October 2029 |
| **3.12** | ✅ GA | October 2028 |
| **3.11** | ✅ GA | October 2027 |
| **3.10** | ✅ GA | October 2026 |

The reference application uses **Python 3.11**, which benefits from CPython's specializing adaptive interpreter introduced in that release. For the latest supported versions and plan-specific availability, check the [Azure Functions supported languages](https://learn.microsoft.com/azure/azure-functions/supported-languages) page.

> **Note:** Linux Consumption supports Python 3.10–3.12. Flex Consumption, Premium, and Dedicated support Python 3.10–3.13 (GA) and 3.14 (Preview). Remote build support for Python 3.14 is not yet available on the Flex Consumption plan. Python 3.8 and 3.9 have reached end of support and are no longer available.

### Setting the Python Version

When creating a **classic Consumption** function app in Azure:

```bash
az functionapp create \
  --name your-func \
  --resource-group your-rg \
  --storage-account yourstorage \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type linux
```

> **Flex Consumption:** The `--consumption-plan-location` flag creates a classic Consumption plan. To create a Flex Consumption app, use `az functionapp create` with a pre-created Flex Consumption plan (`--plan`), or use the Bicep template in `infra/main.bicep`. See [Flex Consumption plan](https://learn.microsoft.com/azure/azure-functions/flex-consumption-how-to) for CLI details.

> **Important:** Azure Functions for Python only runs on Linux. The `--os-type linux` flag is required.

### Checking the Current Version

```bash
az functionapp config show \
  --name your-func \
  --resource-group your-rg \
  --query "linuxFxVersion" --output tsv
# Output: Python|3.11
```

## Worker Process Settings

### PYTHON_THREADPOOL_THREAD_COUNT

Controls the number of threads in the Python worker's thread pool. Synchronous functions execute in this thread pool, so increasing it allows more concurrent function invocations per worker process.

| Value | Behaviour |
|-------|-----------|
| Default (not set) | Number of CPUs on the instance (minimum 1) |
| `1` | Single-threaded — functions execute sequentially |
| `16` | Up to 16 concurrent synchronous functions per worker process |

```bash
az functionapp config appsettings set \
  --name your-func \
  --resource-group your-rg \
  --settings "PYTHON_THREADPOOL_THREAD_COUNT=16"
```

**When to increase:** If your functions are I/O-bound (making HTTP calls, querying databases, reading files). The GIL is released during I/O operations, so additional threads provide real concurrency.

**When not to increase:** If your functions are CPU-bound (data processing, computation). More threads will not help due to the GIL and may increase memory usage.

### FUNCTIONS_WORKER_PROCESS_COUNT

Run multiple Python worker processes to increase throughput beyond what a single process can handle:

```bash
az functionapp config appsettings set \
  --name your-func \
  --resource-group your-rg \
  --settings "FUNCTIONS_WORKER_PROCESS_COUNT=4"
```

| Setting | Default | Maximum |
|---------|---------|---------|
| Worker processes | `1` | `10` |

Each worker process:

- Has its own Python interpreter and memory space
- Handles requests independently
- Consumes additional memory (typically 50–150 MB per process)

> **Memory Warning:** On the Consumption plan, each instance has **1.5 GB** of memory. On Flex Consumption, instance memory is configurable (**512 MB**, **2048 MB**, or **4096 MB**). With 4 worker processes, divide the available memory accordingly. Monitor memory usage and reduce worker count if you hit the limit.

Total concurrency per instance:

```
Max concurrent invocations = WORKER_PROCESS_COUNT × THREADPOOL_THREAD_COUNT
```

Example: 4 processes × 16 threads = 64 concurrent invocations per instance.

## Async Function Support

Azure Functions Python v2 supports `async def` functions. Async functions run on the event loop directly, bypassing the thread pool:

```python
import azure.functions as func
import json
import httpx

bp = func.Blueprint()

@bp.route(route="async-demo", methods=["GET"])
async def async_demo(req: func.HttpRequest) -> func.HttpResponse:
    """Async function — runs on the event loop, not in the thread pool."""
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.example.com/data")
        data = resp.json()

    return func.HttpResponse(
        json.dumps(data),
        mimetype="application/json",
        status_code=200
    )
```

### When to Use Async

| Pattern | Recommendation |
|---------|---------------|
| Single outbound HTTP call | Either sync or async — minimal difference |
| Multiple concurrent outbound calls | **Async** — use `asyncio.gather` for parallelism |
| CPU-bound computation | **Sync** — async provides no benefit for CPU work |
| Database queries | **Async** if the SDK supports it (e.g., `azure-cosmos` has async) |

### Multiple Concurrent Calls

```python
import asyncio
import httpx

@bp.route(route="parallel-fetch", methods=["GET"])
async def parallel_fetch(req: func.HttpRequest) -> func.HttpResponse:
    """Fetch multiple URLs in parallel using asyncio.gather."""
    urls = [
        "https://api.example.com/users",
        "https://api.example.com/orders",
        "https://api.example.com/products"
    ]

    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    results = {}
    for url, resp in zip(urls, responses):
        if isinstance(resp, Exception):
            results[url] = {"error": str(resp)}
        else:
            results[url] = {"status": resp.status_code}

    return func.HttpResponse(
        json.dumps(results),
        mimetype="application/json",
        status_code=200
    )
```

## Virtual Environment and Dependency Management

### requirements.txt

The `requirements.txt` file must be in the **root directory** of your function app (the same directory as `function_app.py`). The Azure Functions deployment process runs `pip install -r requirements.txt` during remote build.

```
azure-functions>=1.17.0
httpx>=0.25.0
azure-identity>=1.15.0
azure-storage-blob>=12.19.0
```

> **Important:** Always pin or constrain package versions to avoid unexpected breaking changes in production. Use `>=` for minimum versions or `==` for exact pins.

### Local Development

Always use a virtual environment locally:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

The `.venv` directory should be excluded from deployment via `.funcignore`:

```
.venv/
__pycache__/
.git/
*.pyc
local.settings.json
```

### Dependency Isolation

The `PYTHON_ISOLATE_WORKER_DEPENDENCIES` setting (default `1`) isolates the worker's internal dependencies from your function dependencies. This prevents version conflicts between the Azure Functions worker packages and your application packages.

```bash
# Default (recommended) — isolation enabled
az functionapp config appsettings set \
  --name your-func \
  --resource-group your-rg \
  --settings "PYTHON_ISOLATE_WORKER_DEPENDENCIES=1"
```

### Large Dependencies

If your function app uses large packages (ML libraries like `scikit-learn`, `tensorflow`, `pandas`), consider:

1. **Remote build** — always use remote build so packages are compiled for Linux
2. **Custom Docker image** — for very large dependency trees, use a custom container image
3. **Lazy imports** — import heavy packages inside function bodies to reduce cold start

## See Also
- [Environment Variables](environment-variables.md)
- [Platform Limits](platform-limits.md)
- [Scaling](../../platform/scaling.md)

## Sources
- [Python v2 Programming Model (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Functions Overview (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-overview)
