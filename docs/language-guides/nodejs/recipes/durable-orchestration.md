---
content_sources:

  references:
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-node-model-upgrade
    - type: mslearn-adapted
      url: https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
  diagrams:
    - id: architecture
      type: flowchart
      source: self-generated
      justification: Illustrative logical call view of one HTTP-starter, Durable-client, orchestrator and three-activity workflow in the Node.js v4 model; shows role relationships and the recipe's call order, not hosting topology, a measured trace or parallel execution.
      based_on:
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-node-model-upgrade
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview
        - https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-types-features-overview
---
# Durable Orchestration

This recipe implements a complete Durable Functions Node.js v4 workflow with an HTTP starter, orchestrator, and activity function.

## Architecture

<!-- diagram-id: architecture -->
```mermaid
flowchart TD
    accTitle: Node.js Durable workflow roles
    accDescr: The HTTP starter uses a Durable client to start the orchestrator, which calls the three named activities. Arrows show logical dependencies, not parallel execution.
    START[HTTP Starter] --> CLIENT[Durable Client]
    CLIENT --> ORCH[Orchestrator Function]
    ORCH --> ACT1["Activity 1<br/>validateOrder"]
    ORCH --> ACT2["Activity 2<br/>reserveInventory"]
    ORCH --> ACT3["Activity 3<br/>emitConfirmation"]
    %% Layout-only tiers; these links add no calls or execution-order arrows.
    ACT1 ~~~ ACT2
    ACT2 ~~~ ACT3
    classDef neutral fill:#f2f4f8,stroke:#707e93,stroke-width:1.5px,color:#14202e;
    class START,CLIENT,ORCH,ACT1,ACT2,ACT3 neutral;
```

**Reading key:** Arrows show the starter/client/orchestrator call relationships.
Activities 1–3 are `validateOrder`, `reserveInventory` and `emitConfirmation`;
the recipe below calls them in that order, not in parallel.

## Prerequisites

Install durable package:

```bash
npm install durable-functions
```

Use extension bundle v4 in `host.json`:

```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

## Working Node.js v4 Code

```javascript
const { app } = require("@azure/functions");
const df = require("durable-functions");

app.http("startOrderOrchestration", {
  methods: ["POST"],
  route: "orchestrators/order-processing",
  authLevel: "function",
  extraInputs: [df.input.durableClient()],
  handler: async (request, context) => {
    const payload = await request.json();
    const client = df.getClient(context);

    const instanceId = await client.startNew("orderProcessingOrchestrator", {
      input: payload
    });

    context.log("Started orchestration", { instanceId });
    return client.createCheckStatusResponse(request, instanceId);
  }
});

df.app.orchestration("orderProcessingOrchestrator", function* (context) {
  const input = context.df.getInput();

  const validatedOrder = yield context.df.callActivity("validateOrder", input);
  const inventory = yield context.df.callActivity("reserveInventory", validatedOrder);
  const confirmation = yield context.df.callActivity("emitConfirmation", inventory);

  return confirmation;
});

df.app.activity("validateOrder", {
  handler: (order) => {
    if (!order?.orderId || !order?.customerId) {
      throw new Error("orderId and customerId are required.");
    }
    return { ...order, validatedUtc: new Date().toISOString() };
  }
});

df.app.activity("reserveInventory", {
  handler: (order) => {
    return {
      ...order,
      inventoryReservationId: `${order.orderId}-inv`
    };
  }
});

df.app.activity("emitConfirmation", {
  handler: (order) => {
    return {
      orderId: order.orderId,
      reservationId: order.inventoryReservationId,
      status: "Confirmed"
    };
  }
});
```

## Implementation Notes

- Use `df.input.durableClient()` + `df.getClient(context)` in the HTTP starter for orchestration control APIs.
- Start orchestrations with the durable client start API (`client.startNew(...)`, often described as `df.app.client.start()` in starter patterns).
- Keep orchestrator logic deterministic: no random values, no network calls, no current-time APIs inside orchestrator code.
- Put all external interactions in activities (`df.app.activity(...)`).

## Review Matrix

| Review area | Page-specific check |
|---|---|
| Scope | Confirm the guidance applies to Durable Orchestration. |
| Source basis | Validate the recommendation against the Microsoft Learn sources in this page. |
| Evidence | Capture command output, portal state, metrics, logs, or screenshots before treating the result as proven. |

## See Also
- [Node.js Recipes Index](index.md)
- [Timer Jobs](timer.md)
- [Node.js v4 Programming Model](../v4-programming-model.md)

## Sources
- [Migrate Durable Functions app to Node.js v4 model (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-node-model-upgrade)
- [Durable Functions overview (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview)
