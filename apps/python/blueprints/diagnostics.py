import azure.functions as func
import json
import logging
import os
import socket
import time

bp = func.Blueprint()
logger = logging.getLogger(__name__)


@bp.route(route="diagnostics/slow-response", methods=["GET"])
def slow_response(req: func.HttpRequest) -> func.HttpResponse:
    """Simulate slow response with configurable delay.

    Query parameters:
        delay_ms: Delay in milliseconds (default 3000, max 25000).
    """
    delay_ms = min(int(req.params.get("delay_ms", "3000")), 25000)
    logger.info("Slow response endpoint requested (delay=%dms)", delay_ms)

    start = time.monotonic()
    time.sleep(delay_ms / 1000.0)
    elapsed_ms = round((time.monotonic() - start) * 1000)

    body = json.dumps(
        {
            "status": "completed",
            "requestedDelayMs": delay_ms,
            "actualDelayMs": elapsed_ms,
        }
    )
    return func.HttpResponse(body, mimetype="application/json", status_code=200)


@bp.route(route="diagnostics/storage-probe", methods=["GET"])
def storage_probe(req: func.HttpRequest) -> func.HttpResponse:
    """Probe storage account access via managed identity.

    Tests blob service connectivity by listing containers.
    Returns success or the exact error for troubleshooting.
    """
    account_name = os.environ.get("AzureWebJobsStorage__accountName", "")
    if not account_name:
        return func.HttpResponse(
            json.dumps({"error": "AzureWebJobsStorage__accountName not set"}),
            mimetype="application/json",
            status_code=500,
        )

    logger.info("Storage probe requested (account=%s)", account_name)
    start = time.monotonic()

    try:
        from azure.identity import ManagedIdentityCredential
        from azure.storage.blob import BlobServiceClient

        client_id = os.environ.get("AzureWebJobsStorage__clientId")
        credential = ManagedIdentityCredential(client_id=client_id)
        blob_client = BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=credential,
        )
        containers = [c["name"] for c in blob_client.list_containers()]
        elapsed_ms = round((time.monotonic() - start) * 1000)

        logger.info(
            "Storage probe succeeded (%dms, %d containers)", elapsed_ms, len(containers)
        )
        body = json.dumps(
            {
                "status": "success",
                "account": account_name,
                "containers": containers,
                "elapsedMs": elapsed_ms,
            }
        )
        return func.HttpResponse(body, mimetype="application/json", status_code=200)

    except Exception as exc:
        elapsed_ms = round((time.monotonic() - start) * 1000)
        logger.error("Storage probe failed: %s (%dms)", exc, elapsed_ms)
        body = json.dumps(
            {
                "status": "error",
                "account": account_name,
                "error": type(exc).__name__,
                "message": str(exc),
                "elapsedMs": elapsed_ms,
            }
        )
        return func.HttpResponse(body, mimetype="application/json", status_code=502)


@bp.route(route="diagnostics/dns-resolve", methods=["GET"])
def dns_resolve(req: func.HttpRequest) -> func.HttpResponse:
    """Resolve a hostname and return the result for DNS troubleshooting.

    Query parameters:
        host: Hostname to resolve (required).
    """
    host = req.params.get("host", "")
    if not host:
        return func.HttpResponse(
            json.dumps({"error": "Missing 'host' query parameter"}),
            mimetype="application/json",
            status_code=400,
        )

    logger.info("DNS resolve requested (host=%s)", host)
    start = time.monotonic()

    try:
        results = socket.getaddrinfo(host, 443, socket.AF_UNSPEC, socket.SOCK_STREAM)
        elapsed_ms = round((time.monotonic() - start) * 1000)
        addresses = list({r[4][0] for r in results})

        logger.info(
            "DNS resolve succeeded: %s -> %s (%dms)", host, addresses, elapsed_ms
        )
        body = json.dumps(
            {
                "status": "resolved",
                "host": host,
                "addresses": addresses,
                "elapsedMs": elapsed_ms,
            }
        )
        return func.HttpResponse(body, mimetype="application/json", status_code=200)

    except socket.gaierror as exc:
        elapsed_ms = round((time.monotonic() - start) * 1000)
        logger.error("DNS resolve failed: %s -> %s (%dms)", host, exc, elapsed_ms)
        body = json.dumps(
            {
                "status": "failed",
                "host": host,
                "error": str(exc),
                "elapsedMs": elapsed_ms,
            }
        )
        return func.HttpResponse(body, mimetype="application/json", status_code=502)
