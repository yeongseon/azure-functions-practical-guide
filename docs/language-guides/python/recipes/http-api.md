# HTTP API Patterns

This recipe covers the essential HTTP API patterns for Azure Functions Python v2 — route parameters, query strings, request body parsing, response codes, CORS headers, and a complete CRUD-style example.

## Route Parameters

Define route parameters using curly braces in the `route` string. Access them via `req.route_params`:

```python
import azure.functions as func
import json

bp = func.Blueprint()

@bp.route(route="items/{item_id}", methods=["GET"])
def get_item(req: func.HttpRequest) -> func.HttpResponse:
    item_id = req.route_params.get("item_id")
    if not item_id:
        return func.HttpResponse(
            json.dumps({"error": "item_id is required"}),
            mimetype="application/json",
            status_code=400
        )

    # Look up item (in-memory example)
    item = {"id": item_id, "name": f"Item {item_id}", "status": "active"}

    return func.HttpResponse(
        json.dumps(item),
        mimetype="application/json",
        status_code=200
    )
```

You can use multiple route parameters:

```python
@bp.route(route="users/{user_id}/orders/{order_id}", methods=["GET"])
def get_user_order(req: func.HttpRequest) -> func.HttpResponse:
    user_id = req.route_params.get("user_id")
    order_id = req.route_params.get("order_id")
    return func.HttpResponse(
        json.dumps({"user_id": user_id, "order_id": order_id}),
        mimetype="application/json",
        status_code=200
    )
```

## Query String Parameters

Access query string parameters using `req.params`:

```python
@bp.route(route="items", methods=["GET"])
def list_items(req: func.HttpRequest) -> func.HttpResponse:
    page = int(req.params.get("page", "1"))
    page_size = int(req.params.get("page_size", "20"))
    sort_by = req.params.get("sort_by", "created_at")

    # Calculate offset
    offset = (page - 1) * page_size

    # Return paginated response
    return func.HttpResponse(
        json.dumps({
            "items": [],  # Your data here
            "page": page,
            "page_size": page_size,
            "sort_by": sort_by,
            "offset": offset
        }),
        mimetype="application/json",
        status_code=200
    )
```

Test with: `GET /api/items?page=2&page_size=10&sort_by=name`

## Request Body Parsing

For POST and PUT requests, parse the JSON body with `req.get_json()`. Always wrap this in error handling since the body may be missing or malformed:

```python
@bp.route(route="items", methods=["POST"])
def create_item(req: func.HttpRequest) -> func.HttpResponse:
    # Parse JSON body with error handling
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON in request body"}),
            mimetype="application/json",
            status_code=400
        )

    # Validate required fields
    name = body.get("name")
    if not name:
        return func.HttpResponse(
            json.dumps({"error": "Field 'name' is required"}),
            mimetype="application/json",
            status_code=400
        )

    # Create the item
    item = {
        "id": "generated-uuid",
        "name": name,
        "description": body.get("description", ""),
        "status": "created"
    }

    return func.HttpResponse(
        json.dumps(item),
        mimetype="application/json",
        status_code=201
    )
```

For raw body access (non-JSON payloads):

```python
raw_bytes = req.get_body()       # Returns bytes
raw_text = raw_bytes.decode()    # Decode to string
```

## Response Status Codes

Return appropriate HTTP status codes to indicate the outcome:

| Status | Meaning | When to Use |
|--------|---------|-------------|
| `200` | OK | Successful GET, PUT |
| `201` | Created | Successful POST that creates a resource |
| `202` | Accepted | Async operation accepted (e.g., enqueued) |
| `204` | No Content | Successful DELETE |
| `400` | Bad Request | Invalid input, missing fields |
| `401` | Unauthorized | Missing or invalid authentication |
| `404` | Not Found | Resource does not exist |
| `500` | Internal Server Error | Unhandled exception |

```python
@bp.route(route="items/{item_id}", methods=["DELETE"])
def delete_item(req: func.HttpRequest) -> func.HttpResponse:
    item_id = req.route_params.get("item_id")

    # Simulate looking up the item
    found = True  # Replace with actual lookup

    if not found:
        return func.HttpResponse(
            json.dumps({"error": f"Item {item_id} not found"}),
            mimetype="application/json",
            status_code=404
        )

    # Delete the item
    return func.HttpResponse(status_code=204)
```

## CORS Headers

Azure Functions does not set CORS headers automatically. You must configure CORS in the Azure Portal, `host.json`, or set headers manually in your response.

### Configure CORS in host.json

```json
{
  "version": "2.0",
  "extensions": {
    "http": {
      "routePrefix": "api"
    }
  },
  "Host": {
    "CORS": {
      "AllowedOrigins": [
        "https://your-frontend.azurestaticapps.net",
        "http://localhost:3000"
      ],
      "SupportCredentials": true
    }
  }
}
```

### Configure CORS via Azure CLI

```bash
az functionapp cors add \
  --name your-func \
  --resource-group your-rg \
  --allowed-origins "https://your-frontend.azurestaticapps.net" "http://localhost:3000"
```

### Manual CORS Headers

For fine-grained control, set CORS headers in your response:

```python
@bp.route(route="items", methods=["GET", "OPTIONS"])
def list_items_with_cors(req: func.HttpRequest) -> func.HttpResponse:
    # Handle preflight OPTIONS request
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "https://your-frontend.azurestaticapps.net",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Max-Age": "86400"
            }
        )

    # Regular GET response
    return func.HttpResponse(
        json.dumps({"items": []}),
        mimetype="application/json",
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "https://your-frontend.azurestaticapps.net"
        }
    )
```

## Complete Example: CRUD API

Here is a complete CRUD-style blueprint for managing items in memory. In production, replace the in-memory store with a database or storage service.

```python
import azure.functions as func
import json
import uuid
from datetime import datetime, timezone

bp = func.Blueprint()

# In-memory store (replace with database in production)
_items: dict = {}

@bp.route(route="items", methods=["GET"])
def list_items(req: func.HttpRequest) -> func.HttpResponse:
    page = int(req.params.get("page", "1"))
    page_size = int(req.params.get("page_size", "20"))
    all_items = list(_items.values())
    start = (page - 1) * page_size
    end = start + page_size
    return func.HttpResponse(
        json.dumps({"items": all_items[start:end], "total": len(all_items)}),
        mimetype="application/json",
        status_code=200
    )

@bp.route(route="items/{item_id}", methods=["GET"])
def get_item(req: func.HttpRequest) -> func.HttpResponse:
    item_id = req.route_params.get("item_id")
    item = _items.get(item_id)
    if not item:
        return func.HttpResponse(
            json.dumps({"error": "Item not found"}),
            mimetype="application/json",
            status_code=404
        )
    return func.HttpResponse(json.dumps(item), mimetype="application/json")

@bp.route(route="items", methods=["POST"])
def create_item(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            mimetype="application/json",
            status_code=400
        )

    item_id = str(uuid.uuid4())
    item = {
        "id": item_id,
        "name": body.get("name", ""),
        "description": body.get("description", ""),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    _items[item_id] = item
    return func.HttpResponse(
        json.dumps(item), mimetype="application/json", status_code=201
    )

@bp.route(route="items/{item_id}", methods=["PUT"])
def update_item(req: func.HttpRequest) -> func.HttpResponse:
    item_id = req.route_params.get("item_id")
    if item_id not in _items:
        return func.HttpResponse(
            json.dumps({"error": "Item not found"}),
            mimetype="application/json",
            status_code=404
        )
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            mimetype="application/json",
            status_code=400
        )

    _items[item_id].update({
        "name": body.get("name", _items[item_id]["name"]),
        "description": body.get("description", _items[item_id]["description"])
    })
    return func.HttpResponse(
        json.dumps(_items[item_id]), mimetype="application/json"
    )

@bp.route(route="items/{item_id}", methods=["DELETE"])
def delete_item(req: func.HttpRequest) -> func.HttpResponse:
    item_id = req.route_params.get("item_id")
    if item_id not in _items:
        return func.HttpResponse(
            json.dumps({"error": "Item not found"}),
            mimetype="application/json",
            status_code=404
        )
    del _items[item_id]
    return func.HttpResponse(status_code=204)
```

> **Note:** In-memory storage is lost when the function instance scales down or restarts. For persistent storage, see the [Cosmos DB](cosmosdb.md) or [Blob Storage](blob-storage.md) recipes.

## See Also
- [HTTP Authentication](http-auth.md)
- [Cosmos DB Integration](cosmosdb.md)

## Sources
- [Azure Functions HTTP Trigger (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-bindings-http-webhook)
- [Python v2 Programming Model (Microsoft Learn)](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
