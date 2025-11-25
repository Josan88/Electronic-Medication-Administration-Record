from flask import Flask, render_template, jsonify, request, send_from_directory  # type: ignore
import time
from threading import Thread
from flask_swagger_ui import get_swaggerui_blueprint
from config import config
from services.thingspeak_service import thingspeak_service
from services.queue_service import persistent_queue
from services.local_db_service import local_db
from services.sync_service import sync_queue
from services.thingspeak_bulk_service import thingspeak_bulk_service
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


def process_prescription_queue():
    """Background worker to process the prescription queue to local database."""
    logger.info("Prescription queue worker started")

    while True:
        try:
            # Check if an entry is waiting
            item = persistent_queue.get_next()

            if item:
                try:
                    # Write to local database (no rate limit)
                    entry_id = local_db.write_to_channel(
                        "medicine_prescription", item.data
                    )

                    if entry_id and entry_id > 0:
                        logger.info(
                            f"Successfully posted prescription entry {entry_id} for patient {item.data.get('patient_id', 'unknown')} to local database"
                        )

                        # Mark as successfully processed
                        persistent_queue.mark_success(item)
                    else:
                        error_msg = "Local database returned invalid entry_id"
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


def process_thingspeak_sync():
    """Background worker to sync local database to ThingSpeak using bulk write."""
    logger.info("ThingSpeak sync worker started")

    # Sync interval in seconds (e.g., every 5 minutes)
    SYNC_INTERVAL_SECONDS = 300
    
    # Track last write time per channel to respect ThingSpeak rate limits (15s)
    last_write_times = {
        'patient_info': 0.0,
        'medicine_prescription': 0.0,
        'medicine_track': 0.0
    }
    THINGSPEAK_RATE_LIMIT = 15  # seconds between writes to same channel

    while True:
        try:
            # Check for pending sync operations
            item = sync_queue.get_next_ready_item()

            if item:
                try:
                    channel_name = item.channel_name
                    since_entry_id = item.since_entry_id
                    
                    # Check ThingSpeak rate limit for this channel
                    current_time = time.time()
                    time_since_last_write = current_time - last_write_times.get(channel_name, 0)
                    
                    if time_since_last_write < THINGSPEAK_RATE_LIMIT:
                        # Too soon to write to this channel, reschedule for later
                        wait_time = THINGSPEAK_RATE_LIMIT - time_since_last_write
                        item.next_retry_at = current_time + wait_time
                        logger.debug(
                            f"Rate limit: waiting {wait_time:.1f}s before syncing {channel_name}"
                        )
                        time.sleep(1)
                        continue

                    # Get feeds from local database that need to be synced
                    feeds = local_db.get_feeds_for_bulk_write(
                        channel_name, since_entry_id
                    )

                    if feeds:
                        # Prepare batches (max 100 per batch as per ThingSpeak limits)
                        batches = thingspeak_bulk_service.prepare_feeds_for_bulk_write(
                            feeds, max_batch_size=100
                        )

                        logger.info(
                            f"Syncing {len(feeds)} entries to ThingSpeak {channel_name} "
                            f"in {len(batches)} batches"
                        )

                        # Write each batch
                        for batch_idx, batch in enumerate(batches):
                            result = thingspeak_bulk_service.bulk_write_to_channel(
                                channel_name, batch
                            )
                            logger.info(
                                f"Batch {batch_idx + 1}/{len(batches)} synced: "
                                f"{result.get('feeds_written', 0)} entries"
                            )

                            # Update last write time after successful write
                            last_write_times[channel_name] = time.time()

                            # Delay between batches to respect rate limits
                            if batch_idx < len(batches) - 1:
                                time.sleep(THINGSPEAK_RATE_LIMIT)

                        # Mark as success with highest entry_id synced
                        highest_entry_id = max(
                            feed.get("entry_id", 0) for feed in feeds
                        )
                        sync_queue.mark_success(item, highest_entry_id)
                    else:
                        # No new data to sync, mark as success
                        sync_queue.mark_success(item, since_entry_id)
                        logger.debug(f"No new data to sync for {channel_name}")

                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Failed to sync {item.channel_name}: {error_msg}")
                    sync_queue.mark_failure(item, error_msg)
            else:
                # No pending items, schedule periodic sync for all channels
                # Check if enough time has passed since last sync
                current_time = time.time()
                last_sync = sync_queue.stats.get("last_sync_time")

                # If last_sync is None, initialize to 0 (never synced)
                if last_sync is None:
                    last_sync = 0

                if current_time - last_sync >= SYNC_INTERVAL_SECONDS:
                    # Queue sync operations for all channels
                    for channel_name in [
                        "patient_info",
                        "medicine_prescription",
                        "medicine_track",
                    ]:
                        last_synced_entry_id = sync_queue.get_last_synced_entry_id(
                            channel_name
                        )
                        sync_queue.add_sync_operation(
                            channel_name, last_synced_entry_id
                        )
                        logger.debug(
                            f"Scheduled periodic sync for {channel_name} "
                            f"(since entry_id {last_synced_entry_id})"
                        )

            # Sleep for a bit before checking again
            time.sleep(10)

        except Exception as e:
            logger.error(f"Error in ThingSpeak sync worker: {e}", exc_info=True)
            time.sleep(30)  # Wait longer on error


# Start the background worker threads when the app starts
worker_thread = Thread(target=process_prescription_queue, daemon=True)
worker_thread.start()

sync_worker_thread = Thread(target=process_thingspeak_sync, daemon=True)
sync_worker_thread.start()

logger.info(
    "Electronic Medication Administration Record (eMAR) application initialized"
)

if __name__ == "__main__":
    logger.info("Starting Flask development server on http://0.0.0.0:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
