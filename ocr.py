import cv2
import numpy as np
import os
from logger import log_event, log_error
import config

# Global storage for character templates
templates = {}

def load_templates():
    """
    Load character template images from the templates directory.
    Templates should be named A.png, B.png, etc.
    
    Returns:
        dict: Dictionary mapping characters to their template images
    """
    try:
        # Create templates directory if it doesn't exist
        os.makedirs('templates', exist_ok=True)
        
        # For now, we'll create a simple template for testing
        # In production, you would load pre-trained templates from files
        template_size = (30, 40)  # width, height
        
        # Create basic templates for A-Z (placeholder implementation)
        for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
            template = np.zeros(template_size, dtype=np.uint8)
            cv2.putText(
                template,
                char,
                (5, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                255,
                2
            )
            templates[char] = template
            
        log_event(f"Loaded {len(templates)} character templates")
        return templates
        
    except Exception as e:
        log_error(f"Failed to load templates: {str(e)}")
        return {}

def preprocess_image(image):
    """
    Preprocess the image for OCR.
    
    Args:
        image (numpy.ndarray): Input image
        
    Returns:
        numpy.ndarray: Preprocessed image
    """
    try:
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
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
        
        # Edge detection
        edges = cv2.Canny(thresh, 50, 150)
        
        return edges
        
    except Exception as e:
        log_error(f"Image preprocessing failed: {str(e)}")
        return None

def segment_characters(processed_image):
    """
    Segment the image into individual characters.
    
    Args:
        processed_image (numpy.ndarray): Preprocessed image
        
    Returns:
        list: List of (x, y, w, h) coordinates for each character
    """
    try:
        # Find contours
        contours, _ = cv2.findContours(
            processed_image,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours by size
        char_contours = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if (config.MIN_CHAR_WIDTH <= w <= config.MAX_CHAR_WIDTH and
                config.MIN_CHAR_HEIGHT <= h <= config.MAX_CHAR_HEIGHT):
                char_contours.append((x, y, w, h))
        
        # Sort contours left-to-right
        char_contours.sort(key=lambda x: x[0])
        
        return char_contours
        
    except Exception as e:
        log_error(f"Character segmentation failed: {str(e)}")
        return []

def match_character(char_img, templates):
    """
    Match a character image against templates to identify it.
    
    Args:
        char_img (numpy.ndarray): Image of single character
        templates (dict): Character templates
        
    Returns:
        tuple: (character, confidence)
    """
    try:
        best_match = None
        best_val = -1
        
        # Resize character image to match template size
        char_img = cv2.resize(char_img, (30, 40))
        
        for char, template in templates.items():
            # Template matching
            result = cv2.matchTemplate(
                char_img,
                template,
                cv2.TM_CCOEFF_NORMED
            )
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            if max_val > best_val:
                best_val = max_val
                best_match = char
        
        if best_val >= config.OCR_MATCH_THRESHOLD:
            return best_match, best_val
        return None, 0
        
    except Exception as e:
        log_error(f"Character matching failed: {str(e)}")
        return None, 0

def detect_ticker(image, templates):
    """
    Detect a stock ticker in the image.
    
    Args:
        image (numpy.ndarray): Input image
        templates (dict): Character templates
        
    Returns:
        str: Detected ticker or empty string if none found
    """
    try:
        # Preprocess image
        processed = preprocess_image(image)
        if processed is None:
            return ""
            
        # Segment characters
        char_regions = segment_characters(processed)
        if not char_regions:
            return ""
            
        # Only process if we have 3-5 characters
        if not (3 <= len(char_regions) <= 5):
            return ""
            
        # Match each character
        ticker = ""
        for x, y, w, h in char_regions:
            char_img = processed[y:y+h, x:x+w]
            char, conf = match_character(char_img, templates)
            if char:
                ticker += char
            else:
                return ""  # Invalid character found
        
        log_event(f"Detected potential ticker: {ticker}")
        return ticker
        
    except Exception as e:
        log_error(f"Ticker detection failed: {str(e)}")
        return ""

# Initialize templates when module is imported
templates = load_templates()
