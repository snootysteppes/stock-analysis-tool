import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Global reference to overlay app (will be set from main.py)
overlay_app = None

def set_overlay(app):
    """Set the overlay app reference for UI logging"""
    global overlay_app
    overlay_app = app

def log_event(message, level="INFO"):
    """
    Log an event to both console and overlay UI (if available)
    
    Args:
        message (str): The message to log
        level (str): Log level (INFO, WARNING, ERROR)
    """
    # Console logging
    if level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)
    
    # UI logging (if overlay is available)
    if overlay_app:
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}"
            # Schedule UI update in thread-safe manner
            overlay_app.root.after(0, overlay_app.append_log, log_message)
        except Exception as e:
            logger.error(f"Failed to update overlay log: {e}")

def log_error(message):
    """Convenience method for error logging"""
    log_event(message, level="ERROR")

def log_warning(message):
    """Convenience method for warning logging"""
    log_event(message, level="WARNING")
