import azure.functions as func
import logging

bp = func.Blueprint()
logger = logging.getLogger(__name__)


@bp.blob_trigger(
    arg_name="input_blob",
    path="uploads/{name}",
    connection="AzureWebJobsStorage",
    source="EventGrid",
)
@bp.blob_output(
    arg_name="output_blob",
    path="processed/{name}",
    connection="AzureWebJobsStorage",
)
def process_blob(input_blob: func.InputStream, output_blob: func.Out[bytes]) -> None:
    """Triggered when a blob is uploaded to the 'uploads' container.

    Uses the Event Grid-based blob trigger (source="EventGrid") which is
    required for Flex Consumption and recommended for all plans. The standard
    polling blob trigger is NOT supported on Flex Consumption.

    Reads the blob content, transforms it (uppercase), and writes the result
    to the 'processed' container under the same name.

    Local testing: With Azurite, use the "Execute Function Now" feature in
    VS Code or send a manual POST to the admin endpoint to simulate the
    Event Grid callback. See the mslearn Event Grid blob trigger tutorial
    for details.

    See docs/tutorial/flex-consumption/07-extending-triggers.md for the full
    workflow including Event Grid subscription setup in Azure.
    """
    logger.info(
        "Processing blob: name=%s, size=%d bytes",
        input_blob.name,
        input_blob.length,
    )

    content = input_blob.read()
    output_blob.set(content.upper())

    # input_blob.name includes the container path (e.g. "uploads/test.txt");
    # strip the source container prefix to log just the blob name.
    blob_name = input_blob.name.removeprefix("uploads/")
    logger.info("Written to processed/%s", blob_name)
