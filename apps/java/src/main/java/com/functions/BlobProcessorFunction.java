package com.functions;

import com.microsoft.azure.functions.*;
import com.microsoft.azure.functions.annotation.*;

/**
 * Blob trigger — processes blobs uploaded to the 'uploads' container.
 */
public class BlobProcessorFunction {

    @FunctionName("blobProcessor")
    @StorageAccount("AzureWebJobsStorage")
    public void run(
            @BlobTrigger(
                name = "content",
                path = "uploads/{name}",
                connection = "AzureWebJobsStorage",
                source = "EventGrid")
            byte[] content,
            @BindingName("name") String name,
            final ExecutionContext context) {

        context.getLogger().info("Processing blob: " + name + ", size: " + content.length + " bytes");
    }
}
