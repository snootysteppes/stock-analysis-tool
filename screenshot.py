import numpy as np
from PIL import ImageGrab
import cv2
from logger import log_event, log_error
import config

def capture_screen():
    """
    Capture the current screen and return it as a NumPy array in BGR format
    for OpenCV processing.
    
    Returns:
        numpy.ndarray: Screenshot image in BGR format, or None if capture fails
    """
    try:
        # Capture the entire screen
        log_event("Capturing screen...")
        screenshot = ImageGrab.grab()
        
        # Convert PIL image to numpy array
        img_np = np.array(screenshot)
        
        # Convert RGB to BGR (OpenCV format)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        
        # Add small delay if configured
        if config.SCREENSHOT_WAIT > 0:
            import time
            time.sleep(config.SCREENSHOT_WAIT)
            
        log_event("Screen captured successfully")
        return img_bgr
        
    except Exception as e:
        log_error(f"Screenshot capture failed: {str(e)}")
        return None

def get_region(img, x, y, width, height):
    """
    Extract a region from the screenshot.
    
    Args:
        img (numpy.ndarray): Source image
        x (int): X coordinate of top-left corner
        y (int): Y coordinate of top-left corner
        width (int): Width of region
        height (int): Height of region
    
    Returns:
        numpy.ndarray: Extracted region, or None if extraction fails
    """
    try:
        if img is None:
            raise ValueError("Input image is None")
            
        # Get image dimensions
        img_height, img_width = img.shape[:2]
        
        # Validate coordinates
        if x < 0 or y < 0 or x + width > img_width or y + height > img_height:
            raise ValueError("Region coordinates out of bounds")
            
        # Extract region
        region = img[y:y+height, x:x+width]
        return region
        
    except Exception as e:
        log_error(f"Region extraction failed: {str(e)}")
        return None

def preprocess_for_ocr(img):
    """
    Preprocess an image for OCR by converting to grayscale and
    applying basic image enhancement.
    
    Args:
        img (numpy.ndarray): Input image in BGR format
        
    Returns:
        numpy.ndarray: Preprocessed image, or None if processing fails
    """
    try:
        if img is None:
            raise ValueError("Input image is None")
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11,
            2
        )
        
        return thresh
        
    except Exception as e:
        log_error(f"Image preprocessing failed: {str(e)}")
        return None
