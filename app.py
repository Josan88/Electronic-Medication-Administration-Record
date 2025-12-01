from flask import Flask, render_template, jsonify, request, send_from_directory  # type: ignore
from flask_swagger_ui import get_swaggerui_blueprint
from config import config
from routes import register_blueprints
from services.queue_service import persistent_queue
from services.workers import start_background_workers
from utils.logging_config import logger

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY

# Register all route blueprints
register_blueprints(app, persistent_queue)

# Configure Swagger UI
SWAGGER_URL = "/api/docs"
API_URL = "/swagger.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "eMAR API Documentation"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/")
def role_selection():
    """Landing page for role selection"""
    return render_template("role_selection.html")


@app.route("/nurse-login")
def nurse_login():
    """Nurse login page"""
    return render_template("nurse_login.html")


@app.route("/management-login")
def management_login():
    """Management login page"""
    return render_template("management_login.html")


@app.route("/dashboard")
def index():
    """Main dashboard after login"""
    role = request.args.get("role", "nurse")
    return render_template("index.html", role=role)


@app.route("/swagger.yaml")
def swagger_spec():
    """Serve the OpenAPI specification file"""
    return send_from_directory(".", "swagger.yaml")


@app.route("/api/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "message": "Electronic Medication Administration Record API is running",
        }
    )


# Start the background worker threads when the app starts
_worker_thread, _sync_worker_thread = start_background_workers()

logger.info(
    "Electronic Medication Administration Record (eMAR) application initialized"
)

if __name__ == "__main__":
    logger.info("Starting Flask development server on http://0.0.0.0:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
