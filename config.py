# Configuration settings for the stock analysis program

# API Keys (replace with your actual keys if using NewsAPI)
NEWS_API_KEY = ""  # Leave empty if using RSS feeds

# Screenshot and OCR settings
SCREENSHOT_WAIT = 0.5  # seconds pause after screenshot capture
OCR_MATCH_THRESHOLD = 0.7  # threshold for template matching
MIN_CHAR_WIDTH = 20  # minimum width of character in pixels
MAX_CHAR_WIDTH = 50  # maximum width of character in pixels
MIN_CHAR_HEIGHT = 30  # minimum height of character in pixels
MAX_CHAR_HEIGHT = 60  # maximum height of character in pixels

# UI Configuration
OVERLAY_WIDTH = 400
OVERLAY_HEIGHT = 300
OVERLAY_BG_COLOR = "#1e1e1e"  # Dark semi-transparent background
OVERLAY_OPACITY = 0.85  # Overall window transparency

# Font settings
LOG_FONT = ("Consolas", 10)
TICKER_FONT = ("Helvetica", 16, "bold")
RECOMMEND_FONT = ("Helvetica", 14)

# Colors
SUCCESS_COLOR = "#4CAF50"  # Green
WARNING_COLOR = "#FFC107"  # Yellow
ERROR_COLOR = "#F44336"    # Red
TEXT_COLOR = "#FFFFFF"     # White

# Background image URL (from Pexels)
BG_IMAGE_URL = "https://images.pexels.com/photos/669610/pexels-photo-669610.jpeg"

# Logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
