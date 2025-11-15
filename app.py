from flask import Flask, render_template, jsonify  # type: ignore
import time
from threading import Thread
from config import config
from services.thingspeak_service import thingspeak_service
from services.queue_service import persistent_queue
from utils.logging_config import logger
from routes import register_blueprints

# Global variable to track the last successful ThingSpeak write time
last_ts_write_time = 0

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY

# ThingSpeak rate limit (used by background worker)
TS_RATE_LIMIT_SECONDS = config.THINGSPEAK_RATE_LIMIT_SECONDS

# Register all route blueprints
register_blueprints(app, persistent_queue)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "message": "Electronic Medication Administration Record API is running",
        }
    )


def process_prescription_queue():
    """Background worker to process the prescription queue at the ThingSpeak rate limit."""
    global last_ts_write_time

    logger.info("Prescription queue worker started")

    while True:
        try:
            # Check if an entry is waiting and the rate limit has passed
            current_time = time.time()
            time_since_last_write = current_time - last_ts_write_time

            if time_since_last_write >= TS_RATE_LIMIT_SECONDS:
                item = persistent_queue.get_next()

                if item:
                    try:
                        # Write to ThingSpeak using service
                        entry_id = thingspeak_service.write_to_channel(
                            "medicine_prescription", item.data
                        )

                        # Treat entry_id == 0 as a failed write that should be retried
                        if isinstance(entry_id, int) and entry_id > 0:
                            logger.info(
                                f"Successfully posted prescription entry {entry_id} for patient {item.data.get('patient_id', 'unknown')}"
                            )

                            # Mark as successfully processed
                            persistent_queue.mark_success(item)

                            # Update the last successful write time
                            last_ts_write_time = time.time()
                        else:
                            error_msg = (
                                "ThingSpeak returned entry_id 0 (write not accepted)"
                            )
                            logger.warning(
                                f"Write not accepted for patient {item.data.get('patient_id', 'unknown')}: {error_msg}"
                            )
                            # Mark as failure to requeue for retry
                            persistent_queue.mark_failure(item, error_msg)
                    except Exception as e:
                        # Mark as failed with error message
                        error_msg = str(e)
                        logger.error(
                            f"Failed to post prescription for patient {item.data.get('patient_id', 'unknown')}: {error_msg}"
                        )
                        persistent_queue.mark_failure(item, error_msg)

            # Sleep for 1 second before checking the queue again
            time.sleep(1)

        except Exception as e:
            logger.error(f"Error in prescription queue worker: {e}", exc_info=True)
            time.sleep(5)  # Wait longer on error before retrying


# Start the background worker thread when the app starts
worker_thread = Thread(target=process_prescription_queue, daemon=True)
worker_thread.start()
logger.info(
    "Electronic Medication Administration Record (eMAR) application initialized"
)

if __name__ == "__main__":
    logger.info("Starting Flask development server on http://0.0.0.0:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
