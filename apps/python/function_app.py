import azure.functions as func
import azure.durable_functions as df
import logging
import os

from config.telemetry import configure_telemetry
from blueprints.health import bp as health_bp
from blueprints.info import bp as info_bp
from blueprints.requests import bp as requests_bp
from blueprints.dependencies import bp as dependencies_bp
from blueprints.exceptions import bp as exceptions_bp
from blueprints.diagnostics import bp as diagnostics_bp
from blueprints.durable_lab import bp as durable_lab_bp
from blueprints.durable_lab import http_bp as durable_lab_http_bp
from blueprints.eventhub_lab import bp as eventhub_lab_bp

configure_telemetry()
logger = logging.getLogger(__name__)

app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Core blueprints
app.register_blueprint(health_bp)
app.register_blueprint(info_bp)
app.register_blueprint(requests_bp)
app.register_blueprint(dependencies_bp)
if os.environ.get("LAB_ENDPOINTS_ENABLED") == "true":
    app.register_blueprint(exceptions_bp)
    app.register_blueprint(diagnostics_bp)
    app.register_blueprint(durable_lab_http_bp)

# Lab blueprints
app.register_blueprint(durable_lab_bp)
app.register_blueprint(eventhub_lab_bp)

if os.environ.get("QUEUE_LAB_ENABLED") == "true":
    from blueprints.queue_processor import bp as queue_processor_bp

    app.register_blueprint(queue_processor_bp)

if os.environ.get("TIMER_LAB_ENABLED") == "true":
    from blueprints.timer_lab import bp as timer_lab_bp

    app.register_blueprint(timer_lab_bp)

if os.environ.get("SCHEDULED_TRIGGER_ENABLED") == "true":
    from blueprints.scheduled import bp as scheduled_bp

    app.register_blueprint(scheduled_bp)

if os.environ.get("BLOB_TRIGGER_ENABLED") == "true":
    from blueprints.blob_processor import bp as blob_processor_bp

    app.register_blueprint(blob_processor_bp)

logger.info("Azure Functions Practical Guide application initialized")
