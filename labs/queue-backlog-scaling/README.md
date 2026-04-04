# Lab: Queue Backlog and Scaling Behavior

## Objective
Observe how Azure Functions scales queue-triggered workloads as message backlog grows.

## Prerequisites
- Azure subscription
- Azure Functions Core Tools
- Python runtime (3.11 or later)
- Azure CLI
- Azurite (local storage emulator)

## Scenario
Your workload receives burst traffic and you need to understand processing throughput,
concurrency, and backlog drain characteristics before production rollout.
This lab simulates burst ingestion and measures host behavior over time.
Use the same payload shape across test runs to keep comparisons meaningful.

## Steps
1. Create a Python Function App.
   ```bash
   func init queue-scaling-lab --worker-runtime python
   ```
2. Add queue trigger function.
   ```bash
   cd queue-scaling-lab
   func new --template "Azure Queue Storage trigger" --name QueueConsumer
   ```
3. Start Azurite.
   ```bash
   azurite --location ".azurite" --debug ".azurite/debug.log"
   ```
4. Configure `AzureWebJobsStorage` for emulator in `local.settings.json`.
5. Add processing delay in function code (for example 500 ms) to make scaling visible.
6. Start host with verbose logs.
   ```bash
   func start --verbose
   ```
7. Enqueue 1,000 messages locally.
   ```bash
   python -c "from azure.storage.queue import QueueClient; q=QueueClient.from_connection_string('UseDevelopmentStorage=true','work-items'); q.create_queue(); [q.send_message(f'msg-{i}') for i in range(1000)]"
   ```
8. Track dequeue rate and completion timestamps.
9. Change host tuning (`batchSize`, `newBatchThreshold`) and re-run injection.
10. Record throughput differences in a comparison table.
11. Provision Azure resources for cloud scaling test.
   ```bash
   az group create --name rg-queue-scaling-lab --location eastus
   az storage account create --name stqueuescaling123 --resource-group rg-queue-scaling-lab --location eastus --sku Standard_LRS
   az functionapp create --name func-queue-scaling-123 --resource-group rg-queue-scaling-lab --storage-account stqueuescaling123 --consumption-plan-location eastus --runtime python --runtime-version 3.11 --functions-version 4
   func azure functionapp publish func-queue-scaling-123
   ```
12. Enqueue burst messages to Azure queue and monitor instance behavior.
13. Inspect platform metrics for queue length and function execution count.
   ```bash
   az monitor metrics list --resource "/subscriptions/<subscription-id>/resourceGroups/rg-queue-scaling-lab/providers/Microsoft.Storage/storageAccounts/stqueuescaling123" --metric "QueueMessageCount" --interval PT1M
   ```
14. Repeat test with larger message volume (for example 5,000 messages).
15. Compare drain time and peak queue depth across both test sizes.
16. Summarize recommended host settings for your workload profile.

## Expected Behavior
- Backlog drains gradually with visible throughput plateaus.
- Host tuning affects local pull behavior.
- Azure consumption plan scales out based on queue pressure and execution demand.
- Queue length and execution metrics correlate with observed drain time.
- Larger bursts should show higher queue depth and longer tail-drain periods.
- Throughput tuning can improve drain time at the cost of downstream pressure.

## Cleanup
```bash
az group delete --name rg-queue-scaling-lab --yes --no-wait
```
Delete local artifacts and Azurite data folder.
Remove test queues from both local and Azure storage accounts.

## See Also
- [Scaling and plans](../../docs/platform/scaling.md)
- [Queue trigger guidance](../../docs/language-guides/python/recipes/queue.md)
- [Operational scaling playbook](../../docs/platform/hosting.md)
