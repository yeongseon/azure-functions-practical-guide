import azure.functions as func
import logging

from config.telemetry import configure_telemetry
from blueprints.health import bp as health_bp
from blueprints.info import bp as info_bp
from blueprints.requests import bp as requests_bp
from blueprints.dependencies import bp as dependencies_bp
from blueprints.exceptions import bp as exceptions_bp
from blueprints.scheduled import bp as scheduled_bp
from blueprints.blob_processor import bp as blob_processor_bp

configure_telemetry()
logger = logging.getLogger(__name__)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

app.register_blueprint(health_bp)
app.register_blueprint(info_bp)
app.register_blueprint(requests_bp)
app.register_blueprint(dependencies_bp)
app.register_blueprint(exceptions_bp)
app.register_blueprint(scheduled_bp)
app.register_blueprint(blob_processor_bp)

logger.info("Azure Functions Field Guide application initialized")
