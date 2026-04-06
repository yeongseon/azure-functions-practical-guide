# Python v2 Programming Model

This document provides a deep dive into the Python v2 programming model for Azure Functions. The v2 model uses Python decorators to define triggers, bindings, and routes — replacing the file-based `function.json` configuration from v1.

## v1 vs. v2: What Changed

The v1 programming model required a specific directory structure with one folder per function, each containing a `function.json` configuration file and a `__init__.py` entry point:

```
# v1 structure (LEGACY — do not use)
MyFunctionApp/
  host.json
  requirements.txt
  HealthFunction/
    function.json      # Trigger/binding config
    __init__.py        # Function code
  InfoFunction/
    function.json
    __init__.py
```

The v2 model eliminates this structure entirely. Functions are defined inline using decorators, and the project structure is flat:

```
# v2 structure (CURRENT)
app/
  host.json
  requirements.txt
  function_app.py       # App entry point
  blueprints/
    health.py           # Functions organized by domain
    info.py
    requests.py
```

### Key Differences

| Aspect | v1 Model | v2 Model |
|--------|----------|----------|
| **Function config** | `function.json` per function | Python decorators |
| **Discovery** | Host scans filesystem | Worker indexes decorators |
| **Project structure** | One folder per function | Flat or modular (your choice) |
| **Feature flag** | Not needed | Not required on current runtimes (4.x+) |
| **Bindings** | JSON properties | Decorator parameters |
| **Entry point** | `__init__.py` per folder | `function_app.py` (single entry) |
| **Modularity** | Folders | `Blueprint` class |

## FunctionApp — The Application Entry Point

Every v2 Azure Functions application starts with a `FunctionApp` instance in `function_app.py`. This is the file the Python worker imports at startup.

```python
# function_app.py
import azure.functions as func

app = func.FunctionApp()
```

The `FunctionApp` class serves as the root container for all functions. You can register functions directly on the app or use Blueprints for modular organization.

### Direct Registration

For small applications with a few functions, register directly on the `FunctionApp`:

```python
import azure.functions as func
import json

app = func.FunctionApp()

@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({"status": "healthy"}),
        mimetype="application/json"
    )

@app.route(route="info", methods=["GET"])
def info(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({"name": "azure-functions-python-guide"}),
        mimetype="application/json"
    )
```

This approach is simple but becomes unwieldy with many functions.

## Blueprint — Modular Organization

The `Blueprint` class allows you to group related functions into separate modules. This is the recommended pattern for applications with more than a handful of functions.

### Defining a Blueprint

```python
# blueprints/health.py
import azure.functions as func
import json
from datetime import datetime, timezone

bp = func.Blueprint()

@bp.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    body = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }
    return func.HttpResponse(
        json.dumps(body),
        mimetype="application/json"
    )
```

### Registering Blueprints

```python
# function_app.py
import azure.functions as func

app = func.FunctionApp()

from blueprints.health import bp as health_bp
from blueprints.info import bp as info_bp
from blueprints.requests import bp as requests_bp
from blueprints.dependencies import bp as dependencies_bp
from blueprints.exceptions import bp as exceptions_bp

app.register_functions(health_bp)
app.register_functions(info_bp)
app.register_functions(requests_bp)
app.register_functions(dependencies_bp)
app.register_functions(exceptions_bp)
```

When `register_functions()` is called, all decorated functions from the Blueprint are merged into the `FunctionApp`'s function index.

### `@app.route()` vs. `@bp.route()`

| Decorator | Defined On | Use When |
|-----------|-----------|----------|
| `@app.route()` | `FunctionApp` | Small apps, quick prototypes, single-file applications |
| `@bp.route()` | `Blueprint` | Production apps, multiple function groups, team collaboration |

Both decorators accept the same parameters. The only difference is where the function is registered. Blueprints provide better separation of concerns and make testing individual modules easier.

## HttpRequest Object

The `func.HttpRequest` object provides access to all parts of the incoming HTTP request:

```python
@bp.route(route="example/{id}", methods=["GET", "POST"])
def example(req: func.HttpRequest) -> func.HttpResponse:
    # HTTP method
    method = req.method  # "GET" or "POST"

    # Route parameters (from URL path)
    item_id = req.route_params.get("id")

    # Query parameters
    page = req.params.get("page", "1")

    # Headers
    auth_header = req.headers.get("Authorization", "")
    content_type = req.headers.get("Content-Type", "")

    # Request body (raw bytes)
    raw_body = req.get_body()

    # Request body (as JSON — raises ValueError if not valid JSON)
    try:
        json_body = req.get_json()
    except ValueError:
        json_body = None

    # URL
    url = req.url  # Full request URL
```

### Key Properties and Methods

| Property/Method | Type | Description |
|----------------|------|-------------|
| `req.method` | `str` | HTTP method (GET, POST, PUT, etc.) |
| `req.url` | `str` | Full request URL |
| `req.headers` | `dict`-like | Request headers (case-insensitive keys) |
| `req.params` | `dict` | Query string parameters |
| `req.route_params` | `dict` | URL path parameters from route template |
| `req.get_body()` | `bytes` | Raw request body |
| `req.get_json()` | `dict/list` | Parsed JSON body (raises `ValueError` on invalid JSON) |

## HttpResponse Object

The `func.HttpResponse` object represents the response sent back to the client:

```python
# Simple text response
return func.HttpResponse("OK", status_code=200)

# JSON response
return func.HttpResponse(
    json.dumps({"key": "value"}),
    mimetype="application/json",
    status_code=200
)

# Response with custom headers
response = func.HttpResponse(
    json.dumps({"created": True}),
    mimetype="application/json",
    status_code=201
)
response.headers["X-Request-Id"] = "abc-123"
response.headers["Cache-Control"] = "no-store"
return response

# Error response
return func.HttpResponse(
    json.dumps({"error": "Not found"}),
    mimetype="application/json",
    status_code=404
)
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `body` | `str` or `bytes` | `None` | Response body |
| `status_code` | `int` | `200` | HTTP status code |
| `headers` | `dict` | `{}` | Response headers |
| `mimetype` | `str` | `None` | Content-Type header value |
| `charset` | `str` | `None` | Character encoding |

## Route Configuration

### Route Prefix

All HTTP trigger routes are prefixed with `/api/` by default. This is configured in `host.json`:

```json
{
  "version": "2.0",
  "extensions": {
    "http": {
      "routePrefix": "api"
    }
  }
}
```

With the default prefix, a function with `route="health"` is accessible at `/api/health`. To remove the prefix entirely:

```json
{
  "extensions": {
    "http": {
      "routePrefix": ""
    }
  }
}
```

### Route Templates

Routes support parameterized segments:

```python
@bp.route(route="users/{user_id}/orders/{order_id}", methods=["GET"])
def get_order(req: func.HttpRequest) -> func.HttpResponse:
    user_id = req.route_params["user_id"]
    order_id = req.route_params["order_id"]
    # ...
```

Route parameters are always strings. Cast them as needed:

```python
page = int(req.route_params.get("page", "1"))
```

## Complete Blueprint Example

Here is a complete blueprint demonstrating common patterns:

```python
# blueprints/products.py
import azure.functions as func
import json
import logging

bp = func.Blueprint()

# In-memory store for demo purposes
_products = {
    "1": {"id": "1", "name": "Widget", "price": 9.99},
    "2": {"id": "2", "name": "Gadget", "price": 24.99},
}

@bp.route(route="products", methods=["GET"])
def list_products(req: func.HttpRequest) -> func.HttpResponse:
    """List all products."""
    logging.info("Listing %d products", len(_products))
    return func.HttpResponse(
        json.dumps(list(_products.values())),
        mimetype="application/json"
    )

@bp.route(route="products/{product_id}", methods=["GET"])
def get_product(req: func.HttpRequest) -> func.HttpResponse:
    """Get a single product by ID."""
    product_id = req.route_params.get("product_id")
    product = _products.get(product_id)

    if product is None:
        return func.HttpResponse(
            json.dumps({"error": "Product not found"}),
            mimetype="application/json",
            status_code=404
        )

    return func.HttpResponse(
        json.dumps(product),
        mimetype="application/json"
    )

@bp.route(route="products", methods=["POST"])
def create_product(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new product."""
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            mimetype="application/json",
            status_code=400
        )

    product_id = str(len(_products) + 1)
    product = {"id": product_id, "name": body["name"], "price": body["price"]}
    _products[product_id] = product

    logging.info("Created product: %s", product_id)
    return func.HttpResponse(
        json.dumps(product),
        mimetype="application/json",
        status_code=201
    )
```

Register it in `function_app.py`:

```python
from blueprints.products import bp as products_bp
app.register_functions(products_bp)
```

This creates three endpoints:
- `GET /api/products` — List all products
- `GET /api/products/{product_id}` — Get a product by ID
- `POST /api/products` — Create a new product

## See Also

- [Python Language Guide](index.md)
- [Python Runtime](python-runtime.md)
- [Tutorial Overview & Plan Chooser](tutorial/index.md)
- [Recipes Index](recipes/index.md)

## Sources
- [Python v2 Programming Model (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Functions Overview (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-overview)
- [HTTP Trigger Reference (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-bindings-http-webhook)
- [Create Your First Function with CLI (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/create-first-function-cli-python)
